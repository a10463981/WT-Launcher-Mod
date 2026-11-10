#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修改 APK 里 AndroidManifest.xml 的 versionCode（二进制 AXML 原地改整数）

用法: python3 tools/bump_version.py in.apk out.apk 10817241
说明: 只改 4 字节整数，manifest 长度和字符串池不变，签名仍按原样保留。
"""
import struct, sys, zipfile

def u16(b,o): return struct.unpack_from('<H', b, o)[0]
def u32(b,o): return struct.unpack_from('<I', b, o)[0]

def patch(m, newv):
    assert u16(m,0)==0x0003, "不是 AXML"
    off=8
    assert u16(m,off)==0x0001, "期望字符串池"
    sp_size=u32(m,off+4)
    str_count=u32(m,off+8); flags=u32(m,off+16); strings_start=u32(m,off+20)
    data_off=off+strings_start
    utf8=bool(flags & 0x100)
    offsets=[u32(m, off+28+4*i) for i in range(str_count)]
    def getstr(i):
        o=data_off+offsets[i]
        if utf8:
            l=m[o]; o+=1
            if l&0x80: o+=1
            l2=m[o]; o+=1
            if l2&0x80: o+=1
            return m[o:o+l2].decode('utf-8','replace')
        l=u16(m,o); o+=2
        return m[o:o+l*2].decode('utf-16-le','replace')
    p=off+sp_size; changed=[]
    while p < len(m)-8:
        t=u16(m,p); sz=u32(m,p+4)
        if sz==0: break
        if t==0x0102 and getstr(u32(m,p+20))=='manifest':
            a0=u16(m,p+24); asz=u16(m,p+26); ac=u16(m,p+28)
            base=p+16+a0
            for i in range(ac):
                a=base+i*asz
                nm=getstr(u32(m,a+4))
                if nm in ('versionCode','versionCodeMajor'):
                    old=u32(m,a+16)
                    struct.pack_into('<I', m, a+16, newv)
                    changed.append((nm, old, newv))
            break
        p+=sz
    return changed

def main():
    src, dst, newv = sys.argv[1], sys.argv[2], int(sys.argv[3])
    z=zipfile.ZipFile(src)
    m=bytearray(z.read('AndroidManifest.xml'))
    ch=patch(m, newv)
    if not ch: raise SystemExit("没找到 versionCode")
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as zo:
        for it in z.infolist():
            zo.writestr(it, bytes(m) if it.filename=='AndroidManifest.xml' else z.read(it.filename))
    for nm,o,n in ch: print(f"{nm}: {o} -> {n}")
    print("输出:", dst)

if __name__=='__main__':
    main()
