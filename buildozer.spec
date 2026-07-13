[app]
title = QuantMatrix
package.name = quantmatrixapp
package.domain = org.quant
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
# FIXED: Injected openssl to build the secure handshake module for HTTPS connections
requirements = python3,kivy,requests,openssl,certifi

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a
android.allow_backup = True
# FIXED: Bumped target to modern safety guidelines to clear Google Play Protect warnings
android.api = 34
android.minapi = 21
android.ndk_api = 21
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
