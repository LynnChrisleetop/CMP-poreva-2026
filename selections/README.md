# 候选组合

冻结某一版 24 条时，再建 `selections/<挑战>/<selection_version>/`：

```text
shortlist.tsv
clusters.tsv
structure_review.md
selection_notes.md
```

版本示例：`20261116_v01`。

每条入选序列写一句它相对其余序列多回答的问题。被排除的高分候选也记下原因。替换时新建版本，不覆盖旧清单。

报名页要求文件恰好 24 条。凑满 24 条时仍然去掉精确重复和没有来源的序列。同一骨架的微变体若占多于一个名额，要写明它们检验的假设。

`shortlist.tsv` 至少包含：`priority_rank`、`candidate_id`、`sequence_name`、`sequence_sha256`、`selection_reason`。
