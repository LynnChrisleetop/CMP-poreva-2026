# Poreva 三题目标规格与参考结构复核

核查日期：2026-11-03。范围是五个目标／物种构建的来源和结构语义，不生成设计候选，也不认证实验样品的真实组成。

## 序列规格

| 目标 | UniProt | 官方区间（1-based，含端点） | aa | 与本轮 UniProt 切片 |
|---|---|---|---:|---|
| 人 EGFR | P00533 | 25–645 | 621 | 完全相同 |
| 鼠 EGFR | Q01279 | 25–647 | 623 | 完全相同 |
| 人 TNF-α | P01375 | 77–233 | 157 | 完全相同 |
| 鼠 TNF-α | P06804 | 80–235 | 156 | 完全相同 |
| 人 GLP1R | P43220 | 24–432 | 409 | 完全相同，但只是 WT 参考 |

区间及实验说明来源：[EGFR 官方题目](https://porevaopen.megalaxylab.com/challenges/egfr)、[TNF-α 官方题目](https://porevaopen.megalaxylab.com/challenges/tnf-alpha)、[GLP1R 官方题目](https://porevaopen.megalaxylab.com/challenges/glp1r)。序列独立核对所用完整 UniProt JSON 已保存，下载清单包含精确 URL、时间和 SHA256。

## 结构语义与不能忽略的差异

| 参考 | 选取链 | 目标内观测 CA | 必须保留的解释 |
|---|---|---:|---|
| 6ARU | auth A / label A | 609 / 621 | 受体与 Fab 复合体；assembly1 不是 EGFR 同源三聚体 |
| AF-Q01279-F1 v6 | A | 待统一工具复核 | AFDB 单链预测；不是实验结构，也不能据此认证跨种结合 |
| 1TNF | A、B、C | 每链 152 / 157 | 生物学三聚体；缺 UniProt77–81 的坐标 |
| 2TNF | A、B、C | 每链 148 / 156 | 生物学三聚体；缺 UniProt80–87 的坐标 |
| 6X18 | auth R / label F（entity6） | 384 / 409 | 带配体、G 蛋白和 Nb35 的复合体；不是 GLP1R 六聚体 |

实验原件：[6ARU](https://files.rcsb.org/download/6ARU.cif)、[1TNF](https://files.rcsb.org/download/1TNF.cif)、[2TNF](https://files.rcsb.org/download/2TNF.cif)、[6X18](https://files.rcsb.org/download/6X18.cif)。各自 assembly1 原件也已保存。鼠 EGFR 使用 [AlphaFold DB API](https://alphafold.ebi.ac.uk/api/prediction/Q01279) 返回的版本化下载地址；不手工猜测版本。

- **6ARU 不覆盖完整官方构建。** 映射构建止于 UniProt640，641–645不在该参考构建；25–27和637–640有序列记录但缺坐标。不得把尾端表达标签误映射成641–645。
- **6ARU 有两处目标序列差异。** Biopython复核CIF `_struct_ref_seq_dif`，UniProt540 N→K（label516）、UniProt634 E→R（label610）均标 `conflict`。链A label617–622是6个His标签，应排除。数据库概要的 Mutation0 不能替代逐残基序列检查。
- **2TNF 的映射表存在长度不一致。** `_struct_ref_seq` 写 label1–155 对应 UniProt80–235，但实体序列实际有156位且与官方156 aa完全相同。正确处理应由序列对齐和 `_pdbx_poly_seq_scheme` 交叉验证，不能盲用末端索引。本地复核已用全部156个单体序列残基验证，观测数148／链。
- **1TNF 不是完整的当前WT参考。** 当前实体序列及三条链的label/auth143原子残基均为LEU，而当前UniProt219为ASP，故实际差异是D219L。旧 `_struct_ref_seq_dif` 的ASP45／LEU219条目与当前实体／原子不一致；保留该历史注释，但不能以它覆盖实际比对结论。
- **6X18 有一个目标内序列差异。** UniProt260是L，结构实体及坐标是F；CIF标为 `conflict`。应记录为 L260F 差异，不静默修成WT。目标24–432中的缺坐标区间为24–28、130–135、339–343、424–432。
- **6X18 标签边界明确。** 受体label1–32不属于UniProt（首位起始Met，其余为表达标签），label473–491为C端标签。Poreva目标24–432对应label33–441；链编号转换必须区分label F和auth R。
- **GLP1R 实验构建仍未明确。** 官方说实验靶标含未公开的热稳定突变、FLAG和His标签。WT参考及6X18均不能替代真实实验构建认证；需要主办方提供突变清单或表位适用说明。结构支持结合可行性研究，不能证明激动功能。
- 保留完整原始复合体、糖链和溶剂记录供上下文审查；目标蛋白坐标可另存提取版。未补环、未突变修复、未模拟糖链，因此这些提取结构只能标为保留原始缺口的参考输入。

## 本地交付

- `poreva_specs.json`：五个构建规格、链、区间、UniProt特征和注意事项。
- `sources/`：5份UniProt JSON、4个实验结构及各自assembly1、鼠EGFR的AFDB JSON和预测CIF。
- `download_manifest.json`：15个源文件的可追溯记录。
- `cif_observation_review.json`：原件中目标链、映射表、坐标缺失与范围复核。
- `biopython_tag_crosscheck.json`：标签边界及当前UniProt相对实体的逐位差异。
- `preview_independent_verification.json`：9份预审映射独立检查全部通过，包含输入哈希、逐链计数与1TNF原子直接证据。鼠EGFR目标623位均有CA，但仍是预测结构。

`inspect_cif.py` 是此次审查脚本，检查所需CIF表的列数和单行行形；最终项目残基映射和准备结构应以统一的 Biopython 流程及其验收结果为准。
