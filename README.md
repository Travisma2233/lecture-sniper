# 长安大学讲座腾讯文档抢报名工具

这是一个基于 Python + Playwright 的腾讯文档表单自动填写脚本，主要用于长安大学学生在讲座报名开放时快速完成信息填写。

仓库默认不保留任何个人信息和登录态，你需要在本地自行填写配置并登录一次。

当前推荐流程是：

1. 先登录一次腾讯文档并保存登录态。
2. 到报名时间前启动脚本并保持浏览器打开。
3. 到点后自动刷新页面，检测到表单可填写时自动填入姓名、年级、学号。
4. 由你在浏览器里确认无误后手动点击提交。

这样做的好处是既能抢时间，又能降低误提交的风险。

## 项目特点

- 支持保存并复用腾讯文档登录态
- 支持在指定时间点持续轮询页面，等待讲座报名开放
- 自动填写 `姓名`、`年级/入学年份`、`学号`
- 浏览器全程可见，方便手动确认
- 兼容“第一次需要扫码登录”的场景

## 项目结构

- `qq_form_schedule_with_state.py`
  推荐入口。启动后可输入本次表单链接和目标时间，到点后自动轮询并填写。
- `qq_form_submit_with_state.py`
  核心逻辑。负责登录态检测、保存状态、轮询页面和自动填写。
- `qq_form_login_once.py`
  只执行一次登录，用来提前保存腾讯文档登录态。
- `qq_form_config.py`
  项目配置文件，包含表单链接、姓名、年级、学号、目标时间和轮询频率。
- `qq_form_submit.py`
  较早版本的直接提交脚本，会尝试自动点击“提交”按钮。
- `qq_form_schedule.py`
  较早版本的定时任务脚本，基于 `schedule` 包按固定时间执行。
- `qq_docs_state.json`
  本地登录态文件，包含 Cookie 和会话信息，不要分享给别人。

## 运行环境

- Windows
- Python 3.10 及以上
- 已安装 Chromium 浏览器驱动（由 Playwright 安装）

## 安装步骤

建议在项目目录中使用虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

如果你已经有自己的 Python 环境，也可以直接执行：

```powershell
pip install -r requirements.txt
playwright install chromium
```

## 配置说明

打开 `qq_form_config.py`，按自己的信息修改以下内容：

```python
FORM_URL = "腾讯文档报名表链接"
NAME = "你的姓名"
GRADE = "你的年级"
STUDENT_ID = "你的学号"
TARGET_TIME = "14:00:01"
POLL_INTERVAL = 0.1
```

参数说明：

- `FORM_URL`：讲座报名表的腾讯文档链接
- `NAME`：报名时自动填写的姓名
- `GRADE`：年级或入学年份
- `STUDENT_ID`：学号
- `TARGET_TIME`：预设开始时间，格式必须是 `HH:MM:SS`
- `POLL_INTERVAL`：轮询刷新间隔，单位是秒，越小越积极，但也更频繁

如果你不想把表单链接写死在配置文件里，也可以把 `FORM_URL` 留空，在运行 `qq_form_schedule_with_state.py` 时手动输入。

## 推荐使用方式

### 第一步：提前保存登录态

第一次使用时先运行：

```powershell
python qq_form_login_once.py
```

脚本会打开浏览器，你只需要：

1. 在浏览器里登录腾讯文档
2. 确认表单页面已经正常打开
3. 回到终端按回车

随后脚本会把登录态保存到 `qq_docs_state.json`。

### 第二步：开始抢讲座

讲座报名开始前运行：

```powershell
python qq_form_schedule_with_state.py
```

脚本会提示你输入：

- 本次表单链接
- 本次目标时间的小时、分钟、秒

如果直接回车，会使用 `qq_form_config.py` 里的默认值。

运行后流程如下：

1. 立即打开表单页面并检查登录态
2. 如果登录失效，会提示你重新登录
3. 浏览器保持打开，等待到你设定的时间
4. 到点后持续刷新页面
5. 一旦检测到表单可填写，自动填入你的信息
6. 你在浏览器确认无误后手动点击提交
7. 提交完成后，回终端按回车关闭浏览器

## 适合这个项目的使用习惯

- 报名前 5 到 10 分钟先启动脚本，避免临时登录出问题
- 把网络、电脑电源和浏览器窗口保持稳定
- 如果是新的讲座链接，可以在启动时临时输入，不一定要改配置文件
- 如果讲座表单字段名称变了，可能需要调整脚本里的匹配文字

## 其他脚本说明

### `qq_form_submit.py`

这个脚本会直接打开表单、填写信息并尝试点击提交，更接近“全自动提交”。  
但它没有当前推荐流程那么稳妥，也没有登录态恢复和到点轮询能力。

### `qq_form_schedule.py`

这是一个老版本的固定时间定时任务脚本，会每天在固定时刻触发。  
如果你主要是抢单次讲座，推荐使用 `qq_form_schedule_with_state.py`。

## 常见问题

### 1. 提示 `ModuleNotFoundError: No module named 'playwright'`

说明依赖还没安装：

```powershell
pip install -r requirements.txt
playwright install chromium
```

### 2. 浏览器打开了，但提示需要重新登录

说明保存的登录态过期了。重新运行：

```powershell
python qq_form_login_once.py
```

### 3. 自动填写失败，提示找不到足够的输入框

通常是因为：

- 表单还没开放
- 页面还没完全加载
- 讲座表单字段名称和当前脚本假设的不一致

这时可以检查页面字段名称是否还是：

- `姓名`
- `年级` 或 `入学年份`
- `学号`

### 4. 想改成别的时间怎么办

有两种方式：

- 直接修改 `qq_form_config.py` 里的 `TARGET_TIME`
- 启动 `qq_form_schedule_with_state.py` 后按提示临时输入

## 注意事项

- `qq_docs_state.json` 含有登录态，请不要发给别人
- 建议仅用于自己的讲座报名，不要替他人批量操作
- 请遵守学校和平台的使用规则
- 如果腾讯文档页面结构变化，脚本可能需要重新调整

## 一句话总结

如果你只是想稳定地抢长安大学讲座名额，直接按下面这套流程用就行：

```powershell
python qq_form_login_once.py
python qq_form_schedule_with_state.py
```

前者负责提前登录，后者负责到点自动填写。
