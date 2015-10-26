#!/usr/bin/env bash

cd resource

inkscape -z -e icon.iconset/icon_512x512@2x.png -w 1024 -h 1024 icon.svg

inkscape -z -e icon.iconset/icon_512x512.png -w 512 -h 512 icon.svg
cp icon.iconset/icon_512x512.png icon.iconset/icon_256x256@2x.png

inkscape -z -e icon.iconset/icon_256x256.png -w 256 -h 256 icon.svg
cp icon.iconset/icon_256x256.png icon.iconset/icon_128x128@2x.png

inkscape -z -e icon.iconset/icon_128x128.png -w 128 -h 128 icon.svg

inkscape -z -e icon.iconset/icon_32x32@2x.png -w 64 -h 64 icon.svg

inkscape -z -e icon.iconset/icon_32x32.png -w 32 -h 32 icon.svg
cp icon.iconset/icon_32x32.png icon.iconset/icon_16x16@2x.png

inkscape -z -e icon.iconset/icon_16x16.png -w 16 -h 16 icon.svg

iconutil -c icns icon.iconset
