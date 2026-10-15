# NinjaDesktop for Arch Linux

将 NinjaDesktop **1.0.6** 的官方 amd64 DEB 重新打包为 Arch Linux / CachyOS 可安装的软件包，已在 CachyOS 上验证可用。

- 架构：`x86_64`
- 软件版本：`1.0.6`
- Arch 包版本：`1.0.6-2`（`-2` 为本地打包修订号，下载文件名省略此修订号）

这是非官方打包仓库；软件版权归原作者所有。

## 下载与安装

[下载安装包](https://github.com/ilsl1007/NinjaDesktop-Arch/releases/download/ninjadesktop-1.0.6-arch2/ninjadesktop-electron-1.0.6-x86_64.pkg.tar.zst) · [Release 页面](https://github.com/ilsl1007/NinjaDesktop-Arch/releases/tag/ninjadesktop-1.0.6-arch2)

```bash
# 下载 Arch 安装包
curl -fLO https://github.com/ilsl1007/NinjaDesktop-Arch/releases/download/ninjadesktop-1.0.6-arch2/ninjadesktop-electron-1.0.6-x86_64.pkg.tar.zst

# 下载校验文件并核对安装包
curl -fLO https://github.com/ilsl1007/NinjaDesktop-Arch/releases/download/ninjadesktop-1.0.6-arch2/SHA256SUMS
sha256sum -c SHA256SUMS

# 安装软件，按提示确认依赖
sudo pacman -U ./ninjadesktop-electron-1.0.6-x86_64.pkg.tar.zst

# 启动软件，也可以从应用菜单打开 NinjaDesktop
/opt/NinjaDesktop/ninjadesktop-electron
```

## 本次打包修正

- 移除错误的 `gtk` 依赖，保留 `gtk3`，补充 `libsecret`。
- 修复 debtap 转坏的安装脚本注释和提前返回语句。
- 重建包内校验清单 `.MTREE`，将归档属主设为 root。

软件二进制来自原始 DEB，未修改软件源码。需要自行打包时，参见[中文命令清单](docs/BUILD.md)。

## 登录提示代理连接被拒绝

如果报错包含 `127.0.0.1:7890` 和 `connection refused`，说明软件继承了代理环境变量，但该代理端口未提供服务。需要代理时，先启动对应的 Clash 等代理客户端。

若准备直连，先从托盘完全退出 NinjaDesktop，然后执行：

```bash
# 取消本次启动继承的代理环境变量，不影响其他程序
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
    -u http_proxy -u https_proxy -u all_proxy \
    /opt/NinjaDesktop/ninjadesktop-electron
```

直连是否可用取决于当前网络能否访问登录服务器。
