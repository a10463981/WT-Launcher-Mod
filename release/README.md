# Release 说明

本目录的 APK 是**成品补丁包**，已保留原厂签名（只替换了 `classes.dex` 和图标 PNG）。

## 文件

| 文件 | 说明 |
|---|---|
| `WT_Launcher_patch8.apk` | 基础版：白名单 +3（CarPlay / QQ音乐 / 腾讯地图）+ 6 个品牌图标 |

## 校验

```
md5: 88a83fb6184788ef7ce55abb7acee7c4
size: 5,860,545 字节
```

## 安装

见根目录 [README](../README.md) 的「上车安装」章节。**务必先备份** `/system/app/WT_Launcher.apk`。

## 版权提示

该 APK 由原厂 `WT_Launcher.apk` 改制而成，内部的厂商代码、图片资源版权归长安汽车 / 梧桐车联所有。
本仓库仅提供**技术研究与学习**用途，请勿用于商业分发。
如你希望完全规避版权问题，请不要下载本 APK，改用 `tools/build_patch.py` 在你自己的车机 APK 上生成。
