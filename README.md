# N1 精简旁路由固件

使用 **ImmortalWrt 24.10.6 官方 ImageBuilder 和预编译软件包**组装 ARM64 rootfs，
再交给 [Flippy/openwrt_packit](https://github.com/unifreq/openwrt_packit) 制作 N1 专用镜像，
采用 Flippy 6.12.114 内核与 Btrfs 根文件系统。

## 构建方式

1. 打开 Actions → **Build N1 OpenWrt** → **Run workflow**，选择 `main`。
2. 默认不勾选 `publish_release`，只生成下载产物。
3. 成功后下载 **N1-firmware-数字**，解开 ZIP。
4. 核对 `SHA256SUMS`，用 `openwrt_s905d_n1_*.img.gz` 制作 U 盘，先测试启动。

更新流程后需要新建一次运行；重跑旧运行仍会使用旧提交。
失败时下载同次运行的 `N1-build-logs-数字`。

不再从头编译整套系统或工具链。维护依赖 `btrfs-progs` 是唯一需要单独构建的目标软件包：
官方预编译版本没有启用打包项目要求的 Zstd，因此使用同版本官方 SDK 编译这一项及其构建依赖。
该包和构建记录有 Actions 缓存，命中后跳过 SDK 下载与编译。
实际耗时仍取决于下载、首次 SDK 依赖构建和 Flippy 打包。

## 默认配置

| 项目 | 设置 |
|---|---|
| 后台地址 | `http://192.168.1.2` |
| IPv4 上游网关、DNS | `192.168.1.1` |
| DHCP 服务 | 关闭，由主路由负责 |
| N1 IPv6、Wi-Fi | 关闭，客户端 IPv6 由主路由提供 |
| 防火墙 | Firewall4 / nftables，关闭流量卸载 |
| 默认外观 | Vantage 主题、Vantage 仪表盘，二者均带简体中文翻译 |
| 应用 | OpenClash、晶晨宝盒、网页终端、防火墙及软件包管理 |
| 代理初始状态 | 关闭；预装 ARM64 Mihomo，需自行导入配置 |
| 密码与订阅 | 不内置，首次登录自行设置 |
| 根文件系统 | Flippy 打包生成的 Btrfs |

Vantage 的四个组件均明确加入：`luci-theme-vantage`、`luci-app-vantage`、
`luci-i18n-vantage-theme-zh-cn`、`luci-i18n-vantage-zh-cn`。
首次启动脚本指定默认主题和中文界面，不依赖安装顺序自动选择。
不添加下载、NAS、Docker、去广告或其他代理插件。
主路由向 N1 转发和故障回退仍需另行配置。

## 版本与维护依赖

`configs/prebuilt-lock.json` 锁定官方 ImageBuilder、SDK 和上游插件发布包的 URL、版本及 SHA256；
下载时验证摘要，官方软件源保留 ImageBuilder 自带的签名验证。
`configs/packages.txt` 是安装清单，负号表示移除默认包。
OpenClash、晶晨宝盒、Vantage 使用其上游预编译包；SDK 只构建带 Zstd 的 Btrfs 工具。

已保留 openwrt_packit README 要求的 Perl 模块、磁盘/文件系统工具、Bash、
bsdtar、pigz、gawk、getopt、losetup、tar、uuidgen 等依赖。
不添加仅用于 Wi-Fi、KVM、Photonicat 或 Netdata 的可选组件。
`armsr/armv8` 对应旧教程的 `armvirt/64` 使用场景；这里只取通用目标的 `rootfs.tar.gz`，
实际启动镜像由 N1 专用脚本生成，不能把通用 ARM EFI 镜像刷入 N1。

构建会检查实际安装包、Vantage 主题资产、仪表盘与两份中文翻译、默认主题、
代理内核、Btrfs 的 Zstd 动态库依赖，以及最终镜像的分区边界与文件系统大小。
这些检查不能替代真实 N1 启动测试。先 U 盘验证，再考虑写入 eMMC。
构建记录、安装清单、锁文件及 SDK 记录随固件提供。
详细步骤见 [首次启动说明](docs/FIRST-BOOT.md)。

## 晶晨宝盒在线升级

晶晨宝盒来自 [ophub/luci-app-amlogic](https://github.com/ophub/luci-app-amlogic) 的 JS 发布包，
带中文翻译，提供 eMMC 安装、备份、手动上传及在线更新入口。

- 完整固件源指向本仓库，Releases 标签筛选 `N1-`。
- 内核源为 `ophub/kernel` 的 `kernel_flippy`，筛选 6.12 系列。
- Actions Artifact 不能直接作为公开在线更新源。
- 构建时主动勾选 `publish_release` 后，成功产物才会发布为 `N1-运行编号` Release。
- 默认不发布；也可下载 Artifact 后手动上传镜像。

eMMC 安装及在线升级仍需实机验证。操作前备份并保留可启动 U 盘。
不要从通用官方源强制安装与 Flippy 内核不匹配的 `kmod-*`。
