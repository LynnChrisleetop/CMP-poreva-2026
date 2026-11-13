# 提交包

一次冻结提交一个目录：`submissions/<挑战>/<submission_version>/`。版本示例：`20261117_v01`。

```text
sequences.csv
review_packet.md
candidate_mapping.tsv
manifest.json
checksums.sha256
receipts/
```

`sequences.csv` 按官网模板导出，再用 `tools/check_submission.py` 重读。`candidate_mapping.tsv` 把序号和序列名称映回 `candidate_id`。`receipts/` 可能含身份信息，默认不进版本库。

状态只用：`prepared`、`uploaded_draft`、`confirmed_submitted`、`superseded`、`uncertain`。保存草稿不算完成。

页面上的挑战、分子类型、表达系统和模型名称写进 `manifest.json`，并与 CSV 一起做哈希。
