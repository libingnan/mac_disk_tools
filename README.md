# Mac Disk Tools

[中文](#中文说明) | [English](#english)

## 中文说明

`Mac Disk Tools` 是一个面向 macOS 的本地磁盘空间分析工具。它会扫描常见的大目录、缓存目录、开发工具目录和个人文件目录，帮助你快速判断哪些内容可以清理、哪些内容需要谨慎处理。

### 功能

- 中英双语界面切换
- 扫描常见高占用路径
- 显示磁盘总览和目录占用
- 按分类、安全等级、名称、大小筛选和排序
- 查看目录说明和删除风险等级
- 在 Finder 中打开目标目录
- 下钻查看子目录
- 将可清理内容移入废纸篓
- 对高风险路径启用删除保护
- 并发扫描常见路径，减少整体等待时间

### 界面预览

主界面：

![Main UI](./pic/page.png)

详情面板：

![Detail UI](./pic/detail.png)

### 运行要求

- macOS
- Python 3.9+

### 使用方式

```bash
python3 mac_disk_analyzer.py
```

程序启动后会在本地打开：

```text
http://127.0.0.1:18765
```

### 测试

```bash
python3 -m unittest discover -s tests
```

### 使用建议

- `Safe to delete / 可安全删除`：通常是缓存文件，删除后会自动重建。
- `Delete with caution / 谨慎删除`：可能是旧版本、归档、工具链或本地备份，确认后再删。
- `Not recommended / 不建议直接删除`：通常有更安全的卸载或应用内清理方式。
- `Manual review / 手动检查`：通常是个人文件，需要你自行判断。

### 注意事项

- 本工具不会自动执行永久删除，删除动作是“移入废纸篓”。
- 对系统目录、数据库目录、云同步目录和聊天记录目录，务必谨慎。
- 首次扫描大目录时可能需要几十秒。
- 标记为“不建议直接删除”的路径会被后端和界面同时保护，不能直接移入废纸篓。

---

## English

`Mac Disk Tools` is a local macOS disk usage analyzer. It scans common large folders, cache folders, developer tool directories, and personal file locations so you can quickly see what is safe to clean and what needs extra caution.

### Features

- Chinese / English language switch
- Scan common storage-heavy paths
- Disk overview and per-path usage display
- Filter and sort by category, safety level, name, and size
- Built-in path descriptions and safety labels
- Open target folders in Finder
- Drill down into subdirectories
- Move removable content to Trash
- Protect high-risk paths from deletion
- Scan common paths concurrently to reduce wait time

### Screenshots

Main view:

![Main UI](./pic/page.png)

Detail panel:

![Detail UI](./pic/detail.png)

### Requirements

- macOS
- Python 3.9+

### Run

```bash
python3 mac_disk_analyzer.py
```

The app starts a local web server at:

```text
http://127.0.0.1:18765
```

### Test

```bash
python3 -m unittest discover -s tests
```

### Guidance

- `Safe to delete`: Usually cache files that apps can regenerate.
- `Delete with caution`: Often archives, backups, old SDKs, or tool versions.
- `Not recommended`: Usually there is a safer uninstall or in-app cleanup path.
- `Manual review`: Usually personal files that require your own judgment.

### Notes

- The tool does not permanently delete items. It moves them to Trash.
- Be careful with system folders, database directories, cloud sync folders, and messaging data.
- Large directory scans may take tens of seconds.
- Paths marked as `Not recommended` are protected by both the API and UI and cannot be moved to Trash directly.
