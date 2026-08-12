[app]
title = Universal Media Downloader
package.name = unimediadownloader
package.domain = org.mymediaapp
source.dir = .
source.include_exts = py,png,jpg
version = 1.0.0

# Strict dependency mapping to skip buggy alpha libraries
requirements = python3,kivy==2.3.0,yt-dlp,certifi,openssl

orientation = portrait
fullscreen = 1

android.permissions = INTERNET

# Stable build environment layers
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# CRITICAL STABILITY ENFORCEMENT: Force strict python version allocation
python3_version = 3.10.12

# Strict hardware profiling matching your Samsung A06 architecture
android.archs = arm64-v8a
android.accept_sdk_license = True
