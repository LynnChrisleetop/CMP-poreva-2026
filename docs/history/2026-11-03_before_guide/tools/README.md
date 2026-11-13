# 辅助脚本

| 脚本 | 状态 | 作用 |
|---|---|---|
| `check_submission.py` | 已实现 | `--rules form` 按中文报名页；`--rules guide` 按平台使用说明。自测 25 项 |

```bash
python3 tools/check_submission.py --self-test
python3 tools/check_submission.py path/to/sequences.csv --molecule-type protein --rules form
python3 tools/check_submission.py path/to/sequences.csv --molecule-type scfv --rules guide
```

官方模板若改表头，先改脚本顶部的 `EXPECTED_HEADER`，再用 `--self-test` 确认脚本本身仍然可用。

格式检查不管科学问题。配对序列仍要人工确认冒号两侧是 VH 和 VL，且没有把 linker 写进某一侧。
