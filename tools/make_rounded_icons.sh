#!/usr/bin/env bash
# 把任意 logo 做成桌面可用的 136x136 圆角图标
# 用法: ./make_rounded_icons.sh input.png output.png [圆角半径]
set -euo pipefail
IN="$1"; OUT="$2"; R="${3:-22}"
convert "$IN" -strip -resize 96x96 \
  \( -size 96x96 xc:black -fill white -draw "roundrectangle 0,0,95,95,$R,$R" \) \
  -alpha off -compose CopyOpacity -composite \
  -background none -gravity center -extent 136x136 \
  -strip "PNG32:$OUT"
convert "$OUT" -format "center=%[pixel:p{68,68}] corner=%[pixel:p{2,2}]\n" info:
