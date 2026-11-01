# N1 精简旁路由固件

通过 GitHub Actions 编译 ImmortalWrt 24.10 的 ARM64 rootfs，再由
[Flippy/openwrt_packit](https://github.com/unifreq/openwrt_packit) 打包为斐讯 N1 镜像。
首轮构建选用 Flippy 6.12.114 内核包、OpenClash 和 ARM64 Mihomo 代理内核。
源码、feeds、打包工具和代理内核均锁定版本，实际构建记录随固件提供。

## 如何构建

1. 打开仓库的 **Actions** 页面。
2. 如提示，启用 GitHub Actions。
3. 选择 **Build N1 OpenWrt** → **Run workflow** → **Run workflow**。
4. 等待构建成功，在本次运行页面下方下载 **N1-firmware-数字**。
5. 解开产物 ZIP，使用其中 `openwrt_s905d_n1_*.img.gz` 制作启动 U 盘。

工作流只接受手动触发，不会定时编译，不需要个人访问令牌，也不会自动发布 Release。
首次编译需要较长时间。若失败，下载同一运行中的 `N1-build-logs-数字` 用于排查。

## 默认设置

| 项目 | 设置 |
|---|---|
| N1 管理地址 | `192.168.1.2` |
| IPv4 上游网关、DNS | `192.168.1.1` |
| DHCP 服务 | 关闭，由主路由负责 |
| N1 的 IPv6、Wi-Fi | 关闭，主路由继续提供直连 IPv6 |
| 防火墙 | Firewall4 / nftables，流量卸载关闭 |
| 功能插件 | OpenClash、网页终端；保留防火墙和软件包管理 |
| 代理初始状态 | 关闭，导入自己的配置后再启用 |
| 密码、代理订阅 | 不写入仓库或镜像，首次登录后设置 |
| 根文件系统 | openwrt_packit 创建的 Btrfs |

保留打包项目要求的磁盘、压缩、Perl、Bash 等维护依赖，不添加下载、NAS、Docker、去广告和其他代理工具。
主路由故障回退配置另行实施；仅刷入该镜像不会自动让所有设备经过 N1。

## 验证与安装

构建会核查选包、rootfs 必需文件、Mihomo 下载摘要，以及最终镜像的分区边界和 Btrfs 大小。
这些检查不能代替真实 N1 上的启动和代理测试。**先 U 盘启动测试，再考虑覆盖 eMMC。**
详细步骤见 [首次启动说明](docs/FIRST-BOOT.md)。

更换版本时需要同时核对源码、feeds、OpenClash 及 Flippy 内核兼容性，避免强制安装其他内核的模块。
