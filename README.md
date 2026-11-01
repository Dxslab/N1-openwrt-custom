# N1 精简旁路由固件

通过 GitHub Actions 编译 ImmortalWrt 24.10 的 ARM64 rootfs，再由
[Flippy/openwrt_packit](https://github.com/unifreq/openwrt_packit) 打包为斐讯 N1 镜像。
首轮构建选用 Flippy 6.12.114 内核包、OpenClash、ARM64 Mihomo 代理内核和晶晨宝盒。
源码、feeds、打包工具和代理内核均锁定版本，实际构建记录随固件提供。

## 如何构建

1. 打开仓库的 **Actions** 页面。
2. 如提示，启用 GitHub Actions。
3. 选择 **Build N1 OpenWrt** → **Run workflow** → **Run workflow**。
4. 等待构建成功，在本次运行页面下方下载 **N1-firmware-数字**。
5. 解开产物 ZIP，使用其中 `openwrt_s905d_n1_*.img.gz` 制作启动 U 盘。

工作流只接受手动触发，不会定时编译，不需要个人访问令牌。
默认只上传 Actions 构建产物；只有运行时主动勾选 `publish_release`，才会发布到 Releases。
首次编译需要较长时间。若失败，下载同一运行中的 `N1-build-logs-数字` 用于排查。

## 默认设置

| 项目 | 设置 |
|---|---|
| N1 管理地址 | `192.168.1.2` |
| IPv4 上游网关、DNS | `192.168.1.1` |
| DHCP 服务 | 关闭，由主路由负责 |
| N1 的 IPv6、Wi-Fi | 关闭，主路由继续提供直连 IPv6 |
| 防火墙 | Firewall4 / nftables，流量卸载关闭 |
| 功能插件 | OpenClash、晶晨宝盒、网页终端；保留防火墙和软件包管理 |
| 代理初始状态 | 关闭，导入自己的配置后再启用 |
| 密码、代理订阅 | 不写入仓库或镜像，首次登录后设置 |
| 根文件系统 | openwrt_packit 创建的 Btrfs |

保留打包项目要求的磁盘、压缩、Perl、Bash 等维护依赖，不添加下载、NAS、Docker、去广告和其他代理工具。
主路由故障回退配置另行实施；仅刷入该镜像不会自动让所有设备经过 N1。

## README 必选依赖核对

旧版教程的 `QEMU ARM Virtual Machine / armvirt/64` 在所选 24.10 源码中使用
`Arm SystemReady / armsr/armv8 / Generic EFI Boot` 构建目标；这里只取生成的
`rootfs.tar.gz` 作为输入，再由 N1 专用脚本制作实际启动镜像。

`configs/n1.config` 已选择打包项目列出的基础依赖：Perl 及指定模块、blkid/fdisk/lsblk/parted、
attr/btrfs-progs（启用 Zstd）/chattr/dosfstools/e2fsprogs/f2fs/xfs 工具、bsdtar/pigz、
bash/gawk/getopt/losetup/tar/uuidgen。`check-config.py` 会在 `make defconfig` 后逐项检查。
检查 LuCI 应用时，以 `.packageinfo` 的真实包名为准，不会把未安装应用的 `INCLUDE_*` 子选项误判成应用。

不选择针对其他用途的可选依赖：N1 关闭 Wi-Fi，因此不额外添加 Wi-Fi 服务；
不使用 KVM、Photonicat 或 Netdata，因此不添加 acpid、pcat-manager 和相关 Python 监控栈。

## 验证与安装

构建会核查选包、rootfs 必需文件、Mihomo 下载摘要，以及最终镜像的分区边界和 Btrfs 大小。
这些检查不能代替真实 N1 上的启动和代理测试。**先 U 盘启动测试，再考虑覆盖 eMMC。**
详细步骤见 [首次启动说明](docs/FIRST-BOOT.md)。

更换版本时需要同时核对源码、feeds、OpenClash 及 Flippy 内核兼容性，避免强制安装其他内核的模块。

## 晶晨宝盒与在线升级

预装 `ophub/luci-app-amlogic` 的 JS 分支，源码锁定在工作流的 `AMLOGIC_COMMIT`。
支持通过网页调用配套脚本进行 eMMC 安装、手动上传更新、内核更新及备份等操作。

- 完整固件更新源指向本仓库，Releases 标签筛选词为 `N1-`。
- 内核源指向 `ophub/kernel` 的 `kernel_flippy`，默认筛选 6.12 系列。
- Actions 的 Artifact 不能直接作为插件的公开在线更新源。
- 确认固件配置和 U 盘启动可用后，可在新一次构建时勾选 `publish_release`。
  成功的构建将创建 `N1-运行编号` Release，附带完整镜像和摘要文件；
  仓库存在这样的公开 Release 后，插件才有可用的本仓库在线固件。
- 不勾选发布选项时，仍可下载 Artifact 解压后，在晶晨宝盒中手动上传镜像升级。
- 请先保留一个已验证可启动的 U 盘。结构检查不代表在线升级和 eMMC 启动已经经过实机验证。
