# 评估

一次评估一个目录：`evaluations/<挑战>/<evaluation_id>/`。

```text
evaluation_manifest.json
config.yaml
structures/
raw_scores/
summary.tsv
```

`evaluation_id` 示例：`EGFR_E20261107A_000123`。

官方口径未确认时，`evaluation_role` 写 `proxy_evaluation`。多次预测记为 `robustness`，全部保留，不用其中的最高分替换单次结果。

结构和原始分数默认不进版本库。索引写在 `registry/evaluations.tsv`，具体指标分行写进 `registry/metrics.tsv`。pH、物种和细胞功能没有对应计算时，不另造一个分数占位。
