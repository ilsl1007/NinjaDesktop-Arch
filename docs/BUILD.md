# NinjaDesktop 1.0.6 打包命令

本流程仅针对 `NinjaDesktop-1.0.6-linux-amd64.deb` 和 `x86_64` 系统。最终生成 `ninjadesktop-electron-1.0.6-x86_64.pkg.tar.zst`。

## 首次准备

```bash
# 更新系统并安装打包工具
sudo pacman -Syu --needed base-devel binutils pacman-contrib pkgfile python libarchive zstd git curl

# 安装 debtap；使用 yay 的人改为 yay -S debtap
paru -S debtap

# 克隆本仓库并进入目录
git clone https://github.com/ilsl1007/NinjaDesktop-Arch.git
cd NinjaDesktop-Arch

# 更新转换数据库，用英文环境避免中文字段解析错误
sudo env LC_ALL=C debtap -u

# 修复 debtap 3.6.3 的缓存检查，并重建基础包列表
sudo bash ./scripts/fix-debtap.sh
```

修复脚本适用于本次遇到的 debtap 缓存检查问题，会先备份 `/usr/bin/debtap` 为 `/usr/bin/debtap.before-cache-fix`。数据库不完整或脚本版本不匹配时会退出。debtap 更新后若已修复问题，可跳过这一步。

## 转换软件包

将原始 `NinjaDesktop-1.0.6-linux-amd64.deb` 放到仓库目录，然后以普通用户执行：

```bash
# 转换 DEB；按提示填写打包者，许可证可填 UNLICENSED，编辑菜单直接回车
env LC_ALL=C debtap ./NinjaDesktop-1.0.6-linux-amd64.deb

# 修正此版本的依赖和安装脚本，生成 1.0.6-2 包
python3 ./scripts/repair-ninjadesktop.py \
  ./ninjadesktop-electron-1.0.6-1-x86_64.pkg.tar.zst

# 将修正后的包重命名为发布时使用的文件名，包内版本仍为 1.0.6-2
mv -n ./ninjadesktop-electron-1.0.6-2-x86_64.pkg.tar.zst \
  ./ninjadesktop-electron-1.0.6-x86_64.pkg.tar.zst

# 检查 pacman 能否读取包并解析安装事务，不实际安装
pacman -Up --print-format '%n %v' ./ninjadesktop-electron-1.0.6-x86_64.pkg.tar.zst

# 检查安装脚本语法，成功时无输出
bsdtar -xOf ./ninjadesktop-electron-1.0.6-x86_64.pkg.tar.zst .INSTALL | bash -n

# 安装最终包
sudo pacman -U ./ninjadesktop-electron-1.0.6-x86_64.pkg.tar.zst
```

修正脚本保留原转换包；最终包已经存在时会拒绝覆盖。不同 debtap 版本可能生成不同内容，此脚本会检查预期的包信息和安装脚本，不适用于其他软件。

## GitHub 超时导致数据库更新失败

`debtap -u` 末尾显示成功不一定代表每一步成功。如果只是 virtual-packages 下载失败，已有的非空缓存可继续使用。

```bash
# 检查本地是否已有虚拟包列表
test -s /var/cache/debtap/virtual-packages && echo '已有缓存'
```

没有缓存时，可改用 raw 地址下载；确认当前终端能够访问 GitHub：

```bash
# 下载成功后才写入数据库
curl -fL --connect-timeout 15 --max-time 60 \
  https://raw.githubusercontent.com/helixarch/virtual-packages-list-generator/master/virtual-packages \
  -o /tmp/debtap-virtual-packages && \
sudo install -m 644 /tmp/debtap-virtual-packages /var/cache/debtap/virtual-packages

# 缓存补齐后重新应用修复
sudo bash ./scripts/fix-debtap.sh
```
