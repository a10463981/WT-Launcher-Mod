# WT-Launcher-Mod

> 长安 CS75 PLUS（梧桐车机 S311 / Android 4.4.2）原厂桌面 `com.android.launcherWT` 的白名单与图标定制方案
>
> **不需要 root 权限改代码、不需要重编译资源表**，只替换 `classes.dex` 和 PNG，保留原厂签名。

[![Android](https://img.shields.io/badge/Android-4.4.2-3ddc84)](https://www.android.com)
[![Device](https://img.shields.io/badge/Device-CS75%20PLUS%202020-2b6cb0)]()

---

## 这是什么

长安 CS75 PLUS 2020 款（梧桐车机 S311，Android 4.4.2）的桌面是 `com.android.launcherWT`，
**桌面图标 = 代码里硬编码的白名单**，没有配置文件、没有数据库，所以在车机上装了新 App 也不会显示。

本项目提供一套**可复现的定制流程**：

1. 往白名单里**增加任意包名**（CarPlay、音乐、导航、自己写的 App……）
2. 给新增项**配图标**（用应用自己的图标，或用桌面内置的 136×136 图标槽）
3. 替换原厂错的图标槽位（比如"酷我音乐槽"被原厂配成了地图图标）
4. 打包成**保留原厂签名**的 APK，直接替换 `/system/app/WT_Launcher.apk`

> ⚠️ 已适配版本：`1.8.17.23.release` / versionCode `10817230`
> 其它版本的偏移不同，请先反编译确认（见 [docs/01-逆向分析.md](docs/01-逆向分析.md)）

---

## 快速开始

### 1. 下载

到 [Releases](../../releases) 下载 `WT_Launcher_patchN.apk`。

### 2. 上车安装

| 步骤 | 操作 |
|---|---|
| 1 | ES 文件浏览器（root）进入 `/system/app/` |
| 2 | 长按 `WT_Launcher.apk` → 复制到 `/sdcard/WT_Launcher_backup.apk`（**先备份**） |
| 3 | 把下载的 APK 复制进 `/system/app/`，改名成 `WT_Launcher.apk` 覆盖 |
| 4 | 权限设为 `rw-r--r--`（644） |
| 5 | 重启车机 |

### 3. 回滚

```bash
# 车机开了 ADB 的话
adb shell su -c "cp /sdcard/WT_Launcher_backup.apk /system/app/WT_Launcher.apk"
adb reboot
```

或者 ES 里把备份文件再覆盖回去。

---

## 自己构建

### 依赖

- JDK 8+（本项目用 17 验证）
- [apktool](https://github.com/iBotPeaches/Apktool) ≥ 2.9
- Android SDK build-tools（`zipalign`、`apksigner`、`aapt2`）
- ImageMagick（做图标用）

### 配置

编辑 `config/example.json`：

```json
{
  "base_apk": "WT_Launcher.apk",
  "add_packages": [
    { "pkg": "com.shihab.diplay",        "cn": "CarPlay",  "en": "CarPlay",     "icon": "classic_icon_applet" },
    { "pkg": "com.wt.music",             "cn": "QQ音乐",   "en": "QQ Music",    "icon": "classic_icon_music" },
    { "pkg": "com.tencent.wecarnavi",    "cn": "腾讯地图",  "en": "Tencent Map", "icon": "classic_icon_user_center" }
  ],
  "icons": [
    { "target": "res/drawable/classic_icon_applet.png", "source": "icons/carplay.png" },
    { "target": "res/drawable-land-hdpi-v4/classic_icon_applet.png", "source": "icons/carplay.png" }
  ]
}
```

### 构建

```bash
python3 tools/build_patch.py --config config/example.json --out release/WT_Launcher_patch.apk
```

输出 APK **保留原厂 META-INF**（大图标版同款做法），只有 `classes.dex` 和列出的 PNG 被替换。

---

## 文档

| 文档 | 内容 |
|---|---|
| [docs/01-逆向分析.md](docs/01-逆向分析.md) | 桌面完整链路：启动、过滤、图标、主题、持久化 |
| [docs/02-添加白名单.md](docs/02-添加白名单.md) | 三张并行列表的约束、怎么加/删 |
| [docs/03-图标定制.md](docs/03-图标定制.md) | 图标查找逻辑、136×136 规格、圆角、替换 PNG |
| [docs/04-避坑指南.md](docs/04-避坑指南.md) | 黑屏的 4 个真实原因（含两个 NPE） |
| [docs/05-模拟器验证.md](docs/05-模拟器验证.md) | PVE + Android-x86 4.4 搭建与 8:3 分辨率 |

---

## 已验证的改动清单（v1.8.17.23）

| # | 位置 | 改动 |
|---|---|---|
| 1 | `apps/AppsConfig$1.smali` | 白名单 map 追加包名 + 图标资源名 |
| 2 | `apps/AppsConfig$4.smali` | 追加中文标签（必须与 map 同序等长） |
| 3 | `apps/AppsConfig$5.smali` | 追加英文标签（同上） |
| 4 | `model/infos/AppInfo.smali` | 图标查不到时置空，**不调用 `mInfo`**（修 NPE） |
| 5 | `common/utils/Utilities.smali` | `getResourcesID` 空名字保护（修第二个 NPE） |
| 6 | `res/drawable*/classic_icon_*.png` | 替换图标内容（文件名不变） |

---

## 免责声明

- 本项目**仅供个人学习研究**，不得用于商业用途。
- 修改系统桌面**存在变砖风险**，请务必先备份 `/system/app/WT_Launcher.apk` 并能恢复。
- 分发修改后的 APK 涉及**厂商版权**：本仓库的**脚本和文档**是原创的，但 `WT_Launcher.apk` 及其图标资源归长安/梧桐车联所有。
  如担心版权，建议只发布 `tools/` 与 `docs/`，APK 由使用者自行用脚本生成。
- 不同车机固件版本可能存在差异，**未验证的版本请勿直接刷入**。

## License

脚本与文档：MIT
APK 内的厂商代码与素材：版权归原厂所有，本项目不主张任何权利。
