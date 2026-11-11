# Release 说明

## WT_Launcher_C2_verified.apk（✅ 真车验证通过）

| 项目 | 值 |
|---|---|
| 基线 | 车机现装 `WT_Launcher.apk`（1.8.17.23 / versionCode 10817230） |
| 大小 | 5,846,005 字节 |
| MD5 | `37cb5f0822890310ee8a3c8c40dfa93a` |
| AndroidManifest | **与原机逐字节一致** |
| 签名 | 原厂 freescale 证书，未重签 |

### 白名单 16 条（原机 15 条 + DiPlay）

原机 15 条原样保留，只做了两处改动：

1. 第 15 条 `com.tencent.wecarspeech/com.tencent.wecarspeech.app.MoreActivity`
   → 改为纯包名 `com.tencent.wecarspeech`
   （主列表只比对包名，组件式写法永远匹配不到 —— 这是原机的 bug）
2. 新增第 16 条 `com.shihab.diplay`（CarPlay / 75Play）

### 其它改动

- 图标替换 7 张：酷我 / 喜马拉雅 / 腾讯视频 / CarPlay
- 修复 `AppInfo` NPE（加白名单黑屏的根因）
- 修复 `getResourcesID` 空名 NPE
- 启动日志 `/sdcard/launcher_boot.txt`

### 安装

```
1. 备份 /system/app/WT_Launcher.apk → /sdcard/
2. ES(root) 把本 APK 放进 /system/app/，改名 WT_Launcher.apk 覆盖
3. 权限 644
4. 重启
```

### 版权

APK 由原厂包改制，内部厂商代码与素材版权归长安 / 梧桐车联所有。仅供学习研究，请勿商用。
