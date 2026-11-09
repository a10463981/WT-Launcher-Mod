#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""车机刷机包解包工具：zip / sparse ext4 / raw ext4 / payload.bin
用法:
  python3 rom_extract.py info   <包>                 # 看类型/内部条目
  python3 rom_extract.py ls     <镜像> <路径>         # 列目录，如 /system/framework
  python3 rom_extract.py dump   <镜像> <路径> <输出>  # 取单个文件
  python3 rom_extract.py all    <镜像> <镜像内目录> <输出目录>   # 整目录导出
不需要 root、不需要 mount（用 debugfs 直接读 ext4）
"""
import os, struct, subprocess, sys, zipfile

SPARSE_MAGIC = 0xED26FF3A

def file_type(p):
    with open(p, 'rb') as f:
        head = f.read(4096)
    if head[:4] == b'PK\x03\x04':
        return 'zip'
    if len(head) >= 4 and struct.unpack_from('<I', head, 0)[0] == SPARSE_MAGIC:
        return 'sparse'
    if len(head) >= 1084 and head[1080:1082] == b'\x53\xef':
        return 'ext4'
    if head[:8] == b'CrAU\x00\x00\x00':
        return 'payload'
    if head[0:2] == b'\x1f\x8b':
        return 'gzip'
    return 'unknown'

def sparse2raw(src, dst):
    with open(src, 'rb') as f, open(dst, 'wb') as o:
        magic, major, minor, fhdr, chdr = struct.unpack('<IHHHH', f.read(12))
        assert magic == SPARSE_MAGIC, "不是 sparse 镜像"
        blk_sz, total_blks, total_chunks, csum_sz = struct.unpack('<IIII', f.read(16))
        out_off = 0
        for i in range(total_chunks):
            ctype, reserved, csize, tsize = struct.unpack('<HHII', f.read(12))
            if ctype == 0xCAC1:      # raw
                o.write(f.read(csize * blk_sz))
            elif ctype == 0xCAC2:    # fill
                v = f.read(4)
                o.write(v * (csize * blk_sz // 4))
            elif ctype == 0xCAC3:    # don't care
                o.write(b'\x00' * (csize * blk_sz))
            elif ctype == 0xCAC4:    # crc32
                f.read(csize)
            else:
                raise SystemExit("未知 chunk 类型 %#x" % ctype)
            if csum_sz:
                f.read(csum_sz)
        o.truncate(total_blks * blk_sz)
    return dst

def as_raw(img):
    """如果是 sparse 就先转成 raw，返回 raw 路径"""
    if file_type(img) == 'sparse':
        raw = img + '.raw'
        if not os.path.exists(raw) or os.path.getsize(raw) == 0:
            print("转换 sparse -> raw ...")
            sparse2raw(img, raw)
        return raw
    return img

def debugfs(img, cmd):
    p = subprocess.run(['debugfs', '-R', cmd, img], capture_output=True, text=False)
    return p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')

def main():
    if len(sys.argv) < 3:
        print(__doc__); return
    mode, target = sys.argv[1], sys.argv[2]
    t = file_type(target)
    print("类型:", t)
    if mode == 'info':
        if t == 'zip':
            with zipfile.ZipFile(target) as z:
                for i in z.infolist():
                    print(f"{i.file_size:>12d}  {i.filename}")
        elif t in ('ext4', 'sparse'):
            raw = as_raw(target)
            print(debugfs(raw, 'ls -l /'))
        else:
            print("暂不支持的格式:", t)
        return
    if mode in ('ls', 'dump', 'all'):
        path = sys.argv[3] if len(sys.argv) > 3 else '/'
        if not path.startswith('/'):
            path = '/' + path
        raw = as_raw(target)
        if mode == 'ls':
            print(debugfs(raw, f'ls -l "{path}"'))
        elif mode == 'dump':
            out = sys.argv[4]
            r = debugfs(raw, f'dump "{path}" "{out}"')
            print(r); print("输出:", out, os.path.getsize(out) if os.path.exists(out) else "失败")
        else:
            outdir = sys.argv[4]
            os.makedirs(outdir, exist_ok=True)
            # 递归导出：用 rdump
            r = debugfs(raw, f'rdump "{path}" "{outdir}"')
            print(r); print("导出到:", outdir)
        return
    print(__doc__)

if __name__ == '__main__':
    main()
