# YTLitePlusEXTRA 本地整合说明

本地目录：`/Users/dou/agentSpace/YTLite`。分支：`integrate-ytliteplusextra`。

## 来源和范围

- 目标仓库：[doggy/YTLite](https://github.com/doggy/YTLite)，基础提交 `e8bb26f`。
- EXTRA 来源：[jaydenjcpy/YTLitePlusEXTRA](https://github.com/jaydenjcpy/YTLitePlusEXTRA)，提交 `f72b78cb113744c351c55a672bf4971757372827`。
- 保留目标仓库的源码、资源、README、Issue 模板与原有 Actions。加入 EXTRA 的两套 IPA 工作流、两套手动清理工作流，以及上游说明和 FAQ。未复制 `.DS_Store` 或上游 `.git`。
- 上游说明见 [原说明](YTLitePlusEXTRA-upstream.md) 和 [FAQ](YTLitePlusEXTRA-FAQ.md)。它们保留了上游历史信息；实际使用步骤以本文件为准。

EXTRA 工作流现使用历史 EXTRA cracked 流程引用的固定 `.deb`（包内版本 `5.2.1`），再编译其他插件并注入用户提供的 IPA。原有 **Create YouTube Plus app** 等入口继续使用官方发布包。它不会编译本 fork 根目录的 YTLite 源码。因此后续修改 `YTLite.x` 等源码，不会自动进入这个工作流的成品。

## 已修复的问题

- `brew install ... meason ...` 改为 `meson`，补充 `dpkg`。
- 用 Python `plistlib` 读取 XML 或二进制 `Info.plist`，支持不同的 `.app` 文件夹名称，优先取应用显示版本。拒绝网页、其他应用、缺少可执行文件或多个顶层应用的输入。
- 新增的校验只检查 IPA 结构和元数据，不验证可执行文件是否已解密。仍须提供已解密的原版 YouTube IPA。
- 下载使用失败即退出的 `curl`，cracked `.deb` 下载后验证固定 SHA256、包格式、Package、Version 和 Architecture。
- EXTRA 的应用名称、Bundle ID、IPA URL 通过环境变量传给 shell；插件版本、来源和校验值固定在工作流中；注入文件使用数组，避免空格、引号等导致参数拆分。
- 两套 EXTRA 流程统一 YTUHD 来源、递归子模块和 `SIDELOAD=1`，安装其视频解码库所需构建工具，使用上游标准流程中的 iPhoneOS26.5 SDK 和 Logos 提交。
- 原有工作流中的 Safari 扩展目录统一为实际的 `OpenYouTubeSafariExtension.appex`，去除标准 IPA / Cyan 流程重复加入的 `ytplus.deb`。
- 去除原辅助工作流中同时标记 `required: true` 和 `default: false` 的冗余默认值。
- 新工作流发布文件缺失会报错；成品写入 Draft Release。清理工作流仅手动触发，执行时会按所选条件删除内容。

## 推送后怎样试打包

1. 将整合内容合并或推送到仓库默认分支。新的手动工作流通常需要先存在于默认分支，Actions 才会出现运行入口。本地提交不会触发远程构建。
2. 在 GitHub 的 Actions 页面启用 fork 的工作流。打包任务已显式声明 `contents: write` 权限；如组织策略禁止写入，需要先调整该策略。
3. 选择 **Build YTLitePlusEXTRA IPA (Cracked)**（文件 `build.yml`）。不要将原有的 **Create YouTube Plus app** 误认为 EXTRA 流程。
4. 输入已解密原版 YouTube IPA 的下载直链。标准 EXTRA 流程还保留了上游的 MEGA 分享链接支持；无 YTLite 流程只接受直链。
5. 当前 cracked 包的元数据固定为 `5.2.1`，不再提供手动修改版本号的输入框；保留默认显示名称和 Bundle ID 即可。`demc` 与 `volboost` 是可选插件开关。
6. 成功后在本仓库的 **Releases** 找到 Draft，下载 IPA，再按你的侧载方式签名和安装。

原有官方包入口中，YTLite 5.2 起仍要求开发者会员。当前 EXTRA cracked 入口使用单独的第三方包；其包内版本为 `5.2.1`，确切二进制基版未确认，不能将官方 5.2.2 的兼容性说明直接套用到它。破解效果、YouTube 兼容性及设备运行情况尚未实测。无 YTLite 流程只注入其他插件，不包含 YTLite 本身的功能。


## 当前 cracked deb 来源（2026-10-26）

- 直链：`https://files.catbox.moe/l2pfst.deb`。
- 来源证据：[EXTRA 历史工作流](https://github.com/jaydenjcpy/YTLitePlusEXTRA/blob/1994eabe19b819a18d48a35001c522b39c207a9c/.github/workflows/YTLiteCracked.yml#L100)。
- SHA256：`2c2cd90394625f8b830aaa5669337a21482590639043222c93bfcd830b0e09a1`。
- 包元数据：`com.dvntm.ytlite` / `5.2.1` / `iphoneos-arm`；主库实际是 ARM64。
- 二进制没有复制进本仓库；工作流运行时下载。链接失效、文件被替换或元数据不匹配会直接停止，避免静默使用另一份文件。
- 成品及 Draft Release 名称包含 `_v5.2.1_cracked`；SHA256 校验只确认文件一致性，不代表运行安全或功能兼容性。

## 本地验证

2026-10-25 初次验证；2026-10-26 接入 cracked 包后复查：

- `actionlint 1.7.12 -shellcheck= -pyflakes=` 检查全部 8 个工作流通过；未运行 ShellCheck / Pyflakes。
- YAML 解析及所有工作流 `run` 脚本的 `bash -n` 语法检查通过。
- `python3 -m unittest discover -s tests -v`：7 项测试通过，涵盖二进制/XML plist、重命名 app、Actions 环境输出和无效输入。
- 初次核对 Actions 引用版本、插件仓库、SDK 目录及官方 YTLite 5.2.2 发布资源；当前 EXTRA 的固定 cracked 包来源和元数据见上节。
- 使用当前工作流中的 SHA256 校验代码验证已下载文件通过，错误校验值会以非零状态退出；固定版本与输入引用检查通过。
- `git diff --check` 通过。

尚未进行完整插件编译、真实 IPA 注入、签名、设备安装和播放测试。动态拉取的插件源码仍可能发生依赖或兼容性变化，配置检查通过不能替代首次 GitHub Actions 构建。
