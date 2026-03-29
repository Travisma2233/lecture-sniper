from qq_form_config import FORM_URL, TARGET_TIME, POLL_INTERVAL, ensure_form_url_configured
from qq_form_submit_with_state import run_scheduled_submission


DEFAULT_HOUR, DEFAULT_MINUTE, DEFAULT_SECOND = map(int, TARGET_TIME.split(":"))


def prompt_with_default(label, default_value):
    value = input(f"{label}（直接回车使用默认值 {default_value}）\n> ").strip()
    return value or str(default_value)


def prompt_target_time_parts():
    hour = int(prompt_with_default("请输入小时", DEFAULT_HOUR))
    minute = int(prompt_with_default("请输入分钟", DEFAULT_MINUTE))
    second = int(prompt_with_default("请输入秒", DEFAULT_SECOND))
    return hour, minute, second


def main():
    try:
        form_url = prompt_with_default("请输入表单链接", FORM_URL)
        ensure_form_url_configured(form_url)
        target_hour, target_minute, target_second = prompt_target_time_parts()
        target_time = f"{target_hour:02d}:{target_minute:02d}:{target_second:02d}"

        print("程序启动后立即打开页面并检查登录态。")
        print(f"本次链接: {form_url}")
        print(f"本次时间: {target_time}")
        print("浏览器会保持打开，直到填写完成。")

        run_scheduled_submission(
            target_hour=target_hour,
            target_minute=target_minute,
            target_second=target_second,
            poll_interval=POLL_INTERVAL,
            form_url=form_url,
        )
    except Exception as exc:
        print(f"执行失败: {exc}")


if __name__ == "__main__":
    main()
