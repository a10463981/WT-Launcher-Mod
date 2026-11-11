# Release 说明

## WT_Launcher_C_carbase.apk（✅ 真车验证通过）

| 项目 | 值 |
|---|---|
| 基线 | 车机现装 `WT_Launcher.apk`（1.8.17.23 / versionCode 10817230） |
| 大小 | 5,846,013 字节 |
| MD5 | `0859aa2bdd12d3eebb63874b1a936843` |
| AndroidManifest | **与原机逐字节一致**（未改 versionCode） |
| 签名 | 原厂 freescale 证书，未重签 |

### 改动

1. 白名单 +1：`com.shihab.diplay`（CarPlay / 75Play）
2. 图标替换 7 张（酷我 / 喜马拉雅 / 腾讯视频 / CarPlay）
3. 修复 `AppInfo` NPE（黑屏根因）
4. 修复 `getResourcesID` 空名 NPE
5. 启动日志写 `/sdcard/launcher_boot.txt`

> 车机 1.8.17.23 的白名单里本来就有酷我 / 喜马拉雅 / ES / 语音设置 / 腾讯视频，
> 因此本版只补 DiPlay 并修正图标。

### 安装

```
1. 备份 /system/app/WT_Launcher.apk → /sdcard/
2. ES(root) 把本 APK 放进 /system/app/，改名 WT_Launcher.apk 覆盖
3. 权限 644
4. 重启
```

### 版权

APK 由原厂包改制，内部厂商代码与素材版权归长安 / 梧桐车联所有。仅供学习研究，请勿商用。
