<title>00 从这里开始</title>

> **欢迎来到 Trisol**

> 这是给「从未用过 Trisol」的同学（和你们的 AI agent）准备的入口页。读完之后，你应该清楚：Trisol 能帮你做什么、你该走哪条路、第一步该点哪里。

# 1. Trisol 是什么

Trisol 是公司内部的一体化机器学习平台。把从**模型管理**、**训练**、**算力分配**到**推理服务上线**的全链路收敛在同一个产品里 —— 你不必再手写 Helm、不必登跳板机、不必和别的团队抢 GPU。

详细的产品定位、命名由来、与现有工具的对比，见 [1.1 产品定位与价值](https://dptechnology.feishu.cn/wiki/P9dEwcfx7i4iwnkZsJQcFydPnsg)。

# 2. Trisol 不做什么

- 不做**数据标注 / 特征工程 / 实验管理**（规划中）
- 不是代码仓库（继续用 GitLab）
- 不自建账号体系（登录走玻尔 SSO：选「企业版登录」，企业代码 `dpt`）
- 不替代 Kubernetes（Trisol 是 K8s 之上的产品化封装）

# 3. 你属于哪类用户？

Trisol 的用户主要分两类，走的路完全不同。选对路，能少走 80% 弯路。

## 1. Human 用户 —— 从 Web UI 走

打开 [trisol.dp.tech](https://trisol.dp.tech) → ENTER CONSOLE → 跳转到玻尔（Bohrium）登录页：**点「企业版登录（B 端）**，不要用微信/邮箱/手机号等个人版（C 端）方式 → 企业代码输 `dpt` → 点「飞书授权登录」。所有操作都在 Web UI 完成。按你的角色读对应路径：

![这是一张玻尔平台的登录界面截图，页面顶部有标注为“中文”的切换选项，用红色箭头和文字提示需先切换到中文。界面主体为微信扫码登录区域，中间有微信扫码的二维码，二维码上方标注“使用 WeChat 扫码登录”，下方有蓝色的“同意并继续”按钮，还提示需勾选同意相关协议后扫码登录。界面底部的其他登录方式中，“企业版登录”选项被红框标注，是该登录界面的核心提示内容。](https://feishu.cn/file/SXRZbTwmzorZ51xiWWncuJkTnAd)



![② 企业代码输入 dpt，点「下一步」](https://feishu.cn/file/Om3fbY3j0oqsdxxJKfIcsXbAnrf)

![③ 深势科技企业页：点「飞书授权登录」完成](https://feishu.cn/file/RBsvbq7pIoLtfwx6kWnc0kJNnub)

| 角色 | 典型场景 | 建议阅读路径 |
|-|-|-|
| **算法 / 应用开发者**（绝大多数人） | 训了个模型想上线；做应用要调线上推理；想跟踪自家服务跑得怎么样 | [0 准备工作](https://dptechnology.feishu.cn/wiki/Mw0Nwbo97iMyp8kqbImcg4Fznie) → [1 加入团队](https://dptechnology.feishu.cn/wiki/U1phwPadgiAYpwkL9OwcTEURnPc) → [2 上传模型](https://dptechnology.feishu.cn/wiki/X6vZwopOeimLvzkWYsGcZ4jmn5c) → [3 上线推理服务](https://dptechnology.feishu.cn/wiki/NnoSwMYE3iI3B7kN6m1cH6lsnp3) → [4 查日志排查](https://dptechnology.feishu.cn/wiki/B6JpwPmJ1iEzEnkPiWOcwfg4ndH) |
| **团队管理员** | 给团队成员审批加入；分配本团队 GPU 配额；看团队整体资源占用 | 先读「算法路径」的 [0](https://dptechnology.feishu.cn/wiki/Mw0Nwbo97iMyp8kqbImcg4Fznie) / [1](https://dptechnology.feishu.cn/wiki/U1phwPadgiAYpwkL9OwcTEURnPc)，再读 [2.2 团队与成员](https://dptechnology.feishu.cn/wiki/AlvWwUHP5iRhTDkmRkzcN3G4nIf) + [2.3 算力与配额](https://dptechnology.feishu.cn/wiki/A8lowPReMiItIIkJAC8cP5ZTncb) |
| **平台管理员** | 纳管新集群；做全局配额规划；跨团队运维 | 先读 [02 能力详解](https://dptechnology.feishu.cn/wiki/MFBBwMBQziabtjkWC5YckK87nLh)，再读运维相关章节 |

## 2. CLI Agent —— 从 CLI + skill 走

你的 AI agent（Claude Code / Kimi / Codex 等）可以直接替你操作 Trisol。Trisol 是 **CLI/API 优先（agent-friendly）**设计的：几乎所有命令支持 `-o json`，响应里 ID 旁边一定带人类可读的 name，agent 不用猜。

- 装 CLI：`curl -fsSL https://trisol.dp.tech/install.sh | bash`（检测到 Claude Code 时会自动装 agent skill；skill 也内嵌在 CLI 二进制里，`trisol skill update` 随时装/更新）
- 登录：`trisol login` 会拉起浏览器，走的也是上面那条玻尔企业版链（企业版登录 → 企业代码 `dpt` → 飞书授权）；headless / 远程机器用 `trisol login --device`（打印 URL + 验证码，人在任意浏览器打开完成同样的授权）
- agent 读 skill 拿到命令依赖图和解析逻辑（自动解析 version_code / cluster / gpu-model），再调 CLI 真正干活：上传模型、起训练、部署推理一条龙
- 详见 [2.10 CLI 与 Agent Skill](https://dptechnology.feishu.cn/wiki/K7WRwTUHDikxAvkKO5Sc0oWintf)；UI 操作和 CLI 命令的对应关系见 [附录：UI / CLI 能力对照表](https://dptechnology.feishu.cn/wiki/GRXMwinqpiQkhOkcPt6cpK22n6b)

# 4. Human 用户的 5 分钟首条路径

不知道从哪儿开始？跟着这条最短路走一遍，你就完整体验了 Trisol 的核心闭环：

1. **登录** —— 打开 [trisol.dp.tech](https://trisol.dp.tech) → ENTER CONSOLE → 玻尔页点「企业版登录」（企业代码 `dpt`）→ 飞书授权
2. **加入一个团队** —— 在「团队」页找到归属团队，提交加入申请，等管理员通过
3. **看一个跑着的推理服务** —— 进「推理服务」列表，点任意一个进详情，看实时日志和监控面板
4. **逛一圈模型库** —— 进「模型」页看本团队已经管了哪些模型、各有哪些版本、文件结构长啥样
5. **想动手起一个自己的** —— 跳到 [2 上传并管理模型版本](https://dptechnology.feishu.cn/wiki/X6vZwopOeimLvzkWYsGcZ4jmn5c) 再跳 [3 上线一个推理服务](https://dptechnology.feishu.cn/wiki/NnoSwMYE3iI3B7kN6m1cH6lsnp3)

# 5. 阅读地图

| 章节 | 什么时候来读 |
|-|-|
| [01 产品介绍](https://dptechnology.feishu.cn/wiki/W1gIw0tWvi4XjKk6heicss0Enhd) | 想搞清楚「Trisol 到底是什么 / 解决什么问题」的时候 |
| [02 能力详解](https://dptechnology.feishu.cn/wiki/MFBBwMBQziabtjkWC5YckK87nLh) | 已经在用了，想深挖某个具体模块（推理服务 / 模型 / 配额 ...） |
| [03 快速上手](https://dptechnology.feishu.cn/wiki/BotmwWAX4iWkMykOiAYcSs70nZp) | 动手做一件事的时候 —— 上线服务、上传模型、查日志、配配额 |
| [04 Release Notes](https://dptechnology.feishu.cn/wiki/SXnTw5roMiJEiNkzOjLcFJeknBd) | 关心版本更新、新能力上线 |
| [05 常见问题](https://dptechnology.feishu.cn/wiki/R6GTwJnGliVQ8akidN8cOUZfn8B) | 新人常见问题（FAQ）、用户问题台账 —— 遇到问题先翻翻，可能已经有人踩过坑 |

---

> **找不到答案？** 先去 [05 常见问题](https://dptechnology.feishu.cn/wiki/R6GTwJnGliVQ8akidN8cOUZfn8B) 翻 FAQ 和问题台账，还没有就在文档上批注。Trisol 还很新，每条反馈都会被认真处理。