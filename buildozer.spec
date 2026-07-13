[app]
title = QuantMatrix
package.name = quantmatrixapp
package.domain = org.quant
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,requests,feedparser

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a
android.allow_backup = True
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
