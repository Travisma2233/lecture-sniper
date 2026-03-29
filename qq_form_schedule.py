import time
import schedule
from qq_form_submit import submit_form


def job():
    try:
        print("开始执行自动填表...")
        submit_form()
    except Exception as exc:
        print(f"执行失败: {exc}")


schedule.every().day.at("14:00").do(job)

print("定时任务已启动，每天 14:00 自动执行。")
while True:
    schedule.run_pending()
    time.sleep(1)
