# 腾讯文档讲座报名表链接
# 留空时，可在运行 qq_form_schedule_with_state.py 时手动输入
FORM_URL = ""

# 报名时自动填写的个人信息
NAME = ""
GRADE = ""
STUDENT_ID = ""

# 目标开放时间，格式为 HH:MM:SS
TARGET_TIME = "14:00:01"

# 表单开放前后的刷新轮询间隔，单位为秒
POLL_INTERVAL = 0.1


def ensure_form_url_configured(form_url):
    if str(form_url).strip():
        return
    raise RuntimeError(
        "请先提供表单链接，可在 qq_form_config.py 中填写 FORM_URL，或在启动时手动输入。"
    )


def ensure_profile_configured():
    missing = []

    if not str(NAME).strip():
        missing.append("NAME")
    if not str(GRADE).strip():
        missing.append("GRADE")
    if not str(STUDENT_ID).strip():
        missing.append("STUDENT_ID")

    if missing:
        raise RuntimeError(
            "请先在 qq_form_config.py 中填写以下配置后再运行: "
            + ", ".join(missing)
        )
