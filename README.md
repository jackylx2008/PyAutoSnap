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
- `flows.auto_snap.region`：可选区域截图，留空表示全屏

区域截图示例：

```yaml
flows:
  auto_snap:
    region:
      left: 0
      top: 0
      width: 1280
      height: 720
```

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

`COMMON_PROJECT_SKILLS.md` 是本地项目规则文件，不提交到仓库。运行产物、日志、本机环境文件和虚拟环境也已通过 `.gitignore` 排除。
