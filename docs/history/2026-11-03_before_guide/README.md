# Poreva Open 2026 全球 AI 蛋白质设计挑战赛

项目根目录：`DPcompetition/poreva-open-2026/`。路径使用相对位置。

这是镁伽发起、鲲鹏实验室（Megalaxy Lab）做湿实验验证的比赛。材料与 `changjiang-cup-2026/` 分开存放。两边的靶点名字即使相同，区间、分子类型、条数和截止日期也各自以自己的官方文件为准。

## 当前状态

| 项 | 内容 |
|---|---|
| 阶段 | 赛题页、四份英文文件和靶点序列已保存。团队还没报名，主攻还没锁定 |
| 第一轮提交 | 2026-10-19 至 2026-11-18，北京时间。审查通过的 24 条尽早提交；平台到点关闭 |
| 主办方确认入选序列 | 2026-11-19 至 2026-11-25 |
| 第一轮入选通知 | 2026-11-26 |
| 第二轮 | 11 月 8 日发布，提交 11 月 9 日至 12 月 8 日。第四、五题仍未公布 |
| 主攻 | 未锁定。使用说明允许多道题分开提交 |
| 格式差异 | [`docs/rules/2026-11-03_submission-conflicts.md`](docs/rules/2026-11-03_submission-conflicts.md) |
| 详细安排 | [`docs/schedule.md`](docs/schedule.md) |
| 下一次复查 | 2026-11-05，或收到 scFv / 长度的回复时 |

计算指标不是实测亲和力，也不是细胞激活结果。入选湿实验之前还有主办方遴选。

## 报名页上已经写明的提交约束

来源是 2026-11-03 的中文报名页。赛题页和平台使用说明对 scFv、长度和 CSV 列有不同写法，对照表在 [`docs/rules/2026-11-03_submission-conflicts.md`](docs/rules/2026-11-03_submission-conflicts.md)。

- 团队至少 3 人。队长邮箱使用工作单位邮箱。
- 先勾选四份文件：官方竞赛条款、平台服务条款、隐私政策、平台使用说明。
- 挑战题目：EGFR、TNF-α、GLP1R。
- 表达系统：HEK293 或无细胞。
- 分子类型：蛋白、纳米抗体、scFv、常规 IgG1 配对可变区。分子类型在页面上选，不写进序列文件。
- 序列文件为 CSV 或 Excel，恰好 24 条。三列依次是序号、序列名称、序列。序号 1 为最推荐。
- scFv 与 IgG1 写成 `VH:VL`，一个英文冒号，不加 linker。纳米抗体和蛋白是单条序列。
- 只使用 20 种标准氨基酸。每行 VH 与 VL 合计不超过 300 个氨基酸。
- 须填写使用的 AI 模型名称。
- 补充材料用于遴选：ipTM、ipSAE、自洽性、物理类指标、序列成药性评分、结构文件、方法说明。可以附链接。
- 提交文本里嵌入提示注入会被取消资格。
- 提交后要修改，联系 `poreva_open@megarobo.com`。

格式检查：

```bash
python3 tools/check_submission.py submissions/<挑战>/<版本>/sequences.csv --molecule-type protein --rules form
python3 tools/check_submission.py submissions/<挑战>/<版本>/sequences.csv --molecule-type scfv --rules guide
python3 tools/check_submission.py --self-test
```

`form` 按中文报名页，`guide` 按平台使用说明。Excel 先另存为 UTF-8 CSV 再检查。

## 目录

| 路径 | 放什么 |
|---|---|
| `docs/schedule.md` | 从 11-03 到确认日的任务、产物和停止条件 |
| `docs/rules/` | 官网、报名页和媒体材料的快照，按证据等级分开 |
| `docs/registration.md` | 报名步骤。姓名、邮箱、电话放 `docs/private/`，不进版本库 |
| `docs/submission-format.md` | 24 条序列文件的列、分子写法和长度 |
| `docs/decisions.md` | 赛题、分子类型、表达系统和工具的选择及理由 |
| `docs/questions-to-organizer.md` | 向主办方确认的问题与答复原文 |
| `docs/methods-draft.md` | 方法说明草稿，只写已经做过的步骤 |
| `docs/glossary.md` | 术语 |
| `targets/<挑战>/raw/` | 未修改的原始序列和结构 |
| `targets/<挑战>/prepared/` | 清理、裁剪、补全后的派生输入 |
| `references/literature/` | 文献索引 |
| `configs/` | 环境、生成、评估配置 |
| `vendor/` | 外部工具的锁定版本，默认不纳入版本管理 |
| `runs/<挑战>/<run_id>/` | 一次生成任务的配置、日志和原始输出 |
| `registry/` | 候选、来源、评估和指标索引 |
| `evaluations/<挑战>/<evaluation_id>/` | 一次评估的结构、原始分数和摘要 |
| `selections/<挑战>/<版本>/` | 24 条的排序、聚类和选择理由 |
| `submissions/<挑战>/<版本>/` | 冻结的提交包、哈希和回执 |
| `official_results/` | 主办方原始结果和派生分析 |
| `reports/daily/` | 每日一页状态 |
| `tools/check_submission.py` | 序列文件格式检查 |

`runs/`、`evaluations/`、`selections/`、`submissions/` 在对应挑战真正开始后再建子目录。目录里不放假序列、假分数或假回执。

## 四种 ID

| 标识 | 示例 | 含义 |
|---|---|---|
| `run_id` | `EGFR_20261106T090000+0800_R01` | 一次生成任务 |
| `candidate_id` | `EGFR_R20261106A_C000123` | 一条候选在一道挑战上的永久身份 |
| `evaluation_id` | `EGFR_E20261107A_000123` | 某候选在固定条件下的一次评估 |
| `submission_version` | `20261117_v01` | 一次冻结的提交包 |

精确相同的序列在同一挑战内按 `sequence_sha256` 合并身份，并保留全部生成来源。序列发生变化时新建候选，并填写父候选 ID。同一字符串用于另一道挑战时另建候选，不合并身份。

## 下一步

按 [`docs/schedule.md`](docs/schedule.md)：报名、阅读 `docs/rules/legal/`、把 Q-01 到 Q-03 发到 `poreva_open@megarobo.com`。字段定义在 [`registry/schema.md`](registry/schema.md)。
