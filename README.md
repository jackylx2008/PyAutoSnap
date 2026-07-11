# PyAutoSnap

PyAutoSnap 是一个按固定时间间隔自动截屏的小工具。项目采用 `src` 布局，根目录入口脚本负责启动，包内 `modules` 提供基础能力，`flows` 负责编排定时截屏流程。

## 环境准备

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 配置

默认读取根目录 `config.yaml`。本机差异可以写入不入库的 `common.env`，格式参考 `common.env.example`。

主要配置项：

- `app.log_level`：日志级别，默认 `INFO`
- `app.output_dir`：截图输出目录，默认 `output/screenshots`
- `flows.auto_snap.interval_seconds`：截图间隔秒数
- `flows.auto_snap.capture_count`：截图次数，`0` 表示持续运行直到手动停止
- `flows.auto_snap.image_format`：图片格式，支持 `png`、`jpg`、`jpeg`
- `flows.auto_snap.filename_template`：文件名模板，可使用 `{timestamp}`、`{sequence}`、`{extension}`
- `flows.auto_snap.region`：可选区域截图，留空表示全屏；可写全局坐标，也可写 `screen_index` 加屏幕内坐标

先列出当前 Windows 显示器坐标：

```powershell
.\.venv\Scripts\python.exe list_screens.py
```

该命令还会截取一张包含全部屏幕的参考图，默认保存到项目根目录 `test/`：

```text
fullscreen_screenshot=D:\...\PyAutoSnap\test\fullscreen_20260711_170000_0001.png
```

如果只想列出屏幕信息，不保存参考截图：

```powershell
.\.venv\Scripts\python.exe list_screens.py --no-screenshot
```

输出示例：

```text
index=1 device=\\.\DISPLAY1 primary=yes left=0 top=0 width=2560 height=1440 right=2560 bottom=1440
index=2 device=\\.\DISPLAY2 primary=no left=-1920 top=0 width=1920 height=1080 right=0 bottom=1080
index=3 device=\\.\DISPLAY3 primary=no left=2560 top=0 width=1920 height=1080 right=4480 bottom=1080
```

固定屏幕内区域截图示例：

```yaml
flows:
  auto_snap:
    region:
      screen_index: 3
      left: 100
      top: 200
      width: 800
      height: 600
```

这表示截取 `list_screens.py` 输出中 `index=3` 的屏幕，从该屏幕左上角往右 `100`、往下 `200` 开始的 `800x600` 区域。

## 运行

```powershell
.\.venv\Scripts\python.exe autosnap.py
```

使用其他配置文件：

```powershell
.\.venv\Scripts\python.exe autosnap.py --config-file config.yaml
```

运行后截图默认写入 `output/screenshots/`，日志写入 `log/autosnap.log`。当 `capture_count` 为 `0` 时程序会持续运行，按 `Ctrl+C` 停止。

## Git 同步注意

`COMMON_PROJECT_SKILLS.md` 是本地项目规则文件，不提交到仓库。运行产物、日志、本机环境文件、虚拟环境和 `test/` 参考截图也已通过 `.gitignore` 排除。
