from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from qq_form_config import (
    FORM_URL,
    NAME,
    GRADE,
    STUDENT_ID,
    ensure_form_url_configured,
    ensure_profile_configured,
)


def fill_by_label(page, label_text, value):
    candidates = [
        page.locator(f'text="{label_text}"').locator("xpath=ancestor::*[self::div or self::label][1]").locator("input").first,
        page.locator(f'text="{label_text}"').locator("xpath=ancestor::*[self::div or self::label][1]").locator("textarea").first,
        page.locator(f'input[placeholder*="{label_text}"]').first,
        page.locator(f'text="{label_text}"').locator("xpath=following::input[1]").first,
        page.locator(f'text="{label_text}"').locator("xpath=following::textarea[1]").first,
    ]

    for locator in candidates:
        try:
            if locator.count() > 0 and locator.is_visible():
                locator.fill(value)
                return True
        except Exception:
            pass
    return False


def fill_by_position_fallback(page):
    fields = page.locator("textarea, input").all()
    visible_fields = []
    for item in fields:
        try:
            if item.is_visible() and item.is_enabled():
                visible_fields.append(item)
        except Exception:
            pass

    if len(visible_fields) < 3:
        raise RuntimeError("没找到足够的可填写输入框。")

    visible_fields[0].fill(NAME)
    visible_fields[1].fill(GRADE)
    visible_fields[2].fill(STUDENT_ID)


def click_submit(page):
    submit_buttons = [
        page.get_by_role("button", name="提交"),
        page.locator('button:has-text("提交")').first,
        page.locator('text="提交"').first,
    ]

    for button in submit_buttons:
        try:
            if button.count() > 0 and button.is_visible():
                button.click()
                return
        except Exception:
            pass

    raise RuntimeError("没找到提交按钮。")


def submit_form():
    ensure_form_url_configured(FORM_URL)
    ensure_profile_configured()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(locale="zh-CN")
        page = context.new_page()

        try:
            page.goto(FORM_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)

            matched = 0
            matched += int(fill_by_label(page, "姓名", NAME))
            matched += int(fill_by_label(page, "年级", GRADE) or fill_by_label(page, "入学年份", GRADE))
            matched += int(fill_by_label(page, "学号", STUDENT_ID))

            if matched < 3:
                fill_by_position_fallback(page)

            page.wait_for_timeout(1000)
            click_submit(page)
            page.wait_for_timeout(3000)
            print("提交成功")
        except PlaywrightTimeoutError:
            print("页面加载超时")
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    submit_form()
