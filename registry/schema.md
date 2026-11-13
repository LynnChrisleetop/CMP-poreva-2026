# 记录字段

这些表是内部索引。提交文件只用官网模板的三列。表头以登录后下载的模板为准。

单位写在本文件里。置信度要标明 0–1 还是 0–100。距离用 Å。实测亲和力保留原始单位，并另设换算列。耗时分开写秒、墙钟小时和 GPU 小时。缺失用 `NA` 或空值，不用 0。

## `registry/candidates.tsv`

一条候选在一道挑战上占一行。`sequence` 是拟提交的字符串。

| 字段 | 含义 |
|---|---|
| `candidate_id` | 永久 ID，不含当前排名 |
| `challenge_id` | `EGFR`、`TNFA` 或 `GLP1R` |
| `molecule_type` | `protein`、`vhh`、`scfv` 或 `igg1` |
| `expression_system` | `HEK293`、`cell_free` 或 `undecided` |
| `sequence_name` | 拟用的序列名称。未命名留空 |
| `priority_rank` | 进入某版 24 条名单后的序号。未入选留空 |
| `sequence` | 提交字符串。配对序列保留一个英文冒号 |
| `vh_sequence` | 配对序列的 VH。单链留空 |
| `vl_sequence` | 配对序列的 VL。单链留空 |
| `length_aa` | 不计冒号的氨基酸数 |
| `sequence_sha256` | 归一化序列的 SHA-256 |
| `first_generated_at` | 首次生成时间，含时区 |
| `origin_run_id` | 首次出现的运行 |
| `parent_candidate_id` | 有父设计时填写。从头生成留空 |
| `target_manifest_sha256` | 当时使用的靶点 manifest |
| `design_model` | 实际设计工具和版本 |
| `folding_model` | 实际折叠或复预测工具和版本。没有则留空 |
| `generation_config_sha256` | 实际配置哈希 |
| `status` | 如 `generated`、`rejected`、`shortlisted`、`submitted` |
| `rejection_reason` | 淘汰原因。未淘汰留空 |

同一挑战里精确相同的序列合并为同一 `candidate_id`，来源写进 `provenance.jsonl`。另一道挑战即使字符串相同也另建候选。

## `registry/provenance.jsonl`

同一序列的多来源和父子关系，每行一个 JSON 对象。

建议字段：`candidate_id`、`sequence_sha256`、`run_id`、`source_path`、`parent_candidate_id`、`recorded_at`。

## `registry/evaluations.tsv`

一次评估一行。原始分数放在 `evaluations/<挑战>/<evaluation_id>/`。缺失分数不写进索引冒充低分。

| 字段 | 含义 |
|---|---|
| `evaluation_id` | 一次评估 |
| `candidate_id` | 对应候选 |
| `sequence_sha256` | 被评估的序列 |
| `challenge_id` | 挑战 |
| `target_manifest_sha256` | 靶点版本 |
| `evaluator_name` | 工具名 |
| `evaluator_version` | commit、release 或权重标识 |
| `evaluation_role` | `official_aligned`、`proxy_evaluation` 或 `robustness` |
| `evaluation_config_sha256` | 评估配置 |
| `seed` | 随机种子。未知写 `NA` |
| `status` | `ok`、`error` 或 `incomplete` |
| `started_at` | 开始时间 |
| `finished_at` | 结束时间 |
| `summary_path` | 相对项目根的摘要路径 |
| `notes` | 错误、链映射或未确认假设 |

一次评估绑定 `candidate_id + sequence_sha256 + target_manifest_sha256 + evaluator_version + evaluation_config_sha256 + seed`。

## `registry/metrics.tsv`

一个指标一行，挂在某次评估下面。

| 字段 | 含义 |
|---|---|
| `evaluation_id` | 对应评估 |
| `candidate_id` | 对应候选 |
| `metric_name` | 如 `ipTM`、`ipSAE`、`self_consistency`、`developability` |
| `metric_value` | 原始数值的字符串。缺失不写这一行 |
| `unit` | 无单位时留空 |
| `condition` | 如 `complex`、`monomer`、`ph_low`、`ph_neutral` |
| `species` | 如 `human`。不适用留空 |
| `ph` | 数值或留空。未在赛题确认前不自填 |
| `notes` | 链方向、阈值、实现名称 |

不同工具产出的同名指标分行记录，不覆盖。

## 运行清单

每个 `runs/<挑战>/<run_id>/run_manifest.json` 至少包含：工具名称、源码 commit 或 release、权重标识及校验值、环境、完整命令、实际配置及哈希、输入文件及哈希、随机种子、GPU 型号及显存、开始与结束时间、墙钟耗时、GPU 小时、退出码、输出路径、运行状态和失败原因。

## 算力与漏斗

`reports/compute_usage.tsv`：按比赛内的挑战和 GPU 型号记账。

`reports/funnel.tsv`：某一运行在某一筛选层留下的数量和淘汰原因。尚未检查的实验维度写 `not_checked`，不用别的分数填上。

`reports/pilot_comparison.tsv`：小试比较。不同挑战的原始分数不能当成同一把难度尺。

## 靶点 manifest

`targets/<挑战>/target_manifest.json` 在资料准备完成时创建。需要记下：

- 赛题原文文件和哈希
- UniProt 编号、异构体、区间、物种
- 功能条件：结合、释放或激活发生在什么实验读出
- 结构文件、链、装配、缺失坐标和工程突变
- 糖基化与表达构建中仍为 `unconfirmed` 的部分
- 每一步准备的输入、输出和哈希

残基映射表 `residue_map.tsv` 的列：

```text
challenge_id
species
uniprot_accession
uniprot_position
uniprot_residue
source_structure_id
source_entity_id
source_chain_id
source_residue_number
source_insertion_code
source_residue
prepared_chain_id
prepared_residue_number
prepared_residue
coordinate_status
modification_or_mutation
notes
```

`coordinate_status` 只用 `experimental`、`missing`、`modeled`。补全坐标不是新的实验结构。
