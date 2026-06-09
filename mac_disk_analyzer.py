#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mac 磁盘空间分析工具 v1.0
"""

import os
import subprocess
import json
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

PORT = 18765

PATHS_CONFIG = [

    # ════════════════════════════════════════
    #  缓存 & 日志
    # ════════════════════════════════════════
    {"path": "~/Library/Caches",
     "name": "用户应用缓存",
     "category": "缓存 & 日志",
     "desc": "各 App 产生的临时缓存文件，删除后 App 会自动重新生成，不影响正常使用。通常是最大的可清理空间之一。",
     "safety": "safe"},
    {"path": "~/Library/Logs",
     "name": "用户应用日志",
     "category": "缓存 & 日志",
     "desc": "App 运行产生的日志文件，可安全删除。",
     "safety": "safe"},
    {"path": "~/.Trash",
     "name": "废纸篓",
     "category": "缓存 & 日志",
     "desc": "已删除但未清空的文件，清空后立即释放空间（也可在 Finder 中右键废纸篓→清倒废纸篓）。",
     "safety": "safe"},
    {"path": "~/Library/Saved Application State",
     "name": "应用窗口恢复状态",
     "category": "缓存 & 日志",
     "desc": "记录 App 上次退出时的窗口状态，用于重新打开时恢复。删除后下次打开 App 不会自动恢复窗口，可安全清理。",
     "safety": "safe"},
    {"path": "/Library/Caches",
     "name": "系统缓存",
     "category": "缓存 & 日志",
     "desc": "macOS 系统级缓存，需要管理员权限，建议通过系统工具清理。",
     "safety": "caution"},
    {"path": "/private/var/log",
     "name": "系统日志",
     "category": "缓存 & 日志",
     "desc": "macOS 系统运行日志，需要管理员权限，一般无需手动清理。",
     "safety": "caution"},
    {"path": "/private/var/folders",
     "name": "系统临时文件夹",
     "category": "缓存 & 日志",
     "desc": "macOS 为每个用户/进程创建的临时目录（TMPDIR），不建议手动清理，系统会自动管理。",
     "safety": "danger"},
    {"path": "/private/tmp",
     "name": "系统 /tmp 目录",
     "category": "缓存 & 日志",
     "desc": "系统临时文件，重启后自动清空，不建议手动删除。",
     "safety": "danger"},

    # ════════════════════════════════════════
    #  Apple 开发（Xcode / iOS）
    # ════════════════════════════════════════
    {"path": "~/Library/Developer/Xcode/DerivedData",
     "name": "Xcode 编译缓存",
     "category": "Apple 开发",
     "desc": "Xcode 编译项目产生的中间产物，体积通常很大（可达数十 GB）。可安全删除，重新编译时自动重建。",
     "safety": "safe"},
    {"path": "~/Library/Developer/CoreSimulator/Caches",
     "name": "iOS 模拟器缓存",
     "category": "Apple 开发",
     "desc": "iOS 模拟器运行时缓存，可安全删除。",
     "safety": "safe"},
    {"path": "~/Library/Caches/CocoaPods",
     "name": "CocoaPods 缓存",
     "category": "Apple 开发",
     "desc": "CocoaPods 依赖管理器的下载缓存，可安全删除（命令：pod cache clean --all）。",
     "safety": "safe"},
    {"path": "~/.cocoapods/repos",
     "name": "CocoaPods 仓库索引",
     "category": "Apple 开发",
     "desc": "CocoaPods 的 Spec 仓库索引，体积可达数百 MB。可删除，pod install 时会重新拉取。",
     "safety": "safe"},
    {"path": "~/Library/Developer/Xcode/Archives",
     "name": "Xcode 打包归档",
     "category": "Apple 开发",
     "desc": "App Store 打包生成的 .xcarchive，如已上传或有备份可删除旧版本。",
     "safety": "caution"},
    {"path": "~/Library/Developer/Xcode/iOS DeviceSupport",
     "name": "Xcode 设备支持文件",
     "category": "Apple 开发",
     "desc": "连接真机调试时下载的系统符号文件，可删除不再使用的 iOS 版本文件。",
     "safety": "caution"},
    {"path": "~/Library/Developer/Xcode/watchOS DeviceSupport",
     "name": "Xcode watchOS 支持文件",
     "category": "Apple 开发",
     "desc": "Apple Watch 调试支持文件，可删除不再使用的版本。",
     "safety": "caution"},
    {"path": "~/Library/Developer/CoreSimulator/Devices",
     "name": "iOS 模拟器设备镜像",
     "category": "Apple 开发",
     "desc": "iOS/iPadOS 模拟器镜像，单个设备可达数 GB。建议在 Xcode → Window → Devices and Simulators 中删除不用的版本。",
     "safety": "caution"},
    {"path": "~/Library/Developer/Xcode/UserData/Previews",
     "name": "SwiftUI 预览缓存",
     "category": "Apple 开发",
     "desc": "Xcode SwiftUI Canvas 预览生成的缓存文件，可安全删除。",
     "safety": "safe"},
    {"path": "~/Library/Application Support/MobileSync/Backup",
     "name": "iPhone / iPad 本地备份",
     "category": "Apple 开发",
     "desc": "通过 Finder 或 iTunes 创建的 iOS 设备备份，单份备份可达数十 GB。如有 iCloud 备份或已不再需要旧备份可删除。",
     "safety": "caution"},

    # ════════════════════════════════════════
    #  Node.js / 前端
    # ════════════════════════════════════════
    {"path": "~/.npm/_cacache",
     "name": "npm 缓存",
     "category": "Node.js / 前端",
     "desc": "npm 包管理器缓存，可安全删除（命令：npm cache clean --force）。",
     "safety": "safe"},
    {"path": "~/.yarn/cache",
     "name": "Yarn 缓存",
     "category": "Node.js / 前端",
     "desc": "Yarn 包管理器缓存，可安全删除（命令：yarn cache clean）。",
     "safety": "safe"},
    {"path": "~/.pnpm-store",
     "name": "pnpm 全局存储",
     "category": "Node.js / 前端",
     "desc": "pnpm 的全局包存储，删除后重装依赖会重新下载（命令：pnpm store prune）。",
     "safety": "safe"},
    {"path": "~/.nvm",
     "name": "nvm Node.js 版本库",
     "category": "Node.js / 前端",
     "desc": "nvm 管理的全部 Node.js 版本，可删除不再使用的版本（命令：nvm uninstall <version>）。",
     "safety": "caution"},
    {"path": "~/.volta",
     "name": "Volta Node.js 工具链",
     "category": "Node.js / 前端",
     "desc": "Volta 管理的 Node.js / npm / yarn 版本，可删除不再使用的工具版本。",
     "safety": "caution"},
    {"path": "~/.bun",
     "name": "Bun 运行时",
     "category": "Node.js / 前端",
     "desc": "Bun JavaScript 运行时的安装目录和缓存。",
     "safety": "caution"},
    {"path": "~/.deno",
     "name": "Deno 运行时缓存",
     "category": "Node.js / 前端",
     "desc": "Deno 的缓存和已安装模块，可安全删除，使用时会重新下载。",
     "safety": "safe"},

    # ════════════════════════════════════════
    #  Python
    # ════════════════════════════════════════
    {"path": "~/Library/Caches/pip",
     "name": "pip 下载缓存",
     "category": "Python",
     "desc": "pip 包下载缓存，可安全删除（命令：pip cache purge）。",
     "safety": "safe"},
    {"path": "~/.cache/pip",
     "name": "pip 缓存（.cache）",
     "category": "Python",
     "desc": "pip 在 ~/.cache 下的缓存副本，可安全删除。",
     "safety": "safe"},
    {"path": "~/.pyenv/versions",
     "name": "pyenv Python 版本",
     "category": "Python",
     "desc": "pyenv 管理的多个 Python 版本，可删除不再使用的版本（命令：pyenv uninstall <version>）。",
     "safety": "caution"},
    {"path": "~/opt/anaconda3",
     "name": "Anaconda3 发行版",
     "category": "Python",
     "desc": "Anaconda Python 发行版及所有 conda 环境，体积通常很大（数 GB 至数十 GB）。",
     "safety": "caution"},
    {"path": "~/opt/miniconda3",
     "name": "Miniconda3",
     "category": "Python",
     "desc": "Miniconda 最小化 Conda 环境，包含所有创建的虚拟环境。",
     "safety": "caution"},
    {"path": "~/miniconda3",
     "name": "Miniconda3（根目录安装）",
     "category": "Python",
     "desc": "安装在 ~/miniconda3 的 Miniconda 环境。",
     "safety": "caution"},
    {"path": "~/anaconda3",
     "name": "Anaconda3（根目录安装）",
     "category": "Python",
     "desc": "安装在 ~/anaconda3 的 Anaconda 环境。",
     "safety": "caution"},
    {"path": "~/.conda/pkgs",
     "name": "Conda 包缓存",
     "category": "Python",
     "desc": "Conda 下载的安装包缓存，可安全删除（命令：conda clean --all）。",
     "safety": "safe"},
    {"path": "~/.jupyter",
     "name": "Jupyter 配置与缓存",
     "category": "Python",
     "desc": "Jupyter Notebook / Lab 的配置、内核信息和运行时数据。",
     "safety": "caution"},

    # ════════════════════════════════════════
    #  Java / Kotlin / JVM
    # ════════════════════════════════════════
    {"path": "~/.gradle/caches",
     "name": "Gradle 依赖缓存",
     "category": "Java / JVM",
     "desc": "Android / Java / Kotlin 的 Gradle 构建缓存，可安全删除，构建时自动重新下载。",
     "safety": "safe"},
    {"path": "~/.gradle/wrapper",
     "name": "Gradle Wrapper 下载",
     "category": "Java / JVM",
     "desc": "各版本 Gradle 构建工具的下载存档，可删除不再使用的版本。",
     "safety": "safe"},
    {"path": "~/.m2/repository",
     "name": "Maven 本地仓库",
     "category": "Java / JVM",
     "desc": "Maven 本地依赖缓存，可安全删除，构建时自动重新下载。",
     "safety": "safe"},
    {"path": "~/Library/Java/JavaVirtualMachines",
     "name": "已安装的 JDK",
     "category": "Java / JVM",
     "desc": "通过 Homebrew / SDKMAN / 官方安装的 JDK，可删除不再使用的版本。每个 JDK 约 300–600 MB。",
     "safety": "caution"},
    {"path": "~/.sdkman",
     "name": "SDKMAN 工具链",
     "category": "Java / JVM",
     "desc": "SDKMAN 管理的 Java / Kotlin / Groovy / Scala 等 SDK 版本。",
     "safety": "caution"},
    {"path": "~/.ivy2/cache",
     "name": "Ivy / SBT 缓存",
     "category": "Java / JVM",
     "desc": "Scala SBT / Apache Ivy 依赖缓存，可安全删除。",
     "safety": "safe"},
    {"path": "~/.sbt",
     "name": "SBT 配置与缓存",
     "category": "Java / JVM",
     "desc": "Scala 构建工具 SBT 的配置和启动文件。",
     "safety": "caution"},

    # ════════════════════════════════════════
    #  Go
    # ════════════════════════════════════════
    {"path": "~/go/pkg/mod",
     "name": "Go 模块缓存",
     "category": "Go",
     "desc": "Go 语言模块依赖缓存（GOPATH/pkg/mod），可安全删除（命令：go clean -modcache）。",
     "safety": "safe"},
    {"path": "~/Library/Caches/go-build",
     "name": "Go 编译缓存",
     "category": "Go",
     "desc": "Go 编译器的构建缓存，可安全删除（命令：go clean -cache），下次编译会重建。",
     "safety": "safe"},
    {"path": "~/.cache/go-build",
     "name": "Go 编译缓存（.cache）",
     "category": "Go",
     "desc": "Go 编译器在 ~/.cache 下的构建缓存副本，可安全删除。",
     "safety": "safe"},

    # ════════════════════════════════════════
    #  Rust
    # ════════════════════════════════════════
    {"path": "~/.cargo/registry",
     "name": "Cargo 包注册表缓存",
     "category": "Rust",
     "desc": "Rust Cargo 从 crates.io 下载的包源码缓存，可安全删除（命令：cargo cache -a）。",
     "safety": "safe"},
    {"path": "~/.cargo/git",
     "name": "Cargo Git 依赖缓存",
     "category": "Rust",
     "desc": "Cargo 从 Git 仓库克隆的依赖缓存，可安全删除。",
     "safety": "safe"},
    {"path": "~/.rustup/toolchains",
     "name": "Rustup 工具链",
     "category": "Rust",
     "desc": "rustup 管理的 Rust 工具链版本，可删除不再使用的版本（命令：rustup toolchain uninstall <name>）。",
     "safety": "caution"},

    # ════════════════════════════════════════
    #  Flutter / Dart
    # ════════════════════════════════════════
    {"path": "~/.pub-cache",
     "name": "Dart / Flutter pub 缓存",
     "category": "Flutter / Dart",
     "desc": "Dart pub 包管理器的全局缓存，可安全删除（命令：dart pub cache clean）。",
     "safety": "safe"},
    {"path": "~/flutter",
     "name": "Flutter SDK",
     "category": "Flutter / Dart",
     "desc": "Flutter SDK 安装目录，包含工具链和框架源码，可删除旧版本。",
     "safety": "caution"},
    {"path": "~/fvm/versions",
     "name": "FVM Flutter 版本管理",
     "category": "Flutter / Dart",
     "desc": "FVM（Flutter Version Manager）管理的多个 Flutter 版本，可删除不再使用的版本。",
     "safety": "caution"},
    {"path": "~/.flutter",
     "name": "Flutter 配置缓存",
     "category": "Flutter / Dart",
     "desc": "Flutter 工具链的全局配置和缓存。",
     "safety": "caution"},

    # ════════════════════════════════════════
    #  Ruby
    # ════════════════════════════════════════
    {"path": "~/.gem",
     "name": "Ruby Gem 本地安装",
     "category": "Ruby",
     "desc": "全局安装的 Ruby gem，可删除不再需要的包（命令：gem cleanup）。",
     "safety": "caution"},
    {"path": "~/.bundle/cache",
     "name": "Bundler 缓存",
     "category": "Ruby",
     "desc": "Ruby Bundler 的 gem 下载缓存，可安全删除。",
     "safety": "safe"},
    {"path": "~/.rbenv/versions",
     "name": "rbenv Ruby 版本",
     "category": "Ruby",
     "desc": "rbenv 管理的多个 Ruby 版本，可删除不再使用的版本。",
     "safety": "caution"},
    {"path": "~/.rvm",
     "name": "RVM Ruby 版本管理",
     "category": "Ruby",
     "desc": "RVM 管理的 Ruby 版本和 gemset，体积可达数 GB。",
     "safety": "caution"},

    # ════════════════════════════════════════
    #  PHP / Composer
    # ════════════════════════════════════════
    {"path": "~/.composer/cache",
     "name": "Composer 缓存",
     "category": "PHP",
     "desc": "PHP Composer 依赖管理器的下载缓存，可安全删除（命令：composer clear-cache）。",
     "safety": "safe"},

    # ════════════════════════════════════════
    #  Android 开发
    # ════════════════════════════════════════
    {"path": "~/Library/Android/sdk",
     "name": "Android SDK",
     "category": "Android 开发",
     "desc": "Android SDK 完整安装，包含平台工具、编译工具等，体积通常数 GB 至数十 GB。",
     "safety": "caution"},
    {"path": "~/.android/avd",
     "name": "Android 虚拟设备（AVD）",
     "category": "Android 开发",
     "desc": "Android 模拟器镜像，单个设备可达数 GB。可通过 Android Studio AVD Manager 删除不用的版本。",
     "safety": "caution"},
    {"path": "~/.android/cache",
     "name": "Android 工具缓存",
     "category": "Android 开发",
     "desc": "Android 构建工具的缓存数据，可安全删除。",
     "safety": "safe"},

    # ════════════════════════════════════════
    #  其他开发工具
    # ════════════════════════════════════════
    {"path": "~/Library/Caches/Homebrew",
     "name": "Homebrew 下载缓存",
     "category": "其他开发工具",
     "desc": "Homebrew 安装包的下载缓存，可安全删除（命令：brew cleanup）。",
     "safety": "safe"},
    {"path": "~/.cache",
     "name": "用户 .cache 目录",
     "category": "其他开发工具",
     "desc": "Linux 兼容的用户缓存目录，通常存放 pip、Go 等工具的缓存，可安全删除。",
     "safety": "safe"},
    {"path": "~/.asdf/installs",
     "name": "asdf 版本管理工具链",
     "category": "其他开发工具",
     "desc": "asdf 管理的多语言版本（Node / Python / Ruby / Go 等），可删除不再使用的版本。",
     "safety": "caution"},
    {"path": "~/.terraform.d/plugins",
     "name": "Terraform 插件缓存",
     "category": "其他开发工具",
     "desc": "Terraform provider 插件缓存，可安全删除，terraform init 时会重新下载。",
     "safety": "safe"},
    {"path": "~/.minikube",
     "name": "Minikube 本地 K8s",
     "category": "其他开发工具",
     "desc": "Minikube 本地 Kubernetes 集群数据和镜像，体积通常较大。",
     "safety": "caution"},
    {"path": "~/.kube/cache",
     "name": "kubectl 缓存",
     "category": "其他开发工具",
     "desc": "kubectl 命令行工具的 API 发现缓存，可安全删除。",
     "safety": "safe"},
    {"path": "~/.helm",
     "name": "Helm 配置与缓存",
     "category": "其他开发工具",
     "desc": "Kubernetes Helm 包管理器的配置和 chart 仓库缓存，可安全删除。",
     "safety": "safe"},
    {"path": "~/Library/Containers/com.docker.docker",
     "name": "Docker Desktop 数据",
     "category": "其他开发工具",
     "desc": "Docker Desktop 存储所有容器、镜像和数据卷，删除将清除全部本地镜像，请务必谨慎！",
     "safety": "danger"},
    {"path": "/opt/homebrew/Cellar",
     "name": "Homebrew 软件包（Apple Silicon）",
     "category": "其他开发工具",
     "desc": "Homebrew 安装的软件，请勿直接删除。卸载用 brew uninstall <name>，清理旧版本用 brew cleanup。",
     "safety": "danger"},
    {"path": "/usr/local/Cellar",
     "name": "Homebrew 软件包（Intel）",
     "category": "其他开发工具",
     "desc": "Intel Mac 的 Homebrew 软件包，请勿直接删除。",
     "safety": "danger"},

    # ════════════════════════════════════════
    #  IDE & 编辑器
    # ════════════════════════════════════════
    {"path": "~/.vscode/extensions",
     "name": "VS Code 插件",
     "category": "IDE & 编辑器",
     "desc": "已安装的 VS Code 扩展，可删除不再使用的插件（在 VS Code 扩展面板中卸载更安全）。",
     "safety": "caution"},
    {"path": "~/Library/Caches/JetBrains",
     "name": "JetBrains IDE 缓存",
     "category": "IDE & 编辑器",
     "desc": "IntelliJ IDEA / PyCharm / WebStorm 等 JetBrains IDE 的缓存，可安全删除（IDE 会自动重建）。",
     "safety": "safe"},
    {"path": "~/Library/Application Support/JetBrains",
     "name": "JetBrains IDE 配置",
     "category": "IDE & 编辑器",
     "desc": "JetBrains IDE 的配置文件、插件和日志，体积可达数 GB。删除前请备份重要配置。",
     "safety": "caution"},
    {"path": "~/Library/Logs/JetBrains",
     "name": "JetBrains IDE 日志",
     "category": "IDE & 编辑器",
     "desc": "JetBrains IDE 的运行日志，可安全删除。",
     "safety": "safe"},
    {"path": "~/.config/Code/Cache",
     "name": "VS Code 内容缓存",
     "category": "IDE & 编辑器",
     "desc": "VS Code 的页面缓存，可安全删除。",
     "safety": "safe"},

    # ════════════════════════════════════════
    #  设计工具
    # ════════════════════════════════════════
    {"path": "~/Library/Application Support/Adobe",
     "name": "Adobe 应用数据",
     "category": "设计工具",
     "desc": "Photoshop / Illustrator / Premiere 等 Adobe 软件的应用数据，体积通常很大。",
     "safety": "caution"},
    {"path": "~/Library/Caches/Adobe",
     "name": "Adobe 缓存",
     "category": "设计工具",
     "desc": "Adobe 软件的缓存文件，可安全删除，重新使用软件时会重建。",
     "safety": "safe"},
    {"path": "~/Library/Application Support/com.bohemiancoding.sketch3",
     "name": "Sketch 应用数据",
     "category": "设计工具",
     "desc": "Sketch 设计工具的数据，包含插件和自动备份。",
     "safety": "caution"},
    {"path": "~/Library/Application Support/Figma",
     "name": "Figma 桌面应用数据",
     "category": "设计工具",
     "desc": "Figma 桌面客户端的本地缓存和数据，可安全清理。",
     "safety": "safe"},

    # ════════════════════════════════════════
    #  游戏 & 娱乐
    # ════════════════════════════════════════
    {"path": "~/Library/Application Support/Steam",
     "name": "Steam 游戏库",
     "category": "游戏 & 娱乐",
     "desc": "Steam 平台客户端数据和已安装游戏，删除可释放大量空间，但已安装游戏需重新下载。",
     "safety": "caution"},
    {"path": "~/Library/Application Support/Riot Games",
     "name": "Riot 游戏数据",
     "category": "游戏 & 娱乐",
     "desc": "英雄联盟等 Riot Games 游戏数据，删除需重新安装游戏。",
     "safety": "caution"},
    {"path": "~/Library/Caches/com.spotify.client",
     "name": "Spotify 缓存",
     "category": "游戏 & 娱乐",
     "desc": "Spotify 客户端的音乐缓存，可安全删除，Spotify 会根据需要重新缓存。",
     "safety": "safe"},
    {"path": "~/Library/Application Support/Spotify",
     "name": "Spotify 应用数据",
     "category": "游戏 & 娱乐",
     "desc": "Spotify 本地存储数据，包含缓存和配置。",
     "safety": "caution"},

    # ════════════════════════════════════════
    #  个人文件
    # ════════════════════════════════════════
    {"path": "~/Downloads",
     "name": "下载文件夹",
     "category": "个人文件",
     "desc": "所有下载内容。建议手动清理不再需要的 .dmg / .pkg / .zip 安装包，这些通常是大文件。",
     "safety": "manual"},
    {"path": "~/Desktop",
     "name": "桌面",
     "category": "个人文件",
     "desc": "桌面上的文件，请手动检查后清理。",
     "safety": "manual"},
    {"path": "~/Movies",
     "name": "影片文件夹",
     "category": "个人文件",
     "desc": "视频文件通常体积较大，请手动检查后决定是否清理。",
     "safety": "manual"},
    {"path": "~/Music",
     "name": "音乐文件夹",
     "category": "个人文件",
     "desc": "音乐和播客文件，请手动检查是否有不再需要的本地音频。",
     "safety": "manual"},
    {"path": "~/Music/Music/Media.localized",
     "name": "Apple Music 本地媒体",
     "category": "个人文件",
     "desc": "Apple Music App 管理的本地音乐文件，请手动检查后在 Music App 内管理。",
     "safety": "manual"},
    {"path": "~/Pictures",
     "name": "图片文件夹",
     "category": "个人文件",
     "desc": "照片和图片，请手动检查。建议使用 iCloud 照片库减少本地占用。",
     "safety": "manual"},
    {"path": "~/Documents",
     "name": "文稿文件夹",
     "category": "个人文件",
     "desc": "文档文件，请手动检查后清理。",
     "safety": "manual"},
    {"path": "~/Library/Mobile Documents",
     "name": "iCloud Drive 本地缓存",
     "category": "个人文件",
     "desc": "iCloud Drive 同步到本地的文件，不建议直接删除，请在 Finder 或 iCloud 设置中管理。",
     "safety": "danger"},

    # ════════════════════════════════════════
    #  应用数据
    # ════════════════════════════════════════
    {"path": "~/Library/Application Support",
     "name": "应用支持数据（总目录）",
     "category": "应用数据",
     "desc": "各 App 的配置文件和数据库，删除对应 App 子目录可能导致设置丢失，请谨慎操作。",
     "safety": "caution"},
    {"path": "~/Library/Mail",
     "name": "Apple Mail 数据库",
     "category": "应用数据",
     "desc": "Apple Mail 的本地邮件存储，体积可达数 GB。不建议直接删除，请在 Mail App 内管理。",
     "safety": "danger"},
    {"path": "~/Library/Messages",
     "name": "iMessage 消息记录",
     "category": "应用数据",
     "desc": "所有 iMessage 和短信记录，不建议直接删除，请在「信息」App 内管理。",
     "safety": "danger"},
    {"path": "~/Pictures/Photos Library.photoslibrary",
     "name": "Photos 照片图库",
     "category": "应用数据",
     "desc": "系统照片图库，可能很大。不建议直接删除，请在「照片」App 中管理或开启 iCloud 照片以优化本地存储。",
     "safety": "danger"},
    {"path": "~/Library/Containers/com.apple.Safari",
     "name": "Safari 浏览器数据",
     "category": "应用数据",
     "desc": "Safari 的历史记录、书签、密码等数据，不建议直接删除，请在 Safari 偏好设置内管理。",
     "safety": "danger"},

    # ════════════════════════════════════════
    #  虚拟机
    # ════════════════════════════════════════
    {"path": "~/Virtual Machines.localized",
     "name": "VMware Fusion 虚拟机",
     "category": "虚拟机",
     "desc": "VMware Fusion 虚拟机文件，体积通常极大，可删除不再使用的虚拟机文件。",
     "safety": "caution"},
    {"path": "~/Parallels",
     "name": "Parallels Desktop 虚拟机",
     "category": "虚拟机",
     "desc": "Parallels Desktop 虚拟机文件，可删除不再需要的虚拟机。",
     "safety": "caution"},
    {"path": "~/.vagrant.d/boxes",
     "name": "Vagrant Box 镜像",
     "category": "虚拟机",
     "desc": "Vagrant 虚拟机镜像，可删除不再使用的 box（命令：vagrant box remove <name>）。",
     "safety": "caution"},
    {"path": "~/.local/share/containers",
     "name": "Podman 容器数据",
     "category": "虚拟机",
     "desc": "Podman 容器引擎数据（替代 Docker 的无守护进程方案），删除将清除所有镜像。",
     "safety": "danger"},

    # ════════════════════════════════════════
    #  AI / 机器学习
    # ════════════════════════════════════════
    {"path": "~/.ollama/models",
     "name": "Ollama 本地模型",
     "category": "AI / 机器学习",
     "desc": "Ollama 下载的本地大语言模型文件（llama、mistral 等），单个模型 2–70 GB。可删除不再使用的模型（命令：ollama rm <model>）。",
     "safety": "caution"},
    {"path": "~/Library/Application Support/LM Studio",
     "name": "LM Studio 应用数据",
     "category": "AI / 机器学习",
     "desc": "LM Studio 的应用数据，模型文件通常存放在单独目录，请在 LM Studio 内管理。",
     "safety": "caution"},
    {"path": "~/.cache/huggingface",
     "name": "Hugging Face 模型缓存",
     "category": "AI / 机器学习",
     "desc": "通过 transformers / diffusers 下载的预训练模型，单个模型可达数 GB 至数十 GB。可删除不再使用的模型。",
     "safety": "caution"},
    {"path": "~/.cache/torch",
     "name": "PyTorch 模型缓存",
     "category": "AI / 机器学习",
     "desc": "PyTorch Hub 下载的预训练模型缓存，可安全删除，使用时会重新下载。",
     "safety": "safe"},
    {"path": "~/.keras",
     "name": "Keras / TensorFlow 缓存",
     "category": "AI / 机器学习",
     "desc": "Keras 下载的预训练权重和数据集缓存，可安全删除，使用时会重新下载。",
     "safety": "safe"},
    {"path": "~/Library/Application Support/nomic.ai/GPT4All",
     "name": "GPT4All 本地模型",
     "category": "AI / 机器学习",
     "desc": "GPT4All 下载的本地模型文件，体积通常很大，可删除不再使用的模型。",
     "safety": "caution"},
    {"path": "~/.cache/kaggle",
     "name": "Kaggle 数据集缓存",
     "category": "AI / 机器学习",
     "desc": "通过 Kaggle API 下载的数据集缓存，可安全删除。",
     "safety": "safe"},

    # ════════════════════════════════════════
    #  浏览器
    # ════════════════════════════════════════
    {"path": "~/Library/Caches/Google/Chrome",
     "name": "Chrome 缓存",
     "category": "浏览器",
     "desc": "Google Chrome 浏览器缓存，可安全删除（也可在 Chrome 设置→清除浏览数据中清理）。",
     "safety": "safe"},
    {"path": "~/Library/Application Support/Google/Chrome",
     "name": "Chrome 用户数据",
     "category": "浏览器",
     "desc": "Chrome 的用户配置、书签、历史记录、密码等，不建议直接删除，请在 Chrome 内管理。",
     "safety": "danger"},
    {"path": "~/Library/Caches/Firefox",
     "name": "Firefox 缓存",
     "category": "浏览器",
     "desc": "Firefox 浏览器缓存文件，可安全删除（也可在 Firefox 设置→隐私中清理）。",
     "safety": "safe"},
    {"path": "~/Library/Application Support/Firefox/Profiles",
     "name": "Firefox 用户配置",
     "category": "浏览器",
     "desc": "Firefox 的书签、历史、密码等用户数据，不建议直接删除，请在 Firefox 内管理。",
     "safety": "danger"},
    {"path": "~/Library/Caches/com.microsoft.edgemac",
     "name": "Edge 缓存",
     "category": "浏览器",
     "desc": "Microsoft Edge 浏览器缓存，可安全删除。",
     "safety": "safe"},
    {"path": "~/Library/Application Support/BraveSoftware/Brave-Browser",
     "name": "Brave 用户数据",
     "category": "浏览器",
     "desc": "Brave 浏览器的用户数据，不建议直接删除，请在 Brave 内管理。",
     "safety": "danger"},
    {"path": "~/Library/Application Support/Arc",
     "name": "Arc 浏览器数据",
     "category": "浏览器",
     "desc": "Arc 浏览器的应用数据，不建议直接删除。",
     "safety": "danger"},

    # ════════════════════════════════════════
    #  即时通讯 & 协作
    # ════════════════════════════════════════
    {"path": "~/Library/Application Support/Slack",
     "name": "Slack 应用数据",
     "category": "即时通讯",
     "desc": "Slack 桌面客户端的本地缓存和应用数据，可删除以释放空间，重新登录会重新下载。",
     "safety": "caution"},
    {"path": "~/Library/Caches/com.tinyspeck.slackmacgap",
     "name": "Slack 缓存",
     "category": "即时通讯",
     "desc": "Slack 客户端缓存文件，可安全删除。",
     "safety": "safe"},
    {"path": "~/Library/Application Support/zoom.us",
     "name": "Zoom 应用数据",
     "category": "即时通讯",
     "desc": "Zoom 会议客户端数据，包含会议录制等，请手动检查后清理。",
     "safety": "manual"},
    {"path": "~/Documents/Zoom",
     "name": "Zoom 会议录制",
     "category": "即时通讯",
     "desc": "Zoom 本地录制的会议视频，体积可能很大，请手动检查是否仍需要保留。",
     "safety": "manual"},
    {"path": "~/Library/Application Support/discord",
     "name": "Discord 应用数据",
     "category": "即时通讯",
     "desc": "Discord 客户端本地数据和缓存，可安全删除，重启后会重新下载。",
     "safety": "safe"},
    {"path": "~/Library/Caches/com.hnc.Discord",
     "name": "Discord 缓存",
     "category": "即时通讯",
     "desc": "Discord 缓存文件，可安全删除。",
     "safety": "safe"},
    {"path": "~/Library/Containers/com.tencent.xinWeChat",
     "name": "微信数据",
     "category": "即时通讯",
     "desc": "微信 macOS 版的聊天记录、文件、图片等，体积可达数十 GB。不建议直接删除，请在微信内管理。",
     "safety": "danger"},
    {"path": "~/Library/Application Support/WeChat",
     "name": "微信应用数据（旧版）",
     "category": "即时通讯",
     "desc": "旧版微信存储的应用数据，请手动检查。",
     "safety": "caution"},
    {"path": "~/Library/Application Support/TelegramDesktop",
     "name": "Telegram 应用数据",
     "category": "即时通讯",
     "desc": "Telegram 桌面端的本地缓存和媒体文件，可安全删除，消息历史存储在云端。",
     "safety": "safe"},
    {"path": "~/Library/Application Support/Microsoft Teams",
     "name": "Microsoft Teams 数据",
     "category": "即时通讯",
     "desc": "Teams 客户端应用数据和缓存，可删除后重新登录，数据存储在云端。",
     "safety": "caution"},

    # ════════════════════════════════════════
    #  云存储 & 同步
    # ════════════════════════════════════════
    {"path": "~/Dropbox",
     "name": "Dropbox 同步文件夹",
     "category": "云存储",
     "desc": "Dropbox 本地同步的文件，请在 Dropbox 设置中选择性同步以减少本地占用，不建议直接删除。",
     "safety": "danger"},
    {"path": "~/Google Drive",
     "name": "Google Drive 本地文件",
     "category": "云存储",
     "desc": "Google Drive 本地镜像文件，请在 Google Drive 客户端设置中管理同步选项，不建议直接删除。",
     "safety": "danger"},
    {"path": "~/Library/CloudStorage",
     "name": "iCloud / 第三方云存储",
     "category": "云存储",
     "desc": "iCloud Drive 及 OneDrive、Box 等云盘的本地同步目录，不建议直接删除，请在对应 App 中管理同步设置。",
     "safety": "danger"},
    {"path": "~/Library/Application Support/com.apple.CloudDocs",
     "name": "iCloud 文稿数据库",
     "category": "云存储",
     "desc": "iCloud Drive 的本地数据库文件，不建议手动删除。",
     "safety": "danger"},

    # ════════════════════════════════════════
    #  视频 & 媒体制作
    # ════════════════════════════════════════
    {"path": "~/Movies/Final Cut Backups",
     "name": "Final Cut Pro 自动备份",
     "category": "媒体制作",
     "desc": "Final Cut Pro 自动创建的项目备份，可删除较旧的备份以释放空间。",
     "safety": "caution"},
    {"path": "~/Movies/Motion Templates.localized",
     "name": "Motion 模板",
     "category": "媒体制作",
     "desc": "Apple Motion / Final Cut Pro 的本地模板文件。",
     "safety": "caution"},
    {"path": "~/Library/Application Support/DaVinci Resolve",
     "name": "DaVinci Resolve 数据",
     "category": "媒体制作",
     "desc": "DaVinci Resolve 视频剪辑软件的数据库和配置文件，请谨慎操作。",
     "safety": "caution"},
    {"path": "~/Library/Caches/com.blackmagic-design.DaVinciResolve",
     "name": "DaVinci Resolve 缓存",
     "category": "媒体制作",
     "desc": "DaVinci Resolve 的渲染和优化缓存，可安全删除，重新打开项目会重建。",
     "safety": "safe"},
    {"path": "~/Library/Application Support/Davinci Resolve/Fusion/Templates",
     "name": "DaVinci Resolve 模板",
     "category": "媒体制作",
     "desc": "DaVinci Resolve 的 Fusion 模板文件。",
     "safety": "caution"},

    # ════════════════════════════════════════
    #  数据库
    # ════════════════════════════════════════
    {"path": "/usr/local/var/mysql",
     "name": "MySQL 数据目录（Intel）",
     "category": "数据库",
     "desc": "MySQL 数据库数据文件，删除将清除所有数据库内容，请务必提前备份！",
     "safety": "danger"},
    {"path": "/opt/homebrew/var/mysql",
     "name": "MySQL 数据目录（Apple Silicon）",
     "category": "数据库",
     "desc": "MySQL 数据库数据文件（Apple Silicon），删除将清除所有数据，请提前备份！",
     "safety": "danger"},
    {"path": "/usr/local/var/postgresql@14",
     "name": "PostgreSQL 数据目录（Intel）",
     "category": "数据库",
     "desc": "PostgreSQL 数据库数据文件，删除将清除所有数据，请提前备份！",
     "safety": "danger"},
    {"path": "/opt/homebrew/var/postgresql@14",
     "name": "PostgreSQL 数据目录（Apple Silicon）",
     "category": "数据库",
     "desc": "PostgreSQL 数据库数据文件（Apple Silicon），删除将清除所有数据，请提前备份！",
     "safety": "danger"},
    {"path": "~/Library/Application Support/DBngin",
     "name": "DBngin 数据库数据",
     "category": "数据库",
     "desc": "DBngin 管理的本地数据库（MySQL / PostgreSQL / Redis），删除将清除所有数据，请提前备份！",
     "safety": "danger"},
    {"path": "~/.redis",
     "name": "Redis 数据文件",
     "category": "数据库",
     "desc": "Redis 的本地持久化数据文件（dump.rdb），删除将清除所有 Redis 数据。",
     "safety": "danger"},
    {"path": "~/.mongodb",
     "name": "MongoDB 用户数据",
     "category": "数据库",
     "desc": "MongoDB 数据库文件，删除将清除所有数据，请提前备份！",
     "safety": "danger"},

    # ════════════════════════════════════════
    #  云服务 CLI 工具
    # ════════════════════════════════════════
    {"path": "~/.aws",
     "name": "AWS CLI 配置 & 缓存",
     "category": "云服务 CLI",
     "desc": "AWS CLI 的凭证、配置文件和 SSO 缓存，删除将清除所有 AWS 凭证，需谨慎。",
     "safety": "danger"},
    {"path": "~/.config/gcloud",
     "name": "Google Cloud SDK 配置",
     "category": "云服务 CLI",
     "desc": "gcloud CLI 的配置文件和认证信息，删除将清除 GCP 登录状态。",
     "safety": "danger"},
    {"path": "~/google-cloud-sdk",
     "name": "Google Cloud SDK",
     "category": "云服务 CLI",
     "desc": "Google Cloud SDK 安装目录，体积约 200–500 MB，可重新安装。",
     "safety": "caution"},
    {"path": "~/.azure",
     "name": "Azure CLI 配置",
     "category": "云服务 CLI",
     "desc": "Azure CLI 的配置和认证信息，删除将清除 Azure 登录状态。",
     "safety": "danger"},
    {"path": "~/.config/op",
     "name": "1Password CLI 缓存",
     "category": "云服务 CLI",
     "desc": "1Password CLI（op）的配置和缓存，可安全删除。",
     "safety": "safe"},

    # ════════════════════════════════════════
    #  其他语言 & 工具链
    # ════════════════════════════════════════
    {"path": "~/.mix",
     "name": "Elixir Mix 依赖",
     "category": "其他语言",
     "desc": "Elixir 包管理器 Mix 的全局依赖和 Hex 包缓存，可安全删除。",
     "safety": "safe"},
    {"path": "~/.hex",
     "name": "Hex 包缓存（Elixir）",
     "category": "其他语言",
     "desc": "Elixir Hex 包管理器的下载缓存，可安全删除（命令：mix hex.info）。",
     "safety": "safe"},
    {"path": "~/.stack",
     "name": "Haskell Stack 工具链",
     "category": "其他语言",
     "desc": "Haskell Stack 管理的 GHC 编译器和依赖，体积可达数 GB。",
     "safety": "caution"},
    {"path": "~/.cabal",
     "name": "Haskell Cabal 包",
     "category": "其他语言",
     "desc": "Haskell Cabal 包管理器的本地依赖存储。",
     "safety": "caution"},
    {"path": "~/.opam",
     "name": "OCaml OPAM 包",
     "category": "其他语言",
     "desc": "OCaml 包管理器 OPAM 的安装目录，包含编译器和所有依赖。",
     "safety": "caution"},
    {"path": "~/.nuget/packages",
     "name": ".NET NuGet 包缓存",
     "category": "其他语言",
     "desc": ".NET / C# NuGet 包管理器的本地缓存，可安全删除（命令：dotnet nuget locals all --clear）。",
     "safety": "safe"},
    {"path": "~/.dotnet",
     "name": ".NET SDK 安装",
     "category": "其他语言",
     "desc": ".NET SDK 安装目录，可删除不再使用的版本。",
     "safety": "caution"},
    {"path": "~/swift-build",
     "name": "Swift Package Manager 构建",
     "category": "其他语言",
     "desc": "Swift Package Manager 的构建产物，可安全删除。",
     "safety": "safe"},
    {"path": "~/.swiftpm",
     "name": "Swift Package Manager 缓存",
     "category": "其他语言",
     "desc": "Swift PM 下载的依赖包缓存，可安全删除。",
     "safety": "safe"},
    {"path": "~/.luarocks",
     "name": "LuaRocks 包",
     "category": "其他语言",
     "desc": "Lua 包管理器 LuaRocks 安装的本地包。",
     "safety": "caution"},
    {"path": "~/.r",
     "name": "R 包库",
     "category": "其他语言",
     "desc": "R 语言安装的本地包库，可删除不再使用的包。",
     "safety": "caution"},

    # ════════════════════════════════════════
    #  系统 & macOS
    # ════════════════════════════════════════
    {"path": "/private/var/vm",
     "name": "虚拟内存 & 休眠镜像",
     "category": "系统",
     "desc": "包含 macOS 休眠镜像（sleepimage，大小等于内存容量）和 swap 交换文件，不建议手动删除，系统自动管理。",
     "safety": "danger"},
    {"path": "/.Spotlight-V100",
     "name": "Spotlight 索引",
     "category": "系统",
     "desc": "Spotlight 搜索索引文件，不建议手动删除，macOS 会在删除后自动重建，重建期间搜索变慢。",
     "safety": "danger"},
    {"path": "~/.Spotlight-V100",
     "name": "用户 Spotlight 索引",
     "category": "系统",
     "desc": "用户目录的 Spotlight 搜索索引，可删除（删除后 macOS 会自动重建）。",
     "safety": "caution"},
    {"path": "/private/var/db/diagnostics",
     "name": "系统诊断日志",
     "category": "系统",
     "desc": "macOS 系统诊断和崩溃日志，需要管理员权限，一般无需手动清理。",
     "safety": "caution"},
    {"path": "~/Library/Fonts",
     "name": "用户字体",
     "category": "系统",
     "desc": "用户手动安装的字体文件，可删除不再使用的字体。",
     "safety": "caution"},
    {"path": "/Library/Fonts",
     "name": "系统字体（第三方）",
     "category": "系统",
     "desc": "系统级别安装的第三方字体，需要管理员权限，可删除不再使用的字体。",
     "safety": "caution"},
    {"path": "~/Library/Application Support/CrashReporter",
     "name": "崩溃报告",
     "category": "系统",
     "desc": "App 崩溃时生成的诊断报告文件，可安全删除。",
     "safety": "safe"},
    {"path": "~/Library/Containers",
     "name": "沙盒应用数据容器",
     "category": "系统",
     "desc": "macOS 沙盒机制为 App Store 应用创建的独立数据容器，包含各 App 的全部数据。请按子目录（App 名）单独处理，不建议整体删除。",
     "safety": "caution"},

    # ════════════════════════════════════════
    #  笔记 & 知识管理
    # ════════════════════════════════════════
    {"path": "~/Library/Application Support/Notion",
     "name": "Notion 桌面缓存",
     "category": "笔记 & 知识",
     "desc": "Notion 桌面客户端的本地缓存，可安全删除，数据存储在云端。",
     "safety": "safe"},
    {"path": "~/.config/obsidian",
     "name": "Obsidian 全局配置",
     "category": "笔记 & 知识",
     "desc": "Obsidian 的全局配置文件（不含笔记内容，内容在各 Vault 目录中）。",
     "safety": "caution"},
    {"path": "~/Library/Application Support/Bear",
     "name": "Bear 笔记数据",
     "category": "笔记 & 知识",
     "desc": "Bear 笔记 App 的本地数据库，不建议直接删除，请在 Bear 内导出备份后处理。",
     "safety": "danger"},
    {"path": "~/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear",
     "name": "Bear 共享数据",
     "category": "笔记 & 知识",
     "desc": "Bear 跨设备共享的笔记数据，不建议直接删除。",
     "safety": "danger"},
    {"path": "~/Library/Caches/io.typora.Typora",
     "name": "Typora 缓存",
     "category": "笔记 & 知识",
     "desc": "Typora Markdown 编辑器缓存，可安全删除。",
     "safety": "safe"},

    # ════════════════════════════════════════
    #  安全 & 开发调试
    # ════════════════════════════════════════
    {"path": "~/Library/Application Support/Charles",
     "name": "Charles 代理数据",
     "category": "安全 & 调试",
     "desc": "Charles HTTP 代理工具保存的会话、SSL 证书等数据。",
     "safety": "caution"},
    {"path": "~/Library/Application Support/Proxyman",
     "name": "Proxyman 数据",
     "category": "安全 & 调试",
     "desc": "Proxyman 网络调试工具的本地数据。",
     "safety": "caution"},
    {"path": "~/.wireshark",
     "name": "Wireshark 配置",
     "category": "安全 & 调试",
     "desc": "Wireshark 网络抓包工具的配置文件，不含抓包文件（.pcap）。",
     "safety": "caution"},
    {"path": "~/Documents/Wireshark",
     "name": "Wireshark 抓包文件",
     "category": "安全 & 调试",
     "desc": "保存的 .pcap / .pcapng 抓包文件，体积可能很大，请手动检查后清理。",
     "safety": "manual"},
    {"path": "~/.gnupg",
     "name": "GnuPG 密钥环",
     "category": "安全 & 调试",
     "desc": "GPG 密钥、信任数据库等，不建议直接删除，会导致已加密数据无法解密。",
     "safety": "danger"},
    {"path": "~/.ssh",
     "name": "SSH 密钥与配置",
     "category": "安全 & 调试",
     "desc": "SSH 密钥对和 known_hosts 文件，不建议直接删除，会导致无法连接已配置的远程服务器。",
     "safety": "danger"},
]


# ════════════════════════════════════════════════════════════════
#  English translations  (path → (name_en, desc_en, category_en))
# ════════════════════════════════════════════════════════════════
TRANSLATIONS_EN: dict[str, tuple[str, str, str]] = {
    # Caches & Logs
    "~/Library/Caches": ("User App Caches", "Temporary cache files generated by apps. Safe to delete — apps regenerate them automatically. Often one of the largest cleanable areas.", "Caches & Logs"),
    "~/Library/Logs": ("User App Logs", "Log files generated by running applications. Safe to delete.", "Caches & Logs"),
    "~/.Trash": ("Trash", "Files deleted but not yet permanently removed. Emptying immediately frees disk space (also via right-click Trash → Empty Trash in Finder).", "Caches & Logs"),
    "~/Library/Saved Application State": ("Saved App Window State", "Stores window positions/state for app resume after quit. Safe to delete — apps won't auto-restore their windows on next launch.", "Caches & Logs"),
    "/Library/Caches": ("System Caches", "macOS system-level cache files. Requires admin privileges; use system tools to clean.", "Caches & Logs"),
    "/private/var/log": ("System Logs", "macOS system runtime logs. Requires admin privileges; generally no manual cleaning needed.", "Caches & Logs"),
    "/private/var/folders": ("System Temp Folders", "Temporary directories macOS creates per user/process (TMPDIR). System-managed — do not delete manually.", "Caches & Logs"),
    "/private/tmp": ("System /tmp Directory", "System temp files — auto-cleared on reboot. Do not delete manually.", "Caches & Logs"),
    # Apple Development
    "~/Library/Developer/Xcode/DerivedData": ("Xcode Derived Data", "Intermediate build artifacts from Xcode. Usually very large (can be tens of GB). Safe to delete — Xcode rebuilds on next build.", "Apple Development"),
    "~/Library/Developer/CoreSimulator/Caches": ("iOS Simulator Caches", "Runtime caches for iOS simulators. Safe to delete.", "Apple Development"),
    "~/Library/Caches/CocoaPods": ("CocoaPods Cache", "Download cache for CocoaPods dependency manager. Safe to delete (run: pod cache clean --all).", "Apple Development"),
    "~/.cocoapods/repos": ("CocoaPods Spec Repo", "CocoaPods spec repository index — can be hundreds of MB. Safe to delete; re-fetched on next pod install.", "Apple Development"),
    "~/Library/Developer/Xcode/Archives": ("Xcode Archives", "App Store build archives (.xcarchive). Delete old versions if already uploaded or backed up.", "Apple Development"),
    "~/Library/Developer/Xcode/iOS DeviceSupport": ("Xcode iOS Device Support", "Debug symbols downloaded when connecting a real device. Delete files for iOS versions no longer in use.", "Apple Development"),
    "~/Library/Developer/Xcode/watchOS DeviceSupport": ("Xcode watchOS Device Support", "Apple Watch debugging support files. Delete unused versions.", "Apple Development"),
    "~/Library/Developer/CoreSimulator/Devices": ("iOS Simulator Device Images", "iOS/iPadOS simulator images — each device can be several GB. Manage in Xcode → Window → Devices and Simulators.", "Apple Development"),
    "~/Library/Developer/Xcode/UserData/Previews": ("SwiftUI Preview Cache", "Cache generated by Xcode SwiftUI Canvas previews. Safe to delete.", "Apple Development"),
    "~/Library/Application Support/MobileSync/Backup": ("iPhone / iPad Local Backups", "iOS device backups created via Finder or iTunes — each can be tens of GB. Safe to delete if iCloud backup is on or old backups are no longer needed.", "Apple Development"),
    # Node.js / Frontend
    "~/.npm/_cacache": ("npm Cache", "npm package manager cache. Safe to delete (run: npm cache clean --force).", "Node.js / Frontend"),
    "~/.yarn/cache": ("Yarn Cache", "Yarn package manager cache. Safe to delete (run: yarn cache clean).", "Node.js / Frontend"),
    "~/.pnpm-store": ("pnpm Global Store", "pnpm global package store. Safe to delete — re-downloaded on next install (run: pnpm store prune).", "Node.js / Frontend"),
    "~/.nvm": ("nvm Node.js Versions", "All Node.js versions managed by nvm. Delete unused versions (run: nvm uninstall <version>).", "Node.js / Frontend"),
    "~/.volta": ("Volta Toolchain", "Node.js / npm / Yarn versions managed by Volta. Delete unused tool versions.", "Node.js / Frontend"),
    "~/.bun": ("Bun Runtime", "Bun JavaScript runtime installation directory and cache.", "Node.js / Frontend"),
    "~/.deno": ("Deno Cache", "Deno runtime cache and installed modules. Safe to delete — re-downloaded when needed.", "Node.js / Frontend"),
    # Python
    "~/Library/Caches/pip": ("pip Download Cache", "pip package manager download cache. Safe to delete (run: pip cache purge).", "Python"),
    "~/.cache/pip": ("pip Cache (.cache)", "pip cache stored under ~/.cache. Safe to delete.", "Python"),
    "~/.pyenv/versions": ("pyenv Python Versions", "Multiple Python versions managed by pyenv. Delete unused versions (run: pyenv uninstall <version>).", "Python"),
    "~/opt/anaconda3": ("Anaconda3 Distribution", "Full Anaconda Python distribution including all conda environments — usually several to tens of GB.", "Python"),
    "~/opt/miniconda3": ("Miniconda3", "Minimal Conda environment manager including all created virtual environments.", "Python"),
    "~/miniconda3": ("Miniconda3 (Home Install)", "Miniconda installed at ~/miniconda3.", "Python"),
    "~/anaconda3": ("Anaconda3 (Home Install)", "Anaconda installed at ~/anaconda3.", "Python"),
    "~/.conda/pkgs": ("Conda Package Cache", "Conda downloaded package cache. Safe to delete (run: conda clean --all).", "Python"),
    "~/.jupyter": ("Jupyter Config & Cache", "Jupyter Notebook / Lab configuration, kernel info and runtime data.", "Python"),
    # Java / JVM
    "~/.gradle/caches": ("Gradle Dependency Cache", "Gradle build system dependency cache for Android / Java / Kotlin. Safe to delete — re-downloaded on next build.", "Java / JVM"),
    "~/.gradle/wrapper": ("Gradle Wrapper Downloads", "Downloaded Gradle build tool archives. Delete unused versions.", "Java / JVM"),
    "~/.m2/repository": ("Maven Local Repository", "Maven local dependency cache. Safe to delete — re-downloaded on next build.", "Java / JVM"),
    "~/Library/Java/JavaVirtualMachines": ("Installed JDKs", "JDKs installed via Homebrew / SDKMAN / official installer. Delete unused versions (~300–600 MB each).", "Java / JVM"),
    "~/.sdkman": ("SDKMAN Toolchain", "Java / Kotlin / Groovy / Scala SDKs managed by SDKMAN.", "Java / JVM"),
    "~/.ivy2/cache": ("Ivy / SBT Cache", "Scala SBT / Apache Ivy dependency cache. Safe to delete.", "Java / JVM"),
    "~/.sbt": ("SBT Config & Cache", "Scala build tool SBT configuration and launcher files.", "Java / JVM"),
    # Go
    "~/go/pkg/mod": ("Go Module Cache", "Go module dependency cache (GOPATH/pkg/mod). Safe to delete (run: go clean -modcache).", "Go"),
    "~/Library/Caches/go-build": ("Go Build Cache", "Go compiler build cache. Safe to delete (run: go clean -cache) — rebuilt on next compile.", "Go"),
    "~/.cache/go-build": ("Go Build Cache (.cache)", "Go compiler build cache under ~/.cache. Safe to delete.", "Go"),
    # Rust
    "~/.cargo/registry": ("Cargo Registry Cache", "Rust Cargo crates.io source cache. Safe to delete (run: cargo cache -a).", "Rust"),
    "~/.cargo/git": ("Cargo Git Dependencies", "Cargo git repository dependency cache. Safe to delete.", "Rust"),
    "~/.rustup/toolchains": ("Rustup Toolchains", "Rust toolchain versions managed by rustup. Delete unused versions (run: rustup toolchain uninstall <name>).", "Rust"),
    # Flutter / Dart
    "~/.pub-cache": ("Dart / Flutter pub Cache", "Global Dart pub package manager cache. Safe to delete (run: dart pub cache clean).", "Flutter / Dart"),
    "~/flutter": ("Flutter SDK", "Flutter SDK installation including toolchain and framework source. Delete old versions.", "Flutter / Dart"),
    "~/fvm/versions": ("FVM Flutter Versions", "Multiple Flutter versions managed by FVM. Delete unused versions.", "Flutter / Dart"),
    "~/.flutter": ("Flutter Global Config", "Flutter toolchain global configuration and cache.", "Flutter / Dart"),
    # Ruby
    "~/.gem": ("Ruby Gems", "Globally installed Ruby gems. Delete unused packages (run: gem cleanup).", "Ruby"),
    "~/.bundle/cache": ("Bundler Cache", "Ruby Bundler gem download cache. Safe to delete.", "Ruby"),
    "~/.rbenv/versions": ("rbenv Ruby Versions", "Multiple Ruby versions managed by rbenv. Delete unused versions.", "Ruby"),
    "~/.rvm": ("RVM Ruby Versions", "Ruby versions and gemsets managed by RVM — can be several GB.", "Ruby"),
    # PHP
    "~/.composer/cache": ("Composer Cache", "PHP Composer dependency manager download cache. Safe to delete (run: composer clear-cache).", "PHP"),
    # Android
    "~/Library/Android/sdk": ("Android SDK", "Full Android SDK installation including platform tools — typically several to tens of GB.", "Android Development"),
    "~/.android/avd": ("Android Virtual Devices (AVD)", "Android emulator images — each device can be several GB. Manage in Android Studio AVD Manager.", "Android Development"),
    "~/.android/cache": ("Android Tool Cache", "Android build tool cache data. Safe to delete.", "Android Development"),
    # Other Dev Tools
    "~/Library/Caches/Homebrew": ("Homebrew Download Cache", "Homebrew package download cache. Safe to delete (run: brew cleanup).", "Other Dev Tools"),
    "~/.cache": ("User .cache Directory", "Linux-compatible user cache directory — typically contains pip, Go, and other tool caches. Safe to delete.", "Other Dev Tools"),
    "~/.asdf/installs": ("asdf Version Manager", "Multi-language versions managed by asdf (Node / Python / Ruby / Go…). Delete unused versions.", "Other Dev Tools"),
    "~/.terraform.d/plugins": ("Terraform Plugin Cache", "Terraform provider plugin cache. Safe to delete — re-downloaded on terraform init.", "Other Dev Tools"),
    "~/.minikube": ("Minikube Local K8s", "Minikube local Kubernetes cluster data and images — usually large.", "Other Dev Tools"),
    "~/.kube/cache": ("kubectl Cache", "kubectl API discovery cache. Safe to delete.", "Other Dev Tools"),
    "~/.helm": ("Helm Config & Cache", "Kubernetes Helm package manager config and chart repo cache. Safe to delete.", "Other Dev Tools"),
    "~/Library/Containers/com.docker.docker": ("Docker Desktop Data", "Docker Desktop container, image and volume data. Deleting removes ALL local images — use with extreme caution!", "Other Dev Tools"),
    "/opt/homebrew/Cellar": ("Homebrew Packages (Apple Silicon)", "Software installed by Homebrew. Do not delete directly. Use brew uninstall <name> to remove, brew cleanup for old versions.", "Other Dev Tools"),
    "/usr/local/Cellar": ("Homebrew Packages (Intel)", "Homebrew package directory for Intel Macs. Do not delete directly.", "Other Dev Tools"),
    # IDEs & Editors
    "~/.vscode/extensions": ("VS Code Extensions", "Installed VS Code extensions. Delete unused ones (safer via VS Code Extensions panel).", "IDEs & Editors"),
    "~/Library/Caches/JetBrains": ("JetBrains IDE Caches", "Cache for IntelliJ IDEA / PyCharm / WebStorm etc. Safe to delete — IDEs rebuild automatically.", "IDEs & Editors"),
    "~/Library/Application Support/JetBrains": ("JetBrains IDE Config", "JetBrains IDE config, plugins and logs — can be several GB. Back up important configs before deleting.", "IDEs & Editors"),
    "~/Library/Logs/JetBrains": ("JetBrains IDE Logs", "JetBrains IDE runtime logs. Safe to delete.", "IDEs & Editors"),
    "~/.config/Code/Cache": ("VS Code Content Cache", "VS Code page cache. Safe to delete.", "IDEs & Editors"),
    # Design Tools
    "~/Library/Application Support/Adobe": ("Adobe App Data", "App data for Photoshop / Illustrator / Premiere and other Adobe apps — usually very large.", "Design Tools"),
    "~/Library/Caches/Adobe": ("Adobe Caches", "Adobe software cache files. Safe to delete — rebuilt when apps are used.", "Design Tools"),
    "~/Library/Application Support/com.bohemiancoding.sketch3": ("Sketch App Data", "Sketch design tool data including plugins and auto-backups.", "Design Tools"),
    "~/Library/Application Support/Figma": ("Figma Desktop Cache", "Figma desktop client local cache and data. Safe to clean.", "Design Tools"),
    # Gaming & Entertainment
    "~/Library/Application Support/Steam": ("Steam Game Library", "Steam platform client data and installed games. Deleting frees large space but games must be re-downloaded.", "Gaming & Entertainment"),
    "~/Library/Application Support/Riot Games": ("Riot Games Data", "Game data for League of Legends and other Riot titles. Deleting requires reinstalling games.", "Gaming & Entertainment"),
    "~/Library/Caches/com.spotify.client": ("Spotify Cache", "Spotify client music cache. Safe to delete — Spotify re-caches as needed.", "Gaming & Entertainment"),
    "~/Library/Application Support/Spotify": ("Spotify App Data", "Spotify local storage including cache and configuration.", "Gaming & Entertainment"),
    # Personal Files
    "~/Downloads": ("Downloads Folder", "All downloaded content. Consider cleaning up .dmg / .pkg / .zip installers you no longer need — these are often large.", "Personal Files"),
    "~/Desktop": ("Desktop", "Files on your desktop. Review and clean up manually.", "Personal Files"),
    "~/Movies": ("Movies Folder", "Video files — usually large. Review and clean up manually.", "Personal Files"),
    "~/Music": ("Music Folder", "Music and podcast files. Check for local audio you no longer need.", "Personal Files"),
    "~/Music/Music/Media.localized": ("Apple Music Local Media", "Local music files managed by the Music app. Manage inside the Music app.", "Personal Files"),
    "~/Pictures": ("Pictures Folder", "Photos and images. Consider using iCloud Photos to reduce local storage.", "Personal Files"),
    "~/Documents": ("Documents Folder", "Document files. Review and clean up manually.", "Personal Files"),
    "~/Library/Mobile Documents": ("iCloud Drive Local Cache", "Files synced locally from iCloud Drive. Manage in Finder or iCloud settings — do not delete directly.", "Personal Files"),
    # App Data
    "~/Library/Application Support": ("App Support Data", "Config files and databases for all apps. Deleting a specific app subfolder may erase its settings — proceed with caution.", "App Data"),
    "~/Library/Mail": ("Apple Mail Database", "Apple Mail local message store — can be several GB. Manage inside the Mail app; do not delete directly.", "App Data"),
    "~/Library/Messages": ("iMessage History", "All iMessage and SMS history. Manage inside the Messages app; do not delete directly.", "App Data"),
    "~/Pictures/Photos Library.photoslibrary": ("Photos Library", "System photo library — may be very large. Manage in the Photos app or enable iCloud Photos to optimize local storage.", "App Data"),
    "~/Library/Containers/com.apple.Safari": ("Safari Browser Data", "Safari history, bookmarks, passwords etc. Manage in Safari Preferences; do not delete directly.", "App Data"),
    # Virtual Machines
    "~/Virtual Machines.localized": ("VMware Fusion VMs", "VMware Fusion virtual machine files — usually extremely large. Delete VMs you no longer use.", "Virtual Machines"),
    "~/Parallels": ("Parallels Desktop VMs", "Parallels Desktop virtual machine files. Delete VMs you no longer need.", "Virtual Machines"),
    "~/.vagrant.d/boxes": ("Vagrant Box Images", "Vagrant VM images. Delete unused boxes (run: vagrant box remove <name>).", "Virtual Machines"),
    "~/.local/share/containers": ("Podman Container Data", "Podman container engine data (daemonless Docker alternative). Deleting removes all images.", "Virtual Machines"),
    # AI / ML
    "~/.ollama/models": ("Ollama Local Models", "Local LLM files downloaded by Ollama (llama, mistral, etc.) — each model is 2–70 GB. Delete unused (run: ollama rm <model>).", "AI / ML"),
    "~/Library/Application Support/LM Studio": ("LM Studio App Data", "LM Studio application data. Manage model files inside LM Studio.", "AI / ML"),
    "~/.cache/huggingface": ("Hugging Face Model Cache", "Pre-trained models downloaded via transformers / diffusers — each can be GB to tens of GB. Delete unused models.", "AI / ML"),
    "~/.cache/torch": ("PyTorch Model Cache", "Pre-trained models from PyTorch Hub. Safe to delete — re-downloaded when needed.", "AI / ML"),
    "~/.keras": ("Keras / TensorFlow Cache", "Pre-trained weights and dataset cache from Keras. Safe to delete — re-downloaded when needed.", "AI / ML"),
    "~/Library/Application Support/nomic.ai/GPT4All": ("GPT4All Local Models", "GPT4All downloaded local model files — usually very large. Delete unused models.", "AI / ML"),
    "~/.cache/kaggle": ("Kaggle Dataset Cache", "Datasets downloaded via the Kaggle API. Safe to delete.", "AI / ML"),
    # Browsers
    "~/Library/Caches/Google/Chrome": ("Chrome Cache", "Google Chrome browser cache. Safe to delete (also via Chrome Settings → Clear browsing data).", "Browsers"),
    "~/Library/Application Support/Google/Chrome": ("Chrome User Data", "Chrome user config, bookmarks, history, passwords etc. Manage inside Chrome; do not delete directly.", "Browsers"),
    "~/Library/Caches/Firefox": ("Firefox Cache", "Firefox browser cache. Safe to delete (also via Firefox Settings → Privacy).", "Browsers"),
    "~/Library/Application Support/Firefox/Profiles": ("Firefox Profiles", "Firefox bookmarks, history, passwords etc. Manage inside Firefox; do not delete directly.", "Browsers"),
    "~/Library/Caches/com.microsoft.edgemac": ("Edge Cache", "Microsoft Edge browser cache. Safe to delete.", "Browsers"),
    "~/Library/Application Support/BraveSoftware/Brave-Browser": ("Brave User Data", "Brave browser user data. Manage inside Brave; do not delete directly.", "Browsers"),
    "~/Library/Application Support/Arc": ("Arc Browser Data", "Arc browser application data. Do not delete directly.", "Browsers"),
    # Messaging
    "~/Library/Application Support/Slack": ("Slack App Data", "Slack desktop client local cache and data. Delete to free space — re-downloaded on next login.", "Messaging"),
    "~/Library/Caches/com.tinyspeck.slackmacgap": ("Slack Cache", "Slack client cache files. Safe to delete.", "Messaging"),
    "~/Library/Application Support/zoom.us": ("Zoom App Data", "Zoom meeting client data including recordings. Review manually.", "Messaging"),
    "~/Documents/Zoom": ("Zoom Recordings", "Locally recorded Zoom meeting videos — can be very large. Check if you still need them.", "Messaging"),
    "~/Library/Application Support/discord": ("Discord App Data", "Discord client local data and cache. Safe to delete — re-downloaded on restart.", "Messaging"),
    "~/Library/Caches/com.hnc.Discord": ("Discord Cache", "Discord cache files. Safe to delete.", "Messaging"),
    "~/Library/Containers/com.tencent.xinWeChat": ("WeChat Data", "WeChat chat history, files and images — can be tens of GB. Manage inside WeChat; do not delete directly.", "Messaging"),
    "~/Library/Application Support/WeChat": ("WeChat App Data (Legacy)", "Legacy WeChat app data. Review manually.", "Messaging"),
    "~/Library/Application Support/TelegramDesktop": ("Telegram App Data", "Telegram desktop client local cache and media. Safe to delete — messages stored in the cloud.", "Messaging"),
    "~/Library/Application Support/Microsoft Teams": ("Microsoft Teams Data", "Teams client app data and cache. Delete and re-login — data stored in the cloud.", "Messaging"),
    # Cloud Storage
    "~/Dropbox": ("Dropbox Sync Folder", "Locally synced Dropbox files. Use Selective Sync in Dropbox settings to reduce local storage — do not delete directly.", "Cloud Storage"),
    "~/Google Drive": ("Google Drive Local Files", "Google Drive local mirror. Manage sync options in the Google Drive client — do not delete directly.", "Cloud Storage"),
    "~/Library/CloudStorage": ("iCloud & 3rd-Party Cloud", "Local sync directories for iCloud Drive, OneDrive, Box etc. Manage sync settings in each app — do not delete directly.", "Cloud Storage"),
    "~/Library/Application Support/com.apple.CloudDocs": ("iCloud Documents Database", "iCloud Drive local database files. Do not delete manually.", "Cloud Storage"),
    # Media Production
    "~/Movies/Final Cut Backups": ("Final Cut Pro Auto-Backups", "Automatic project backups created by Final Cut Pro. Delete older backups to free space.", "Media Production"),
    "~/Movies/Motion Templates.localized": ("Motion Templates", "Local templates for Apple Motion / Final Cut Pro.", "Media Production"),
    "~/Library/Application Support/DaVinci Resolve": ("DaVinci Resolve Data", "DaVinci Resolve video editor database and config files. Handle with care.", "Media Production"),
    "~/Library/Caches/com.blackmagic-design.DaVinciResolve": ("DaVinci Resolve Cache", "DaVinci Resolve render and optimized media cache. Safe to delete — rebuilt when projects are opened.", "Media Production"),
    "~/Library/Application Support/Davinci Resolve/Fusion/Templates": ("DaVinci Resolve Templates", "DaVinci Resolve Fusion template files.", "Media Production"),
    # Databases
    "/usr/local/var/mysql": ("MySQL Data (Intel)", "MySQL database data files. Deleting erases ALL databases — always back up first!", "Databases"),
    "/opt/homebrew/var/mysql": ("MySQL Data (Apple Silicon)", "MySQL database data files. Deleting erases ALL data — back up first!", "Databases"),
    "/usr/local/var/postgresql@14": ("PostgreSQL Data (Intel)", "PostgreSQL database data files. Deleting erases ALL data — back up first!", "Databases"),
    "/opt/homebrew/var/postgresql@14": ("PostgreSQL Data (Apple Silicon)", "PostgreSQL data files. Deleting erases ALL data — back up first!", "Databases"),
    "~/Library/Application Support/DBngin": ("DBngin Database Data", "Local databases managed by DBngin (MySQL / PostgreSQL / Redis). Deleting erases ALL data — back up first!", "Databases"),
    "~/.redis": ("Redis Data File", "Redis local persistence file (dump.rdb). Deleting erases all Redis data.", "Databases"),
    "~/.mongodb": ("MongoDB Data", "MongoDB database files. Deleting erases all data — back up first!", "Databases"),
    # Cloud Service CLIs
    "~/.aws": ("AWS CLI Config & Cache", "AWS CLI credentials, config and SSO cache. Deleting removes all AWS credentials — handle with care.", "Cloud Service CLIs"),
    "~/.config/gcloud": ("Google Cloud SDK Config", "gcloud CLI config and auth tokens. Deleting removes GCP login state.", "Cloud Service CLIs"),
    "~/google-cloud-sdk": ("Google Cloud SDK", "Google Cloud SDK installation (~200–500 MB). Can be re-installed.", "Cloud Service CLIs"),
    "~/.azure": ("Azure CLI Config", "Azure CLI config and auth tokens. Deleting removes Azure login state.", "Cloud Service CLIs"),
    "~/.config/op": ("1Password CLI Cache", "1Password CLI (op) config and cache. Safe to delete.", "Cloud Service CLIs"),
    # Other Languages
    "~/.mix": ("Elixir Mix Dependencies", "Elixir Mix global dependencies and Hex package cache. Safe to delete.", "Other Languages"),
    "~/.hex": ("Hex Package Cache (Elixir)", "Elixir Hex package manager download cache. Safe to delete.", "Other Languages"),
    "~/.stack": ("Haskell Stack Toolchain", "Haskell Stack-managed GHC compiler and dependencies — can be several GB.", "Other Languages"),
    "~/.cabal": ("Haskell Cabal Packages", "Haskell Cabal package manager local dependency store.", "Other Languages"),
    "~/.opam": ("OCaml OPAM Packages", "OCaml OPAM package manager install directory, including compiler and all dependencies.", "Other Languages"),
    "~/.nuget/packages": (".NET NuGet Package Cache", ".NET / C# NuGet local package cache. Safe to delete (run: dotnet nuget locals all --clear).", "Other Languages"),
    "~/.dotnet": (".NET SDK Install", ".NET SDK installation directory. Delete unused versions.", "Other Languages"),
    "~/swift-build": ("Swift PM Build Artifacts", "Swift Package Manager build artifacts. Safe to delete.", "Other Languages"),
    "~/.swiftpm": ("Swift PM Cache", "Swift PM downloaded dependency cache. Safe to delete.", "Other Languages"),
    "~/.luarocks": ("LuaRocks Packages", "Lua package manager locally installed packages.", "Other Languages"),
    "~/.r": ("R Package Library", "R language locally installed package library. Delete unused packages.", "Other Languages"),
    # Security & Debugging
    "~/Library/Application Support/Charles": ("Charles Proxy Data", "Charles HTTP proxy saved sessions, SSL certificates and config.", "Security & Debugging"),
    "~/Library/Application Support/Proxyman": ("Proxyman Data", "Proxyman network debugging tool local data.", "Security & Debugging"),
    "~/.wireshark": ("Wireshark Config", "Wireshark network capture tool config (does not include capture files).", "Security & Debugging"),
    "~/Documents/Wireshark": ("Wireshark Capture Files", "Saved .pcap / .pcapng capture files — can be very large. Review manually.", "Security & Debugging"),
    "~/.gnupg": ("GnuPG Keyring", "GPG keys and trust database. Do not delete — encrypted data will become inaccessible.", "Security & Debugging"),
    "~/.ssh": ("SSH Keys & Config", "SSH key pairs and known_hosts. Do not delete — remote server connections will break.", "Security & Debugging"),
    # Notes & Knowledge
    "~/Library/Application Support/Notion": ("Notion Desktop Cache", "Notion desktop client local cache. Safe to delete — data stored in the cloud.", "Notes & Knowledge"),
    "~/.config/obsidian": ("Obsidian Global Config", "Obsidian global configuration (not note content, which is in your Vault folders).", "Notes & Knowledge"),
    "~/Library/Application Support/Bear": ("Bear Notes Data", "Bear notes app local database. Do not delete directly — export a backup inside Bear first.", "Notes & Knowledge"),
    "~/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear": ("Bear Shared Data", "Bear cross-device shared notes data. Do not delete directly.", "Notes & Knowledge"),
    "~/Library/Caches/io.typora.Typora": ("Typora Cache", "Typora Markdown editor cache. Safe to delete.", "Notes & Knowledge"),
    # System
    "/private/var/vm": ("Virtual Memory & Hibernate Image", "Contains the macOS hibernate image (sleepimage = RAM size) and swap files. System-managed — do not delete manually.", "System"),
    "/.Spotlight-V100": ("Spotlight Index", "Spotlight search index. Do not delete — macOS auto-rebuilds, but search will be slow during rebuild.", "System"),
    "~/.Spotlight-V100": ("User Spotlight Index", "Spotlight index for user directory. Can be deleted — macOS auto-rebuilds.", "System"),
    "/private/var/db/diagnostics": ("System Diagnostics Logs", "macOS system diagnostics and crash logs. Requires admin privileges; generally no cleaning needed.", "System"),
    "~/Library/Fonts": ("User Fonts", "Manually installed user fonts. Delete unused font files.", "System"),
    "/Library/Fonts": ("System Fonts (Third-Party)", "System-level third-party fonts. Requires admin privileges. Delete unused fonts.", "System"),
    "~/Library/Application Support/CrashReporter": ("Crash Reports", "App crash diagnostic reports. Safe to delete.", "System"),
    "~/Library/Containers": ("Sandboxed App Data Containers", "Isolated data containers created by macOS sandboxing for App Store apps. Handle each app's subfolder individually — do not delete the entire directory.", "System"),
}


def get_dir_size_bytes(path: str):
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return None
    try:
        result = subprocess.run(
            ["du", "-sk", expanded],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return int(result.stdout.split("\t")[0]) * 1024
    except Exception:
        pass
    return 0


def get_disk_info():
    try:
        r = subprocess.run(["df", "-k", "/"], capture_output=True, text=True)
        parts = r.stdout.strip().split("\n")[1].split()
        total = int(parts[1]) * 1024
        used  = int(parts[2]) * 1024
        avail = int(parts[3]) * 1024
        return {"total": total, "used": used, "available": avail}
    except Exception:
        return {"total": 0, "used": 0, "available": 0}


def fmt(n, lang="zh"):
    missing = "不存在" if lang == "zh" else "Not found"
    if n is None:
        return missing
    if n == 0:      return "0 B"
    if n < 1024**2: return f"{n/1024:.0f} KB"
    if n < 1024**3: return f"{n/1024**2:.1f} MB"
    return f"{n/1024**3:.2f} GB"


def browse_dir(path: str):
    """列出目录的直接子项及各自大小，按大小降序"""
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return None, "路径不存在"
    if not os.path.isdir(expanded):
        return None, "不是目录"
    try:
        children = sorted(os.scandir(expanded), key=lambda e: e.name)
    except PermissionError:
        return None, "权限不足，无法读取此目录"

    results = []
    for entry in children:
        try:
            if entry.name.startswith('.') and entry.name not in ('.Trash',):
                is_hidden = True
            else:
                is_hidden = False
            size = get_dir_size_bytes(entry.path)
            results.append({
                "name":      entry.name,
                "path":      entry.path,
                "is_dir":    entry.is_dir(follow_symlinks=False),
                "is_hidden": is_hidden,
                "size":      size,
                "size_formatted": fmt(size, "en"),
            })
        except Exception:
            pass

    results.sort(key=lambda x: x["size"] if x["size"] is not None else 0, reverse=True)
    return results, None


def open_in_finder(path: str):
    """在 Finder 中打开路径"""
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return False, "路径不存在"
    try:
        subprocess.Popen(["open", expanded])
        return True, "已在 Finder 中打开"
    except Exception as e:
        return False, str(e)


def move_to_trash(path: str):
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return False, "路径不存在"
    try:
        script = f'tell application "Finder" to delete POSIX file "{expanded}"'
        r = subprocess.run(["osascript", "-e", script],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return True, "✅ 已移入废纸篓"
        return False, r.stderr.strip() or "操作失败"
    except Exception as e:
        return False, str(e)


def enrich_item(cfg: dict, size):
    name_en, desc_en, category_en = TRANSLATIONS_EN.get(
        cfg["path"],
        (cfg["name"], cfg["desc"], cfg["category"])
    )
    return {
        **cfg,
        "name_en": name_en,
        "desc_en": desc_en,
        "category_en": category_en,
        "size": size,
        "size_formatted": fmt(size, "en"),
        "exists": size is not None,
        "real_path": os.path.expanduser(cfg["path"]),
    }


HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mac Disk Space Analyzer</title>
<style>
  :root {
    --bg:#0f1117;--card:#1a1d27;--card2:#20232f;--border:#2e3140;
    --text:#e2e4ef;--sub:#8b8fa8;--accent:#5b8ef0;
    --safe:#34d399;--caution:#fbbf24;--danger:#f87171;--manual:#a78bfa;
    --radius:12px;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--text);font-family:-apple-system,"PingFang SC",sans-serif;min-height:100vh}

  header{background:var(--card);border-bottom:1px solid var(--border);padding:16px 26px;display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:10}
  .logo{width:38px;height:38px;background:linear-gradient(135deg,#1e2235,#2a2f4a);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}
  header h1{font-size:18px;font-weight:700}
  header p{font-size:12px;color:var(--sub);margin-top:1px}
  .lang-switch{margin-left:auto;display:flex;align-items:center;gap:6px}
  .lang-btn{background:var(--card2);border:1px solid var(--border);color:var(--sub);border-radius:8px;padding:7px 10px;font-size:12px;cursor:pointer}
  .lang-btn.active{border-color:var(--accent);color:var(--text);background:rgba(91,142,240,.15)}
  .scan-btn{margin-left:auto;background:var(--accent);color:#fff;border:none;border-radius:8px;padding:9px 20px;font-size:13px;font-weight:600;cursor:pointer;transition:opacity .2s;white-space:nowrap}
  .scan-btn:hover{opacity:.85}.scan-btn:disabled{opacity:.4;cursor:not-allowed}

  #disk-section{padding:20px 26px 0}
  .disk-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:18px 22px}
  .disk-header{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px}
  .disk-title{font-size:14px;font-weight:600}
  .bar-wrap{background:var(--border);border-radius:6px;height:10px;overflow:hidden}
  .bar-fill{height:100%;border-radius:6px;transition:width .9s ease;background:linear-gradient(90deg,var(--accent),#a78bfa)}
  .disk-stats{display:flex;gap:24px;margin-top:12px;flex-wrap:wrap}
  .stat{font-size:13px}.stat span{color:var(--sub)}

  #filters{padding:16px 26px 0;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  .filter-btn{background:var(--card);border:1px solid var(--border);color:var(--sub);padding:5px 14px;border-radius:20px;font-size:12px;cursor:pointer;transition:all .15s}
  .filter-btn:hover,.filter-btn.active{background:var(--accent);border-color:var(--accent);color:#fff}
  .filter-sep{flex:1;min-width:12px}
  .sort-wrap{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--sub)}
  .sort-wrap select{background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:4px 8px;font-size:12px;cursor:pointer}

  #summary{padding:12px 26px 0;font-size:12px;color:var(--sub)}

  #legend{padding:10px 26px 0;display:flex;gap:14px;flex-wrap:wrap}
  .leg{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--sub)}
  .leg-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}

  #filters2{padding:8px 26px 0;display:flex;gap:7px;flex-wrap:wrap;align-items:center}
  .safety-btn{background:var(--card);border:1px solid var(--border);color:var(--sub);padding:4px 12px;border-radius:20px;font-size:12px;cursor:pointer;transition:all .15s;white-space:nowrap}
  .safety-btn:hover{border-color:#555}
  .safety-btn.active{border-color:var(--accent);color:var(--text);background:rgba(91,142,240,.12)}
  .search-wrap{display:flex;align-items:center;background:var(--card);border:1px solid var(--border);border-radius:8px;overflow:hidden;min-width:200px}
  .search-wrap:focus-within{border-color:var(--accent)}
  #searchBox{background:transparent;border:none;outline:none;color:var(--text);font-size:12px;padding:5px 10px;flex:1;min-width:0}
  #searchBox::placeholder{color:var(--sub)}
  .clear-btn{background:transparent;border:none;color:var(--sub);cursor:pointer;padding:4px 8px;font-size:12px;line-height:1;transition:color .15s}
  .clear-btn:hover{color:var(--text)}

  #loading{display:none;padding:60px 26px;text-align:center;color:var(--sub);font-size:14px}
  .spinner{width:34px;height:34px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 14px}
  @keyframes spin{to{transform:rotate(360deg)}}

  #grid{padding:16px 26px 48px;display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}
  .card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:15px 17px;display:flex;flex-direction:column;gap:9px;transition:border-color .2s}
  .card:hover{border-color:#444766}

  .card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
  .card-info{flex:1;min-width:0}
  .card-name{font-size:14px;font-weight:600;display:flex;align-items:center;gap:6px}
  .card-cat{font-size:10px;background:rgba(91,142,240,.15);color:var(--accent);padding:1px 7px;border-radius:10px;font-weight:500;flex-shrink:0}
  .card-path{font-size:10px;color:var(--sub);margin-top:3px;word-break:break-all;font-family:"SF Mono",monospace;opacity:.8}
  .card-size{font-size:19px;font-weight:700;flex-shrink:0}
  .card-size.na{font-size:12px;color:var(--sub);font-weight:400;margin-top:4px}

  .card-desc{font-size:12px;color:var(--sub);line-height:1.55}

  .card-footer{display:flex;align-items:center;justify-content:space-between;gap:8px}
  .badge{font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px;white-space:nowrap}
  .badge-safe{background:rgba(52,211,153,.15);color:var(--safe)}
  .badge-caution{background:rgba(251,191,36,.15);color:var(--caution)}
  .badge-danger{background:rgba(248,113,113,.15);color:var(--danger)}
  .badge-manual{background:rgba(167,139,250,.15);color:var(--manual)}

  .mini-bar-wrap{flex:1;background:var(--border);border-radius:3px;height:3px;overflow:hidden}
  .mini-bar-fill{height:100%;border-radius:3px;background:var(--accent);transition:width .9s ease}

  .open-btn,.drill-card-btn{background:rgba(91,142,240,.1);border:1px solid rgba(91,142,240,.2);border-radius:7px;padding:4px 8px;font-size:13px;cursor:pointer;transition:all .15s;line-height:1}
  .open-btn:hover,.drill-card-btn:hover{background:rgba(91,142,240,.25)}
  .del-btn{background:rgba(248,113,113,.1);color:var(--danger);border:1px solid rgba(248,113,113,.2);border-radius:7px;padding:4px 12px;font-size:11px;font-weight:600;cursor:pointer;transition:all .15s;white-space:nowrap}
  .del-btn:hover{background:rgba(248,113,113,.22)}
  .del-btn:disabled{opacity:.3;cursor:not-allowed}
  .del-btn.gone{background:rgba(52,211,153,.1);color:var(--safe);border-color:rgba(52,211,153,.2);cursor:default}

  #empty{display:none;padding:50px 26px;text-align:center;color:var(--sub);font-size:13px}

  /* ── 下钻面板 ── */
  #drill-overlay{position:fixed;inset:0;background:rgba(0,0,0,.55);backdrop-filter:blur(4px);z-index:900;display:flex;justify-content:flex-end}
  #drill-panel{background:var(--card2);border-left:1px solid var(--border);width:min(560px,95vw);height:100%;display:flex;flex-direction:column;animation:slideIn .25s ease}
  @keyframes slideIn{from{transform:translateX(100%)}to{transform:translateX(0)}}
  #drill-header{padding:16px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px;flex-shrink:0}
  #drill-breadcrumb{flex:1;font-size:12px;color:var(--sub);word-break:break-all;line-height:1.5}
  #drill-breadcrumb span{cursor:pointer;color:var(--accent)}
  #drill-breadcrumb span:hover{text-decoration:underline}
  .drill-close{background:transparent;border:none;color:var(--sub);font-size:16px;cursor:pointer;padding:4px 8px;border-radius:6px;line-height:1}
  .drill-close:hover{background:var(--border)}
  #drill-body{flex:1;overflow-y:auto;padding:10px 0}
  .drill-row{display:flex;align-items:center;gap:10px;padding:9px 18px;cursor:pointer;transition:background .12s;border-bottom:1px solid rgba(255,255,255,.03)}
  .drill-row:hover{background:rgba(255,255,255,.04)}
  .drill-icon{font-size:15px;flex-shrink:0;width:20px;text-align:center}
  .drill-name{flex:1;font-size:13px;word-break:break-all;min-width:0}
  .drill-name.hidden{color:var(--sub);opacity:.6}
  .drill-size{font-size:12px;color:var(--sub);flex-shrink:0;min-width:64px;text-align:right}
  .drill-bar-wrap{width:80px;background:var(--border);border-radius:3px;height:3px;flex-shrink:0}
  .drill-bar-fill{height:100%;border-radius:3px;background:var(--accent)}
  .drill-actions{display:flex;gap:6px;flex-shrink:0}
  .drill-open-btn{background:rgba(91,142,240,.1);color:var(--accent);border:1px solid rgba(91,142,240,.2);border-radius:6px;padding:3px 9px;font-size:11px;cursor:pointer}
  .drill-open-btn:hover{background:rgba(91,142,240,.22)}
  .drill-del-btn{background:rgba(248,113,113,.08);color:var(--danger);border:1px solid rgba(248,113,113,.18);border-radius:6px;padding:3px 9px;font-size:11px;cursor:pointer}
  .drill-del-btn:hover{background:rgba(248,113,113,.2)}
  .drill-loading{padding:30px;text-align:center;color:var(--sub);font-size:13px}
  .drill-err{padding:20px 18px;color:var(--danger);font-size:13px}
  .drill-empty{padding:30px;text-align:center;color:var(--sub);font-size:13px}

  .overlay{position:fixed;inset:0;background:rgba(0,0,0,.65);backdrop-filter:blur(5px);display:flex;align-items:center;justify-content:center;z-index:999}
  .modal{background:var(--card2);border:1px solid var(--border);border-radius:16px;padding:26px;max-width:400px;width:90%}
  .modal h2{font-size:16px;margin-bottom:8px}
  .modal p{font-size:13px;color:var(--sub);line-height:1.55;margin-bottom:8px}
  .modal code{background:var(--bg);padding:3px 8px;border-radius:5px;font-family:"SF Mono",monospace;font-size:11px;color:var(--text);word-break:break-all;display:block;margin:8px 0 14px}
  .modal-btns{display:flex;gap:10px;justify-content:flex-end;margin-top:6px}
  .btn-cancel{background:var(--border);color:var(--text);border:none;border-radius:8px;padding:8px 16px;font-size:13px;cursor:pointer}
  .btn-confirm{background:var(--danger);color:#fff;border:none;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer}
  .btn-confirm:hover{opacity:.85}

  #toast{position:fixed;bottom:26px;left:50%;transform:translateX(-50%) translateY(16px);background:var(--card2);border:1px solid var(--border);color:var(--text);padding:9px 20px;border-radius:10px;font-size:13px;opacity:0;transition:all .3s;pointer-events:none;white-space:nowrap;z-index:1000}
  #toast.show{opacity:1;transform:translateX(-50%) translateY(0)}

  .welcome{padding:60px 26px;text-align:center}
  .welcome .icon{font-size:56px;margin-bottom:16px}
  .welcome h2{font-size:20px;font-weight:700;margin-bottom:8px}
  .welcome p{font-size:13px;color:var(--sub);max-width:380px;margin:0 auto;line-height:1.65}
  .welcome ul{list-style:none;display:flex;flex-direction:column;gap:6px;margin-top:18px;max-width:340px;margin-left:auto;margin-right:auto}
  .welcome ul li{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px 14px;font-size:12px;color:var(--sub);text-align:left;display:flex;align-items:center;gap:8px}
</style>
</head>
<body>

<header>
  <div class="logo">🔍</div>
  <div>
    <h1 id="appTitle"></h1>
    <p id="appSubtitle"></p>
  </div>
  <div class="lang-switch">
    <button class="lang-btn active" data-lang="zh" onclick="setLanguage('zh', this)">中文</button>
    <button class="lang-btn" data-lang="en" onclick="setLanguage('en', this)">EN</button>
  </div>
  <button class="scan-btn" id="scanBtn" onclick="startScan()">🔍 开始扫描</button>
</header>

<div id="welcome" class="welcome">
  <div class="icon">💾</div>
  <h2 id="welcomeTitle"></h2>
  <p id="welcomeDesc"></p>
  <ul id="welcomeList">
  </ul>
</div>

<section id="disk-section" style="display:none">
  <div class="disk-card">
    <div class="disk-header">
      <span class="disk-title" id="diskTitle"></span>
      <span style="font-size:13px;color:var(--sub)" id="disk-pct"></span>
    </div>
    <div class="bar-wrap"><div class="bar-fill" id="disk-bar" style="width:0%"></div></div>
    <div class="disk-stats">
      <div class="stat"><span id="labelUsed"></span><strong id="d-used"></strong></div>
      <div class="stat"><span id="labelAvail"></span><strong id="d-avail"></strong></div>
      <div class="stat"><span id="labelTotal"></span><strong id="d-total"></strong></div>
    </div>
  </div>
</section>

<section id="filters" style="display:none">
  <button class="filter-btn active" data-filter-key="all" onclick="setFilter('all',this)"></button>
  <button class="filter-btn" data-filter-key="caches_logs" onclick="setFilter('缓存 & 日志',this)"></button>
  <button class="filter-btn" data-filter-key="personal_files" onclick="setFilter('个人文件',this)"></button>
  <button class="filter-btn" data-filter-key="app_data" onclick="setFilter('应用数据',this)"></button>
  <button class="filter-btn" data-filter-key="virtual_machines" onclick="setFilter('虚拟机',this)"></button>
  <div class="sort-wrap" style="margin-left:4px"><span id="categoryLabel"></span>
    <select id="categorySelect" onchange="setFilterSelect(this.value)">
      <option value="" data-select-key="more_categories"></option>
      <optgroup data-group-key="dev_languages">
        <option value="Apple 开发" data-option-key="apple_dev"></option>
        <option value="Node.js / 前端" data-option-key="node_frontend"></option>
        <option value="Python" data-option-key="python"></option>
        <option value="Java / JVM" data-option-key="java_jvm"></option>
        <option value="Go" data-option-key="go"></option>
        <option value="Rust" data-option-key="rust"></option>
        <option value="Flutter / Dart" data-option-key="flutter_dart"></option>
        <option value="Ruby" data-option-key="ruby"></option>
        <option value="PHP" data-option-key="php"></option>
        <option value="Android 开发" data-option-key="android_dev"></option>
        <option value="其他语言" data-option-key="other_languages"></option>
        <option value="其他开发工具" data-option-key="other_dev_tools"></option>
      </optgroup>
      <optgroup data-group-key="tools_services">
        <option value="IDE & 编辑器" data-option-key="ides_editors"></option>
        <option value="AI / 机器学习" data-option-key="ai_ml"></option>
        <option value="数据库" data-option-key="databases"></option>
        <option value="云服务 CLI" data-option-key="cloud_service_clis"></option>
        <option value="安全 & 调试" data-option-key="security_debugging"></option>
      </optgroup>
      <optgroup data-group-key="apps_media">
        <option value="浏览器" data-option-key="browsers"></option>
        <option value="即时通讯" data-option-key="messaging"></option>
        <option value="云存储" data-option-key="cloud_storage"></option>
        <option value="媒体制作" data-option-key="media_production"></option>
        <option value="设计工具" data-option-key="design_tools"></option>
        <option value="游戏 & 娱乐" data-option-key="gaming_entertainment"></option>
        <option value="笔记 & 知识" data-option-key="notes_knowledge"></option>
      </optgroup>
      <optgroup data-group-key="system_group">
        <option value="系统" data-option-key="system"></option>
      </optgroup>
    </select>
  </div>
  <div class="filter-sep"></div>
  <div class="sort-wrap"><span id="sortLabel"></span>
    <select id="sortSelect" onchange="doSort(this.value)">
      <option value="size" data-sort-key="size"></option>
      <option value="name" data-sort-key="name"></option>
      <option value="safety" data-sort-key="safety"></option>
    </select>
  </div>
</section>

<section id="filters2" style="display:none">
  <span style="font-size:12px;color:var(--sub);flex-shrink:0" id="safetyLabel"></span>
  <button class="safety-btn active" data-safety="" data-safety-key="all" onclick="setSafety('',this)"></button>
  <button class="safety-btn" data-safety="safe" data-safety-key="safe" onclick="setSafety('safe',this)"></button>
  <button class="safety-btn" data-safety="caution" data-safety-key="caution" onclick="setSafety('caution',this)"></button>
  <button class="safety-btn" data-safety="danger" data-safety-key="danger" onclick="setSafety('danger',this)"></button>
  <button class="safety-btn" data-safety="manual" data-safety-key="manual" onclick="setSafety('manual',this)"></button>
  <div class="filter-sep"></div>
  <div class="search-wrap">
    <input id="searchBox" type="text" oninput="doSearch(this.value)">
    <button class="clear-btn" id="clearSearchBtn" onclick="clearSearch()">✕</button>
  </div>
</section>

<div id="summary" style="display:none"></div>

<section id="legend" style="display:none">
  <div class="leg"><div class="leg-dot" style="background:var(--safe)"></div><span data-legend-key="safe"></span></div>
  <div class="leg"><div class="leg-dot" style="background:var(--caution)"></div><span data-legend-key="caution"></span></div>
  <div class="leg"><div class="leg-dot" style="background:var(--danger)"></div><span data-legend-key="danger"></span></div>
  <div class="leg"><div class="leg-dot" style="background:var(--manual)"></div><span data-legend-key="manual"></span></div>
</section>

<div id="loading"><div class="spinner"></div><span id="loadingText"></span><br><small style="display:block;margin-top:8px" id="loadingHint"></small></div>
<div id="grid"></div>
<div id="empty"></div>

<!-- 下钻面板 -->
<div id="drill-overlay" style="display:none" onclick="if(event.target===this)closeDrill()">
  <div id="drill-panel">
    <div id="drill-header">
      <div id="drill-breadcrumb"></div>
      <button class="drill-close" onclick="closeDrill()">✕</button>
    </div>
    <div id="drill-body"></div>
  </div>
</div>

<div id="modal" style="display:none">
  <div class="overlay" onclick="closeModal()">
    <div class="modal" onclick="event.stopPropagation()">
      <h2 id="modalTitle"></h2>
      <p id="modalDesc"></p>
      <code id="modal-path"></code>
      <p id="modal-warn" style="color:var(--danger);font-size:12px;display:none"></p>
      <div class="modal-btns">
        <button class="btn-cancel" id="cancelBtn" onclick="closeModal()"></button>
        <button class="btn-confirm" id="confirmBtn" onclick="confirmDelete()"></button>
      </div>
    </div>
  </div>
</div>

<div id="toast"></div>

<script>
let allItems=[], maxSize=1, currentFilter='all', currentSort='size', currentSafety='', searchQuery='', pendingDelete=null, currentLang='zh';
const I18N={
  zh:{
    htmlLang:'zh-CN', title:'Mac 磁盘分析工具', subtitle:'扫描常见路径占用 · 显示路径说明 · 一键移入废纸篓',
    scan:'🔍 开始扫描', rescan:'🔄 重新扫描', scanning:'扫描中…',
    welcomeTitle:'分析 Mac 磁盘占用', welcomeDesc:'点击「开始扫描」，工具将自动扫描系统缓存、开发工具、个人文件等常见路径，并显示每个路径的说明和安全等级。',
    welcomeList:['🟢 <strong>可安全删除</strong> — 缓存类文件，删除不影响使用','🟡 <strong>谨慎删除</strong> — 删除前请确认不再需要','🔴 <strong>不建议直接删除</strong> — 有更安全的卸载方式','🟣 <strong>手动检查</strong> — 个人文件，请自行决定'],
    diskTitle:'磁盘总览', used:'已用 ', avail:'可用 ', total:'总共 ', usedPct:'已使用',
    category:'分类：', sort:'排序：', safetyFilter:'安全等级：', searchPlaceholder:'搜索名称 / 路径 / 说明…', clearSearch:'清除搜索',
    filters:{all:'全部',caches_logs:'缓存 & 日志',personal_files:'个人文件',app_data:'应用数据',virtual_machines:'虚拟机'},
    select:{more_categories:'— 更多分类 —',dev_languages:'── 开发语言 ──',tools_services:'── 工具 & 服务 ──',apps_media:'── 应用 & 媒体 ──',system_group:'── 系统 ──'},
    options:{apple_dev:'Apple 开发（Xcode / iOS）',node_frontend:'Node.js / 前端',python:'Python',java_jvm:'Java / JVM',go:'Go',rust:'Rust',flutter_dart:'Flutter / Dart',ruby:'Ruby',php:'PHP',android_dev:'Android 开发',other_languages:'其他语言（Elixir / Haskell / .NET…）',other_dev_tools:'其他开发工具',ides_editors:'IDE & 编辑器',ai_ml:'AI / 机器学习',databases:'数据库',cloud_service_clis:'云服务 CLI',security_debugging:'安全 & 调试',browsers:'浏览器',messaging:'即时通讯',cloud_storage:'云存储',media_production:'媒体制作',design_tools:'设计工具',gaming_entertainment:'游戏 & 娱乐',notes_knowledge:'笔记 & 知识',system:'系统'},
    sorts:{size:'按大小',name:'按名称',safety:'按安全等级'},
    safety:{all:'全部',safe:'🟢 可安全删除',caution:'🟡 谨慎删除',danger:'🔴 不建议直接删除',manual:'🟣 手动检查'},
    loading:'正在扫描磁盘，请稍候…', loadingHint:'统计大目录可能需要数十秒', empty:'当前分类下没有检测到已存在的路径',
    summary:(count,size)=>`找到 ${count} 个路径，合计占用 ${size}`,
    card:{openTitle:'在 Finder 中打开', drillTitle:'查看子目录', delete:'移入废纸篓', moved:'✅ 已移入废纸篓', processing:'处理中…'},
    modal:{title:'⚠️ 确认移入废纸篓', desc:'以下路径将被移入废纸篓（可在废纸篓中恢复），之后可手动清倒废纸篓释放空间。', cancel:'取消', confirm:'确认移入废纸篓', dangerWarn:'⚠️ 此路径标记为「不建议直接删除」，请确保您了解删除后果！'},
    drill:{loading:'扫描中…', empty:'此目录为空', requestFailed:'❌ 请求失败：', openTitle:'在 Finder 中打开'},
    toast:{scanFailed:'扫描失败：', networkError:'❌ 网络错误', finderOpenFailed:'❌ 无法打开 Finder'},
    api:{missingPath:'缺少 path 参数'}
  },
  en:{
    htmlLang:'en', title:'Mac Disk Space Analyzer', subtitle:'Scan common storage paths · Explain what they contain · Move removable items to Trash',
    scan:'🔍 Start Scan', rescan:'🔄 Rescan', scanning:'Scanning…',
    welcomeTitle:'Analyze Mac Disk Usage', welcomeDesc:'Click "Start Scan" to inspect common storage-heavy locations such as system caches, developer tools, and personal files. Each item includes an explanation and a safety level.',
    welcomeList:['🟢 <strong>Safe to delete</strong> — Cache-like files that apps can recreate','🟡 <strong>Delete with caution</strong> — Confirm you no longer need them first','🔴 <strong>Not recommended</strong> — There is usually a safer uninstall or cleanup path','🟣 <strong>Manual review</strong> — Personal files, your decision'],
    diskTitle:'Disk Overview', used:'Used ', avail:'Available ', total:'Total ', usedPct:'used',
    category:'Category:', sort:'Sort:', safetyFilter:'Safety:', searchPlaceholder:'Search name / path / description…', clearSearch:'Clear search',
    filters:{all:'All',caches_logs:'Caches & Logs',personal_files:'Personal Files',app_data:'App Data',virtual_machines:'Virtual Machines'},
    select:{more_categories:'— More categories —',dev_languages:'── Dev Languages ──',tools_services:'── Tools & Services ──',apps_media:'── Apps & Media ──',system_group:'── System ──'},
    options:{apple_dev:'Apple Development (Xcode / iOS)',node_frontend:'Node.js / Frontend',python:'Python',java_jvm:'Java / JVM',go:'Go',rust:'Rust',flutter_dart:'Flutter / Dart',ruby:'Ruby',php:'PHP',android_dev:'Android Development',other_languages:'Other Languages (Elixir / Haskell / .NET…)',other_dev_tools:'Other Dev Tools',ides_editors:'IDEs & Editors',ai_ml:'AI / ML',databases:'Databases',cloud_service_clis:'Cloud Service CLIs',security_debugging:'Security & Debugging',browsers:'Browsers',messaging:'Messaging',cloud_storage:'Cloud Storage',media_production:'Media Production',design_tools:'Design Tools',gaming_entertainment:'Gaming & Entertainment',notes_knowledge:'Notes & Knowledge',system:'System'},
    sorts:{size:'By size',name:'By name',safety:'By safety'},
    safety:{all:'All',safe:'🟢 Safe to delete',caution:'🟡 Delete with caution',danger:'🔴 Not recommended',manual:'🟣 Manual review'},
    loading:'Scanning disk usage. Please wait…', loadingHint:'Large directories may take tens of seconds to measure', empty:'No existing paths were found for the current filters',
    summary:(count,size)=>`Found ${count} paths using ${size} total`,
    card:{openTitle:'Open in Finder', drillTitle:'Browse subdirectories', delete:'Move to Trash', moved:'✅ Moved to Trash', processing:'Working…'},
    modal:{title:'⚠️ Confirm Move to Trash', desc:'The following path will be moved to Trash and can be restored from Trash later. Empty Trash manually to reclaim disk space.', cancel:'Cancel', confirm:'Move to Trash', dangerWarn:'⚠️ This path is marked as "Not recommended". Make sure you understand the impact before deleting it.'},
    drill:{loading:'Scanning…', empty:'This directory is empty', requestFailed:'❌ Request failed: ', openTitle:'Open in Finder'},
    toast:{scanFailed:'Scan failed: ', networkError:'❌ Network error', finderOpenFailed:'❌ Unable to open Finder'},
    api:{missingPath:'Missing path parameter'}
  }
};
const SAFETY_LABEL={
  zh:{safe:'可安全删除',caution:'谨慎删除',danger:'不建议直接删除',manual:'手动检查'},
  en:{safe:'Safe to delete',caution:'Delete with caution',danger:'Not recommended',manual:'Manual review'}
};
const SAFETY_ORDER={safe:0,caution:1,manual:2,danger:3};

function t(){ return I18N[currentLang]; }

function setLanguage(lang, btn){
  currentLang=lang;
  localStorage.setItem('mac-disk-analyzer-lang', lang);
  document.documentElement.lang=t().htmlLang;
  document.querySelectorAll('.lang-btn').forEach(b=>b.classList.toggle('active', b.dataset.lang===lang));
  applyStaticText();
  renderCards();
}

function applyStaticText(){
  const i=t();
  document.title=i.title;
  document.getElementById('appTitle').textContent=i.title;
  document.getElementById('appSubtitle').textContent=i.subtitle;
  document.getElementById('scanBtn').textContent=allItems.length ? i.rescan : i.scan;
  document.getElementById('welcomeTitle').textContent=i.welcomeTitle;
  document.getElementById('welcomeDesc').textContent=i.welcomeDesc;
  document.getElementById('welcomeList').innerHTML=i.welcomeList.map(x=>`<li>${x}</li>`).join('');
  document.getElementById('diskTitle').textContent=i.diskTitle;
  document.getElementById('labelUsed').textContent=i.used;
  document.getElementById('labelAvail').textContent=i.avail;
  document.getElementById('labelTotal').textContent=i.total;
  document.getElementById('categoryLabel').textContent=i.category;
  document.getElementById('sortLabel').textContent=i.sort;
  document.getElementById('safetyLabel').textContent=i.safetyFilter;
  document.getElementById('searchBox').placeholder=i.searchPlaceholder;
  document.getElementById('clearSearchBtn').title=i.clearSearch;
  document.getElementById('loadingText').textContent=i.loading;
  document.getElementById('loadingHint').textContent=i.loadingHint;
  document.getElementById('empty').textContent=i.empty;
  document.getElementById('modalTitle').textContent=i.modal.title;
  document.getElementById('modalDesc').textContent=i.modal.desc;
  document.getElementById('cancelBtn').textContent=i.modal.cancel;
  document.getElementById('confirmBtn').textContent=i.modal.confirm;
  document.querySelectorAll('[data-filter-key]').forEach(el=>el.textContent=i.filters[el.dataset.filterKey]);
  document.querySelectorAll('[data-group-key]').forEach(el=>el.label=i.select[el.dataset.groupKey]);
  document.querySelectorAll('[data-select-key]').forEach(el=>el.textContent=i.select[el.dataset.selectKey]);
  document.querySelectorAll('[data-option-key]').forEach(el=>el.textContent=i.options[el.dataset.optionKey]);
  document.querySelectorAll('[data-sort-key]').forEach(el=>el.textContent=i.sorts[el.dataset.sortKey]);
  document.querySelectorAll('[data-safety-key]').forEach(el=>el.textContent=i.safety[el.dataset.safetyKey]);
  document.querySelectorAll('[data-legend-key]').forEach(el=>el.textContent=i.safety[el.dataset.legendKey]);
  renderDiskLabels();
}

function renderDiskLabels(){
  const pct=document.getElementById('disk-pct');
  if(!pct.dataset.value) return;
  pct.textContent=`${pct.dataset.value}% ${t().usedPct}`;
}

async function startScan(){
  const btn=document.getElementById('scanBtn');
  btn.disabled=true; btn.textContent=t().scanning;
  document.getElementById('welcome').style.display='none';
  document.getElementById('loading').style.display='block';
  document.getElementById('grid').innerHTML='';
  document.getElementById('disk-section').style.display='none';
  document.getElementById('filters').style.display='none';
  document.getElementById('filters2').style.display='none';
  document.getElementById('legend').style.display='none';
  document.getElementById('summary').style.display='none';
  document.getElementById('empty').style.display='none';
  // reset filters
  currentFilter='all'; currentSafety=''; searchQuery='';
  document.getElementById('searchBox').value='';
  document.querySelectorAll('.filter-btn').forEach((b,i)=>b.classList.toggle('active',i===0));
  document.querySelectorAll('.safety-btn').forEach((b,i)=>b.classList.toggle('active',i===0));
  document.getElementById('categorySelect').value='';
  try{
    const r=await fetch('/api/scan');
    const d=await r.json();
    renderDisk(d.disk_formatted);
    allItems=d.items;
    maxSize=Math.max(...allItems.filter(i=>i.size!=null).map(i=>i.size),1);
    renderCards();
    document.getElementById('disk-section').style.display='block';
    document.getElementById('filters').style.display='flex';
    document.getElementById('filters2').style.display='flex';
    document.getElementById('legend').style.display='flex';
    document.getElementById('summary').style.display='block';
  }catch(e){showToast(t().toast.scanFailed+e.message);}
  finally{
    document.getElementById('loading').style.display='none';
    btn.disabled=false; btn.textContent=t().rescan;
  }
}

function renderDisk(d){
  document.getElementById('disk-pct').dataset.value=d.percent;
  renderDiskLabels();
  const bar=document.getElementById('disk-bar');
  bar.style.width=d.percent+'%';
  bar.style.background=d.percent>85?'linear-gradient(90deg,#f87171,#fbbf24)':d.percent>70?'linear-gradient(90deg,#fbbf24,#5b8ef0)':'linear-gradient(90deg,#5b8ef0,#a78bfa)';
  document.getElementById('d-used').textContent=d.used;
  document.getElementById('d-avail').textContent=d.available;
  document.getElementById('d-total').textContent=d.total;
}

function renderCards(){
  const grid=document.getElementById('grid');
  grid.innerHTML='';
  let items=currentFilter==='all'?allItems:allItems.filter(i=>i.category===currentFilter);
  if(currentSafety) items=items.filter(i=>i.safety===currentSafety);
  if(searchQuery){
    const q=searchQuery.toLowerCase();
    items=items.filter(i=>
      i.name.toLowerCase().includes(q)||
      i.name_en.toLowerCase().includes(q)||
      i.path.toLowerCase().includes(q)||
      i.real_path.toLowerCase().includes(q)||
      i.desc.toLowerCase().includes(q)||
      i.desc_en.toLowerCase().includes(q)||
      i.category.toLowerCase().includes(q)||
      i.category_en.toLowerCase().includes(q)
    );
  }
  items=items.filter(i=>i.exists);
  if(currentSort==='size') items=[...items].sort((a,b)=>(b.size||0)-(a.size||0));
  else if(currentSort==='name') items=[...items].sort((a,b)=>getDisplayName(a).localeCompare(getDisplayName(b),currentLang==='zh'?'zh':'en'));
  else if(currentSort==='safety') items=[...items].sort((a,b)=>(SAFETY_ORDER[a.safety]??2)-(SAFETY_ORDER[b.safety]??2));

  const totalSz=items.reduce((s,i)=>s+(i.size||0),0);
  const sumEl=document.getElementById('summary');
  sumEl.textContent=t().summary(items.length, fmtBytes(totalSz));

  if(!items.length){document.getElementById('empty').style.display='block';return;}
  document.getElementById('empty').style.display='none';

  items.forEach(item=>{
    const pct=item.size?Math.round(item.size/maxSize*100):0;
    const sc={safe:'var(--safe)',caution:'var(--caution)',danger:'var(--danger)',manual:'var(--manual)'}[item.safety]||'var(--sub)';
    const safeLabel=SAFETY_LABEL[currentLang][item.safety]||'';
    const cid='c_'+btoa(encodeURIComponent(item.path)).replace(/[^a-zA-Z0-9]/g,'');
    const div=document.createElement('div');
    div.className='card'; div.id=cid;
    div.innerHTML=`
      <div class="card-top">
        <div class="card-info">
          <div class="card-name">
            <span style="width:7px;height:7px;border-radius:50%;background:${sc};flex-shrink:0;display:inline-block"></span>
            ${esc(getDisplayName(item))}
            <span class="card-cat">${esc(getDisplayCategory(item))}</span>
          </div>
          <div class="card-path">${esc(item.real_path)}</div>
        </div>
        <div class="card-size">${esc(item.size_formatted)}</div>
      </div>
      <div class="card-desc">${esc(getDisplayDesc(item))}</div>
      <div class="card-footer">
        <span class="badge badge-${item.safety}">${safeLabel}</span>
        <div class="mini-bar-wrap"><div class="mini-bar-fill" style="width:${pct}%"></div></div>
        <div style="display:flex;gap:5px;flex-shrink:0">
          <button class="open-btn" title="${esc(t().card.openTitle)}" onclick="openInFinder('${esc(item.real_path)}',event)">📂</button>
          <button class="drill-card-btn" title="${esc(t().card.drillTitle)}" onclick="openDrill('${esc(item.real_path)}',event)">🔍</button>
          <button class="del-btn" data-path="${esc(item.path)}" data-safety="${item.safety}" onclick="askDelete(this)">${t().card.delete}</button>
        </div>
      </div>`;
    grid.appendChild(div);
  });
}

function getDisplayName(item){ return currentLang==='zh' ? item.name : item.name_en; }
function getDisplayDesc(item){ return currentLang==='zh' ? item.desc : item.desc_en; }
function getDisplayCategory(item){ return currentLang==='zh' ? item.category : item.category_en; }

function setFilter(cat,btn){
  currentFilter=cat;
  document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  const sel=document.querySelector('#filters select');
  if(sel) sel.value='';
  renderCards();
}
function setFilterSelect(val){
  if(!val) return;
  currentFilter=val;
  document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
  renderCards();
}
function setSafety(val,btn){
  currentSafety=val;
  document.querySelectorAll('.safety-btn').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  renderCards();
}
function doSearch(val){
  searchQuery=val.trim();
  renderCards();
}
function clearSearch(){
  searchQuery='';
  document.getElementById('searchBox').value='';
  renderCards();
}
function doSort(v){currentSort=v;renderCards();}

function askDelete(btn){
  const path=btn.dataset.path, safety=btn.dataset.safety;
  pendingDelete={path,btn};
  document.getElementById('modal-path').textContent=path;
  const w=document.getElementById('modal-warn');
  if(safety==='danger'){w.textContent=t().modal.dangerWarn;w.style.display='block';}
  else{w.style.display='none';}
  document.getElementById('modal').style.display='flex';
}
function closeModal(){document.getElementById('modal').style.display='none';pendingDelete=null;}

async function confirmDelete(){
  if(!pendingDelete)return;
  const{path,btn,fromDrill}=pendingDelete;
  closeModal();
  if(btn){btn.disabled=true; btn.textContent=t().card.processing;}
  try{
    const r=await fetch('/api/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path})});
    const d=await r.json();
    if(d.success){
      showToast(d.message);
      if(fromDrill){
        // 刷新下钻面板当前层
        if(drillStack.length) loadDrill(drillStack[drillStack.length-1].path);
      } else if(btn){
        btn.textContent=t().card.moved;btn.classList.add('gone');
        const card=btn.closest('.card');
        if(card){
          const sz=card.querySelector('.card-size');if(sz){sz.textContent='—';sz.classList.add('na');}
          const mb=card.querySelector('.mini-bar-fill');if(mb)mb.style.width='0%';
        }
      }
    }else{
      if(btn){btn.disabled=false;btn.textContent=t().card.delete;}
      showToast('❌ '+d.message);
    }
  }catch(e){
    if(btn){btn.disabled=false;btn.textContent=t().card.delete;}
    showToast(t().toast.networkError);
  }
}

// ── 在 Finder 中打开 ──
async function openInFinder(realPath, e){
  if(e) e.stopPropagation();
  try{
    const r=await fetch('/api/open',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:realPath})});
    const d=await r.json();
    if(!d.success) showToast('❌ '+d.message);
  }catch{showToast(t().toast.finderOpenFailed);}
}

// ── 下钻面板 ──
let drillStack=[];  // [{path, label}]

function openDrill(realPath, e){
  if(e) e.stopPropagation();
  drillStack=[{path:realPath, label:realPath}];
  document.getElementById('drill-overlay').style.display='flex';
  loadDrill(realPath);
}

function closeDrill(){
  document.getElementById('drill-overlay').style.display='none';
  drillStack=[];
}

function drillInto(path, label){
  drillStack.push({path, label});
  loadDrill(path);
}

function drillUp(idx){
  drillStack=drillStack.slice(0,idx+1);
  loadDrill(drillStack[idx].path);
}

function renderBreadcrumb(){
  const bc=document.getElementById('drill-breadcrumb');
  bc.innerHTML=drillStack.map((s,i)=>{
    const short=s.label.length>38?'…'+s.label.slice(-36):s.label;
    if(i<drillStack.length-1)
      return `<span onclick="drillUp(${i})" title="${esc(s.label)}">${esc(short)}</span> /`;
    return `<strong title="${esc(s.label)}">${esc(short)}</strong>`;
  }).join(' ');
}

async function loadDrill(path){
  renderBreadcrumb();
  const body=document.getElementById('drill-body');
  body.innerHTML=`<div class="drill-loading"><div class="spinner" style="width:24px;height:24px;border-width:2px;margin:0 auto 10px"></div>${esc(t().drill.loading)}</div>`;
  try{
    const r=await fetch('/api/browse?path='+encodeURIComponent(path));
    const d=await r.json();
    if(d.error){body.innerHTML=`<div class="drill-err">⚠️ ${esc(d.error)}</div>`;return;}
    if(!d.items.length){body.innerHTML=`<div class="drill-empty">${esc(t().drill.empty)}</div>`;return;}
    body.innerHTML='';
    d.items.forEach(item=>{
      const row=document.createElement('div');
      row.className='drill-row';
      const icon=item.is_dir?'📁':'📄';
      row.innerHTML=`
        <span class="drill-icon">${icon}</span>
        <span class="drill-name${item.is_hidden?' hidden':''}" title="${esc(item.path)}">${esc(item.name)}</span>
        <div class="drill-bar-wrap"><div class="drill-bar-fill" style="width:${item.pct}%"></div></div>
        <span class="drill-size">${esc(item.size_formatted)}</span>
        <div class="drill-actions">
          <button class="drill-open-btn" onclick="openInFinder('${esc(item.path)}',event)" title="${esc(t().drill.openTitle)}">📂</button>
          <button class="drill-del-btn" onclick="askDeletePath('${esc(item.path)}',event)">🗑</button>
        </div>`;
      if(item.is_dir){
        row.querySelector('.drill-name').onclick=(e)=>{e.stopPropagation();drillInto(item.path, item.name);};
        row.querySelector('.drill-icon').onclick=(e)=>{e.stopPropagation();drillInto(item.path, item.name);};
        row.ondblclick=(e)=>{e.stopPropagation();drillInto(item.path, item.name);};
      }
      body.appendChild(row);
    });
  }catch(e){body.innerHTML=`<div class="drill-err">${esc(t().drill.requestFailed)}${esc(e.message)}</div>`;}
}

function askDeletePath(path, e){
  if(e) e.stopPropagation();
  // reuse modal, but without a card button reference
  pendingDelete={path, btn:null, fromDrill:true};
  document.getElementById('modal-path').textContent=path;
  document.getElementById('modal-warn').style.display='none';
  document.getElementById('modal').style.display='flex';
}

function showToast(msg){
  const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),3000);
}
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function fmtBytes(n){if(!n)return'0 B';if(n<1024**2)return(n/1024).toFixed(0)+' KB';if(n<1024**3)return(n/1024**2).toFixed(1)+' MB';return(n/1024**3).toFixed(2)+' GB';}
setLanguage(localStorage.getItem('mac-disk-analyzer-lang')||'zh');
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/":
            self._send(200, "text/html; charset=utf-8", HTML.encode())
        elif p == "/api/scan":
            disk = get_disk_info()
            pct  = round(disk["used"] / max(disk["total"], 1) * 100, 1)
            items = []
            for cfg in PATHS_CONFIG:
                size = get_dir_size_bytes(cfg["path"])
                items.append(enrich_item(cfg, size))
            items.sort(key=lambda x: x["size"] if x["size"] is not None else 0, reverse=True)
            payload = json.dumps({
                "disk": disk,
                "disk_formatted": {
                    "total": fmt(disk["total"], "en"), "used": fmt(disk["used"], "en"),
                    "available": fmt(disk["available"], "en"), "percent": pct},
                "items": items}).encode()
            self._send(200, "application/json; charset=utf-8", payload)
        elif p == "/api/browse":
            from urllib.parse import parse_qs
            qs   = parse_qs(urlparse(self.path).query)
            path = qs.get("path", [""])[0]
            if not path:
                self._send(400, "application/json; charset=utf-8",
                           json.dumps({"error": "Missing path parameter"}).encode())
                return
            items, err = browse_dir(path)
            if err:
                self._send(200, "application/json; charset=utf-8",
                           json.dumps({"error": err, "items": []}).encode())
            else:
                max_sz = max((i["size"] for i in items if i["size"]), default=1)
                for i in items:
                    i["pct"] = round(i["size"] / max_sz * 100) if i["size"] else 0
                self._send(200, "application/json; charset=utf-8",
                           json.dumps({"items": items, "path": path}).encode())
        else:
            self._send(404, "text/plain", b"Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path).path
        if parsed_path == "/api/open":
            length = int(self.headers.get("Content-Length", 0))
            body   = json.loads(self.rfile.read(length))
            ok, msg = open_in_finder(body.get("path", ""))
            self._send(200, "application/json; charset=utf-8",
                       json.dumps({"success": ok, "message": msg}).encode())
        elif parsed_path == "/api/delete":
            length = int(self.headers.get("Content-Length", 0))
            body   = json.loads(self.rfile.read(length))
            ok, msg = move_to_trash(body.get("path", ""))
            self._send(200, "application/json; charset=utf-8",
                       json.dumps({"success": ok, "message": msg}).encode())

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"✅ 磁盘分析工具已启动：{url}")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 已停止")
