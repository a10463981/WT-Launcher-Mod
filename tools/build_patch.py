#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WT-Launcher-Mod 构建脚本
========================
把白名单 / 图标补丁打进原厂 WT_Launcher.apk，保留原厂签名。

流程：
  1. apktool 解包原 APK
  2. 打 smali 补丁（白名单、标签、NPE 修复、getResourcesID 保护）
  3. apktool 重建 → 取出 classes.dex
  4. 用 zip 级别重组 APK：原资源 + 原 META-INF + 新 dex + 新图标
  5. zipalign（可选 apksigner）

用法：
  python3 tools/build_patch.py --config config/example.json

依赖：python3, JDK, apktool.jar, Android build-tools(zipalign/apksigner)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

C = {
    "ok": "\033[32m✓\033[0m",
    "warn": "\033[33m!\033[0m",
    "err": "\033[31m✗\033[0m",
}


def log(msg, kind="ok"):
    print(f"{C.get(kind, '')} {msg}")


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout[-3000:])
        print(p.stderr[-3000:])
        raise SystemExit(f"命令失败: {' '.join(cmd)}")
    return p.stdout


# ----------------------------------------------------------------------------
# smali 补丁
# ----------------------------------------------------------------------------

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def _insert_before_last_return(path, block):
    """把 block 插到方法体最后一个 return-void 之前（类初始化用）。"""
    s = read(path)
    idx = s.rfind("    return-void")
    if idx < 0:
        raise SystemExit(f"{path} 里找不到 return-void")
    s = s[:idx] + block + s[idx:]
    write(path, s)
    return True


def patch_whitelist(dec, packages, replacements=None):
    """packages: [{"pkg":..., "icon": "cstr"}]"""
    replacements = replacements or []
    d = os.path.join(dec, "smali/com/autopai/applist/model/config")
    f1 = os.path.join(d, "AppsConfig$1.smali")
    f4 = os.path.join(d, "AppsConfig$4.smali")
    f5 = os.path.join(d, "AppsConfig$5.smali")
    if not f1.endswith("$1.smali"):  # 防止某些 shell 转义问题
        raise SystemExit("AppsConfig$1.smali 路径异常")
    if not os.path.exists(f1):
        raise SystemExit(f"找不到 {f1}")
    # 先做既有条目的字符串替换（如把"包名/类名"式改成纯包名）
    for rep in replacements:
        src, dst = rep.get("old"), rep.get("new")
        if not src or not dst:
            continue
        txt = read(f1)
        if src in txt:
            write(f1, txt.replace(src, dst))
            log(f"替换白名单条目: {src} -> {dst}")
        else:
            log(f"未找到待替换条目: {src}", "warn")

    # 检查是否已加过（用第一个包名判断）
    if packages and packages[0]["pkg"] in read(f1):
        log("白名单已包含目标包名，跳过", "warn")
        return
    for p in packages:
        icon = p.get("icon", "")
        blk = (
            f'\n    const-string v0, "{p["pkg"]}"\n'
            f'    const-string v1, "{icon}"\n'
            '    invoke-virtual {p0, v0, v1}, Lcom/autopai/applist/model/config/AppsConfig$1;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;\n'
        )
        _insert_before_last_return(f1, blk)
    for p in packages:
        cn = p.get("cn") or p["pkg"]
        en = p.get("en") or cn
        _insert_before_last_return(
            f4,
            f'\n    const-string v0, "{cn}"\n'
            '    invoke-virtual {p0, v0}, Lcom/autopai/applist/model/config/AppsConfig$4;->add(Ljava/lang/Object;)Z\n',
        )
        _insert_before_last_return(
            f5,
            f'\n    const-string v0, "{en}"\n'
            '    invoke-virtual {p0, v0}, Lcom/autopai/applist/model/config/AppsConfig$5;->add(Ljava/lang/Object;)Z\n',
        )
    log(f"白名单 +{len(packages)} 条")


def patch_appinfo_npe(dec):
    p = os.path.join(dec, "smali/com/autopai/applist/model/infos/AppInfo.smali")
    s = read(p)
    # 已经是安全版本？
    if 'const/4 v3, 0x0\n\n    iput-object v3, p0, Lcom/autopai/applist/model/infos/AppInfo;->iconDrawable' in s:
        log("AppInfo 已是安全版本，跳过", "warn")
        return
    # 匹配原版 else 分支（寄存器编号随版本不同，如 v3/v4 或 v2/v3）
    pat = re.compile(
        r'(    :cond_\d+\n)'
        r'    iget-object (v\d+), p0, Lcom/autopai/applist/model/infos/AppInfo;->mInfo:[^\n]*\n\n'
        r'(?:    if-nez \2, :cond_\d+\n\n)?'
        r'    const/16 (v\d+), 0xf0\n\n'
        r'    invoke-virtual \{\2, \3\}, Lcom/autopai/applist/model/compat/LauncherActivityInfoCompat;->getBadgedIcon\(I\)Landroid/graphics/drawable/Drawable;\n\n'
        r'    move-result-object \2\n\n'
        r'    iput-object \2, p0, Lcom/autopai/applist/model/infos/AppInfo;->iconDrawable:Landroid/graphics/drawable/Drawable;\n\n'
        r'    goto :goto_0\n'
    )
    def _repl(m):
        label, reg = m.group(1), m.group(2)
        return (
            label
            + '    const/4 ' + reg + ', 0x0\n\n'
            + '    iput-object ' + reg + ', p0, Lcom/autopai/applist/model/infos/AppInfo;->iconDrawable:Landroid/graphics/drawable/Drawable;\n\n'
            + '    goto :goto_0\n'
        )
    s2, n = pat.subn(_repl, s, count=1)
    if n != 1:
        raise SystemExit(
            "AppInfo 补丁匹配失败：固件版本可能不同，请手动对照 docs/04-避坑指南.md 修改"
        )
    write(p, s2)
    log("AppInfo NPE 已修复")


def patch_utilities_guard(dec):
    p = os.path.join(dec, "smali/com/autopai/common/utils/common/Utilities.smali")
    if not os.path.exists(p):
        log("找不到 Utilities.smali，跳过", "warn")
        return
    s = read(p)
    if ":cond_null_name" in s and "if-eqz p1, :cond_null_name" in s:
        # 检查方向是否正确（非 null 时走正常代码）
        if "if-eqz p1, :cond_null_name" in s and "return v0" in s:
            log("getResourcesID 保护已存在，跳过", "warn")
            return
    new_method = '''.method public static getResourcesID(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I
    .locals 2
    .param p0, "context"    # Landroid/content/Context;
    .param p1, "idname"    # Ljava/lang/String;
    .param p2, "localxy"    # Ljava/lang/String;

    .prologue
    if-eqz p1, :cond_null_name

    .line 764
    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    .line 765
    .local v0, "res":Landroid/content/res/Resources;
    invoke-virtual {p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, p1, p2, v1}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I

    move-result v1

    return v1

    :cond_null_name
    const/4 v0, 0x0

    return v0
.end method'''
    pat = re.compile(r'\.method public static getResourcesID\(.*?\n\.end method', re.S)
    s2, n = pat.subn(new_method, s, count=1)
    if n != 1:
        raise SystemExit("getResourcesID 方法匹配失败")
    write(p, s2)
    log("getResourcesID 空名字保护已加入")


def patch_boot_log(dec):
    """（可选）给 LauncherApplication 加启动日志，方便诊断。"""
    p = os.path.join(dec, "smali/com/android/launcherWT/LauncherApplication.smali")
    if not os.path.exists(p):
        return
    s = read(p)
    if "launcher_boot.txt" in s:
        log("启动日志已存在，跳过", "warn")
        return
    old = """.method public onCreate()V
    .locals 0

    .prologue
    .line 12
    invoke-super {p0}, Landroid/app/Application;->onCreate()V"""
    new = """.method public onCreate()V
    .locals 4

    .prologue
    :try_start_boot
    new-instance v0, Ljava/io/FileWriter;
    const-string v1, "/sdcard/launcher_boot.txt"
    invoke-direct {v0, v1}, Ljava/io/FileWriter;-><init>(Ljava/lang/String;)V
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J
    move-result-wide v1
    invoke-static {v1, v2}, Ljava/lang/String;->valueOf(J)Ljava/lang/String;
    move-result-object v1
    invoke-virtual {v0, v1}, Ljava/io/FileWriter;->write(Ljava/lang/String;)V
    invoke-virtual {v0}, Ljava/io/FileWriter;->close()V
    :try_end_boot
    .catch Ljava/lang/Throwable; {:try_start_boot .. :try_end_boot} :catch_boot
    goto :goto_boot
    :catch_boot
    move-exception v0
    :goto_boot
    .line 12
    invoke-super {p0}, Landroid/app/Application;->onCreate()V"""
    if old not in s:
        log("LauncherApplication 结构不同，跳过启动日志", "warn")
        return
    write(p, s.replace(old, new, 1))
    log("启动日志补丁已加入")


# ----------------------------------------------------------------------------
# 打包
# ----------------------------------------------------------------------------

def build_dex(dec, apktool, frame, workdir):
    out = os.path.join(workdir, "built.apk")
    cmd = ["java", "-jar", apktool, "b", dec, "-o", out]
    if frame:
        cmd += ["--frame-path", frame]
    run(cmd)
    with zipfile.ZipFile(out) as z:
        dex = z.read("classes.dex")
    log(f"dex 重建完成（{len(dex)} 字节）")
    return dex


def compose(base_apk, out_apk, dex, icon_repl):
    count = 0
    with zipfile.ZipFile(out_apk, "w", zipfile.ZIP_DEFLATED) as zo, zipfile.ZipFile(base_apk) as z:
        for it in z.infolist():
            if it.filename == "classes.dex":
                data = dex
            elif it.filename in icon_repl:
                with open(icon_repl[it.filename], "rb") as f:
                    data = f.read()
                it2 = zipfile.ZipInfo(it.filename, it.date_time)
                it2.compress_type = zipfile.ZIP_STORED
                it2.external_attr = it.external_attr
                zo.writestr(it2, data)
                count += 1
                continue
            else:
                data = z.read(it.filename)
            zo.writestr(it, data)
    log(f"APK 重组完成（替换 dex + {count} 张图标）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    cfg = json.load(open(args.config, encoding="utf-8"))

    base = cfg["base_apk"]
    if not os.path.exists(base):
        raise SystemExit(f"原 APK 不存在: {base}")

    apktool = cfg.get("apktool", "apktool.jar")
    frame = cfg.get("frame_path")
    out = cfg.get("out", "out/WT_Launcher_patch.apk")
    workdir = cfg.get("workdir", "build")
    os.makedirs(workdir, exist_ok=True)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    dec = os.path.join(workdir, "dec")
    if os.path.exists(dec):
        shutil.rmtree(dec)

    # 1. 解包
    cmd = ["java", "-jar", apktool, "d", "-f", "-o", dec, base]
    if frame:
        cmd += ["--frame-path", frame]
    run(cmd)
    log("解包完成")

    # 2. 打补丁
    if cfg.get("boot_log", True):
        patch_boot_log(dec)
    patch_whitelist(dec, cfg.get("add_packages", []), cfg.get("replace_entries", []))
    patch_appinfo_npe(dec)
    patch_utilities_guard(dec)

    # 3. 重建 dex
    dex = build_dex(dec, apktool, frame, workdir)

    # 4. 图标替换表（target 必须存在于原 APK）
    icon_repl = {}
    with zipfile.ZipFile(base) as z:
        names = set(z.namelist())
    for item in cfg.get("icons", []):
        tgt = item["target"]
        if tgt not in names:
            log(f"原 APK 里没有 {tgt}，跳过", "warn")
            continue
        icon_repl[tgt] = item["source"]

    # 5. 重组 + 对齐
    compose(base, out, dex, icon_repl)
    zipalign = cfg.get("zipalign")
    if zipalign:
        aligned = out + ".aligned"
        run([zipalign, "-f", "4", out, aligned])
        os.replace(aligned, out)
        log("zipalign 完成")

    # 6. 可选签名
    sign = cfg.get("sign")
    if sign and sign.get("keystore"):
        apksigner = cfg.get("apksigner")
        signed = os.path.splitext(out)[0] + "_signed.apk"
        cmd = [
            apksigner, "sign",
            "--ks", sign["keystore"],
            "--ks-pass", f"pass:{sign.get('store_pass','')}",
            "--key-pass", f"pass:{sign.get('key_pass','')}",
            "--min-sdk-version", str(sign.get("min_sdk", 19)),
            "--v1-signing-enabled", "true",
            "--v2-signing-enabled", "false",
            "--out", signed, out,
        ]
        run(cmd)
        log(f"签名完成: {signed}")

    log(f"完成: {out}")
    print()
    print("接下来：")
    print("  1. 反编译检查三条列表长度（见 docs/02）")
    print("  2. 模拟器验证（见 docs/05）")
    print("  3. 上车前先备份 /system/app/WT_Launcher.apk")


if __name__ == "__main__":
    main()
