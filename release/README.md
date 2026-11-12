# Release 说明

## WT_Launcher_FINAL.apk（✅ 真车验证通过 · 最终版）

| 项目 | 值 |
|---|---|
| 基线 | 车机现装 `WT_Launcher.apk`（1.8.17.23 / versionCode 10817230） |
| 大小 | 5,862,192 字节 |
| MD5 | `aed7d6bc09ccef3f2aa86268d3fca76c` |
| AndroidManifest | **与原机逐字节一致** |
| 签名 | 原厂 freescale 证书，未重签 |

### 白名单 19 条

原机 15 条 + 新增 4 条：

| # | 包名 | 名称 | 说明 |
|---|---|---|---|
| 1 | `cn.kuwo.kwmusiccar` | 酷我音乐 | 原机已有 |
| 2 | `com.ximalaya.ting.android.car` | 喜马拉雅 | 原机已有 |
| 3 | `com.tencent.qqlivepad` | 腾讯视频槽 | 原机已有 |
| 4-14 | vlink / 空调 / 高德 / 电话 / DVR / 车辆设置 / 系统设置 / 舒适氛围 / 系统升级 / 文件管理 / 一点通 | — | 原机已有 |
| 15 | `com.tencent.wecarspeech` | 语音设置 | **修正**（原为组件式，匹配不到） |
| 16 | `com.tencent.wecarnavi` | 腾讯地图 | **新增** |
| 17 | `com.wt.music` | QQ音乐 | **新增** |
| 18 | `com.tencent.wecarnews` | 腾讯车载电台 | **新增** |
| 19 | `com.shihab.diplay` | DiPlay / 75Play | **新增** |

### 图标（136×136、22px 圆角，与原厂同规格）

酷我 / 喜马拉雅 / 腾讯视频 / CarPlay / 腾讯地图 / QQ音乐 / 车载电台 —— 共 11 张 PNG 替换。

### 两个 NPE 修复

- `AppInfo` 构造：查不到内置图标时置空（加白名单黑屏的根因）
- `Utilities.getResourcesID`：空名返回 0

### 安装

```
1. 备份 /system/app/WT_Launcher.apk → /sdcard/WT_Launcher_backup.apk
2. ES(root) 把本 APK 放进 /system/app/，改名 WT_Launcher.apk 覆盖
3. 权限 644
4. 重启
```

### 版权

APK 由原厂包改制，内部厂商代码与素材版权归长安 / 梧桐车联所有。仅供学习研究，请勿商用。
