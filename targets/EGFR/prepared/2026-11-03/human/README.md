# 靶点结构输入包审查

目标：EGFR；比赛：poreva-open-2026；物种：human。

官方序列：621 aa；UniProt：P00533，1-based闭区间 25–645。

官方序列与UniProt指定切片完全一致：是。

## 如何使用

- `sequence_review.json` 保留序列校验、UniProt功能区注释和N-X-S/T序列位点。序列位点不等于糖链占位。
- `*.residue_map.tsv` 对每条接受的目标链逐一列出所有官方目标残基，包括没有坐标的残基。编号不连续与插入码均保留。
- `*.target_observed.cif` 只包含已观测到的目标原子。没有补齐缺口、修复突变、添加糖链或优化结构；必须结合原始完整结构审查。
- `*.summary.json` 记录链筛选、覆盖率、变异、糖链、其它分子、装配操作和警告。工具不自行把非对称单元扩展成生物学装配。
- 映射由全长参考序列与沉积聚合物序列比对推断，并非SIFTS映射。预测结构必须按预测证据使用。

## 结构检查结果

| 结构 | 证据类型 | 目标链（label/auth） | 有CA坐标/官方长度 | 序列差异位点数 |
|---|---|---|---:|---:|
| 6ARU | experimental | A/A | 609/621 | 2 |
| 6ARU_assembly | experimental | A/A | 609/621 | 2 |

## 仍需审查

- **6ARU**：Reference has substitutions or microheterogeneity relative to the official target; coordinates have NOT been corrected.
- **6ARU**：Coordinates do not cover the entire official target; missing regions have NOT been reconstructed.
- **6ARU**：Deposited glycan coordinates exist in raw context and are omitted from the target-only subset; review steric accessibility against raw context.
- **6ARU_assembly**：Reference has substitutions or microheterogeneity relative to the official target; coordinates have NOT been corrected.
- **6ARU_assembly**：Coordinates do not cover the entire official target; missing regions have NOT been reconstructed.
- **6ARU_assembly**：Deposited glycan coordinates exist in raw context and are omitted from the target-only subset; review steric accessibility against raw context.

上述文件是来源明确的参考输入与映射，不代表已经验证结合、表达、pH行为或功能，也不表示完整模型输入已满足某个特定设计软件的要求。
