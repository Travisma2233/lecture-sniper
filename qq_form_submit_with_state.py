from pathlib import Path
from datetime import datetime
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from qq_form_config import (
    FORM_URL,
    NAME,
    GRADE,
    STUDENT_ID,
    ensure_form_url_configured,
    ensure_profile_configured,
)

STATE_PATH = Path(__file__).with_name("qq_docs_state.json")
SCREENSHOT_DIR = Path(__file__).with_name("screenshots")
PAGE_LOAD_TIMEOUT = 60000
LOGIN_SETTLE_MS = 3000
RELOAD_SETTLE_MS = 200


def wait_for_form_page(page, form_url=FORM_URL):
    ensure_form_url_configured(form_url)
    page.goto(form_url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
    page.wait_for_timeout(LOGIN_SETTLE_MS)


def fill_by_label(page, label_text, value):
    candidates = [
        page.locator(f'text="{label_text}"').locator("xpath=ancestor::*[self::div or self::label][1]").locator("textarea, input").first,
        page.locator(f'text="{label_text}"').locator("xpath=following::textarea[1]").first,
        page.locator(f'text="{label_text}"').locator("xpath=following::input[1]").first,
        page.locator(f'text="{label_text}"').locator("xpath=ancestor::*[1]/following::textarea[1]").first,
    ]

    for locator in candidates:
        try:
            if locator.count() > 0 and locator.is_visible() and locator.is_editable():
                locator.fill(value)
                return True
        except Exception:
            pass
    return False


def get_fillable_fields(page):
    fillable = []
    for field in page.locator("textarea, input").all():
        try:
            if field.is_visible() and field.is_editable():
                fillable.append(field)
        except Exception:
            pass
    return fillable


def is_login_required(page):
    markers = [
        "登录腾讯文档",
        "登录后填写",
        "扫码登录",
        "微信登录",
        "QQ登录",
    ]
    try:
        body_text = page.locator("body").inner_text()
    except Exception:
        return False
    return any(marker in body_text for marker in markers)


def ensure_logged_in(page):
    if is_login_required(page):
        raise RuntimeError("当前登录态已失效，请先完成登录并保存新的登录态。")


def save_storage_state(context):
    context.storage_state(path=str(STATE_PATH))
    print(f"登录态已保存到: {STATE_PATH}")


def prompt_user_to_log_in(page, context):
    print("需要登录，请在打开的浏览器里完成腾讯文档登录。")
    print("登录完成并确认表单页面已正常打开后，回到终端按回车继续。")

    while True:
        input()
        page.wait_for_timeout(1000)
        page.reload(wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
        page.wait_for_timeout(LOGIN_SETTLE_MS)
        if not is_login_required(page):
            save_storage_state(context)
            return
        print("尚未检测到登录完成，请先在浏览器里完成登录后再按回车。")


def prepare_logged_in_page(page, context, form_url=FORM_URL):
    print("检测登录态...")
    wait_for_form_page(page, form_url=form_url)

    if is_login_required(page):
        prompt_user_to_log_in(page, context)
        wait_for_form_page(page, form_url=form_url)

    ensure_logged_in(page)
    print("登录态可用。")


def open_context_with_state(browser):
    if STATE_PATH.exists():
        return browser.new_context(locale="zh-CN", storage_state=str(STATE_PATH))
    return browser.new_context(locale="zh-CN")


def fill_by_position_fallback(page):
    fillable = get_fillable_fields(page)
    if len(fillable) < 3:
        raise RuntimeError("登录后仍未找到足够的可填写输入框。")

    fillable[0].fill(NAME)
    fillable[1].fill(GRADE)
    fillable[2].fill(STUDENT_ID)


def click_submit(page):
    buttons = [
        page.get_by_role("button", name="提交"),
        page.locator('button:has-text("提交")').first,
        page.locator('text="提交"').first,
    ]

    for button in buttons:
        try:
            if button.count() > 0 and button.is_visible() and button.is_enabled():
                button.click()
                return
        except Exception:
            pass

    raise RuntimeError("没找到可点击的提交按钮。")


def save_success_screenshot(page):
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = SCREENSHOT_DIR / f"submit_success_{timestamp}.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    print(f"截图已保存: {screenshot_path}")


def fill_and_submit(page):
    ensure_profile_configured()

    matched = 0
    matched += int(fill_by_label(page, "姓名", NAME))
    matched += int(fill_by_label(page, "年级", GRADE) or fill_by_label(page, "入学年份", GRADE))
    matched += int(fill_by_label(page, "学号", STUDENT_ID))

    if matched < 3:
        fill_by_position_fallback(page)

    page.wait_for_timeout(RELOAD_SETTLE_MS)
    print("填写完成，未自动提交。")


def wait_until_target_second(hour=14, minute=0, second=1):
    while True:
        now = datetime.now()
        if now.hour == hour and now.minute == minute and now.second >= second:
            return
        time.sleep(0.05)


def run_with_browser(callback, use_storage_state=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = open_context_with_state(browser) if use_storage_state else browser.new_context(locale="zh-CN")
        page = context.new_page()

        try:
            return callback(context, page)
        except PlaywrightTimeoutError:
            print("页面加载超时")
            raise
        finally:
            browser.close()


def run_manual_login(form_url=FORM_URL):
    def callback(context, page):
        wait_for_form_page(page, form_url=form_url)
        prompt_user_to_log_in(page, context)

    run_with_browser(callback, use_storage_state=False)


def submit_form(form_url=FORM_URL):
    def callback(context, page):
        prepare_logged_in_page(page, context, form_url=form_url)
        fill_and_submit(page)

    run_with_browser(callback)


def run_scheduled_submission(target_hour=14, target_minute=0, target_second=1, poll_interval=0.1, form_url=FORM_URL):
    def callback(context, page):
        prepare_logged_in_page(page, context, form_url=form_url)
        print("登录态已准备完成，浏览器将保持打开，等待到配置时间执行。")
        wait_until_target_second(target_hour, target_minute, target_second)

        while True:
            page.reload(wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
            page.wait_for_timeout(RELOAD_SETTLE_MS)
            ensure_logged_in(page)

            if len(get_fillable_fields(page)) >= 3:
                fill_and_submit(page)
                print("请在浏览器中检查填写结果并手动提交，完成后回到终端按回车关闭浏览器。")
                input()
                return

            time.sleep(poll_interval)

    run_with_browser(callback)


def submit_form_when_unlocked(target_hour=14, target_minute=0, target_second=1, poll_interval=0.1, form_url=FORM_URL):
    run_scheduled_submission(
        target_hour=target_hour,
        target_minute=target_minute,
        target_second=target_second,
        poll_interval=poll_interval,
        form_url=form_url,
    )


if __name__ == "__main__":
    submit_form()
