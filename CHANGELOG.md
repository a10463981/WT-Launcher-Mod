# Changelog

## v1.0.0 · 2026-11-09

首个公开版本，基于 `WT_Launcher` 1.8.17.23.release（versionCode 10817230）。

### 新增
- 白名单追加 3 个应用：`com.shihab.diplay`（CarPlay）、`com.wt.music`（QQ音乐）、`com.tencent.wecarnavi`（腾讯地图）
- 6 个品牌图标（136×136、22px 圆角）：CarPlay / QQ音乐 / 酷我 / 喜马拉雅 / 腾讯视频 / 腾讯地图
- 修正原厂错配的 3 个图标槽位（酷我槽显示地图、喜马拉雅槽显示音符、腾讯视频槽显示电台）

### 修复
- `AppInfo` 4 参构造在 `mInfo == null` 时 NPE（新增白名单应用的**黑屏主因**）
- `Utilities.getResourcesID` 在图标名为 null 时 NPE（主题非 classic 时触发）
- 修正 `getResourcesID` 空判断写反导致"所有内置图标失效"的问题

### 工程
- 提供 `tools/build_patch.py` 一键构建（解包 → 打补丁 → 重组 → 对齐）
- 提供 `tools/make_rounded_icons.sh` 图标圆角生成
- 提供 `tools/rom_extract.py` 刷机包解包（ext4/sparse/zip）
- 完整逆向文档 5 篇 + 模拟器验证流程

### 已验证环境
- 长安 CS75 PLUS 2020（梧桐车机 S311，Android 4.4.2）
- PVE + Android-x86 4.4.4 模拟器（1280×480 / 240dpi，等效车机 1920×720）
