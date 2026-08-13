[app]
title = Universal Media Downloader
package.name = unimediadownloader
package.domain = org.mymediaapp
source.dir = .
source.include_exts = py,png,jpg
version = 1.0.0

# Strict dependency mapping to skip buggy alpha libraries
requirements = python3,kivy,yt-dlp,certifi,openssl

orientation = portrait
fullscreen = 1

android.permissions = INTERNET

# STABILITY ENFORCEMENT: Force stable SDK & NDK versions
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Force the stable Python framework target
python3_version = 3.11

# Strict hardware profiling matching your Samsung A06 architecture
android.archs = arm64-v8a
android.accept_sdk_license = True
