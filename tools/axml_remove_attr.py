#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 APK 的 AndroidManifest.xml 中删除一个顶层属性（二进制 AXML 原地删字节）

用法: python3 tools/axml_remove_attr.py in.apk out.apk sharedUserId

说明: 只处理 <manifest> 上的属性；会同步修正 attributeCount、chunk size、总大小。
用于把 sharedUserId=android.uid.system 去掉，以便第三方签名后安装到普通环境。
"""
import struct, sys, zipfile

def u16(b,o): return struct.unpack_from('<H', b, o)[0]
def u32(b,o): return struct.unpack_from('<I', b, o)[0]

def remove_attr(m, want):
    assert u16(m,0)==0x0003
    off=8
    assert u16(m,off)==0x0001
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
    p=off+sp_size
    while p < len(m)-8:
        t=u16(m,p); sz=u32(m,p+4)
        if sz==0: break
        if t==0x0102 and getstr(u32(m,p+20))=='manifest':
            a0=u16(m,p+24); asz=u16(m,p+26); ac=u16(m,p+28)
            base=p+16+a0
            for i in range(ac):
                a=base+i*asz
                if getstr(u32(m,a+4))==want:
                    del m[a:a+asz]
                    struct.pack_into('<H', m, p+28, ac-1)
                    struct.pack_into('<I', m, p+4, sz-asz)
                    struct.pack_into('<I', m, 4, u32(m,4)-asz)
                    return True
            return False
        p+=sz
    return False

def main():
    src,dst,attr=sys.argv[1],sys.argv[2],sys.argv[3]
    z=zipfile.ZipFile(src)
    m=bytearray(z.read('AndroidManifest.xml'))
    ok=remove_attr(m, attr)
    print("删除", attr, "->", ok)
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as zo:
        for it in z.infolist():
            zo.writestr(it, bytes(m) if it.filename=='AndroidManifest.xml' else z.read(it.filename))
    print("输出:", dst)

if __name__=='__main__':
    main()
