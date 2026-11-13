# 辅助脚本

> **适用范围补记（2026-11-03）：**`check_submission.py`已支持`--rules form`和`--rules guide`两套检查。两套实现不能替官方解决格式冲突，尤其FAQ的单链>40与包含40的范围仍有差异；正式导出前结合[规则审计](../docs/rules/2026-11-03_scoring-audit.md)复核。本轮未修改脚本代码，也不把项目已有自测记录当作本轮重新运行结果。

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

## 2026-11-11 CPU 预检

- `bootstrap_gpu_design.sh`：保留旧文件名，但已改为无 GPU 的固定版本 BindCraft 源码准备；不再克隆 BindCraft2。原文件备份为同目录 `.sh.pre-cpu-prep-20261111`。
- `preflight_bindcraft.py`：默认检查配置和 PDB；`--runtime` 在 CPU 模式下逐项验证依赖、原生库和模型权重。不会生成序列、提交任务或申请 GPU。
- `run_bindcraft_smoke.sh`：在以后已准备好的运行环境内执行；明确指定 Python 和源码路径，CPU 预检通过后检查 JAX GPU，再限时运行。默认 3600 秒，超时返回 124。此脚本本身不提交 Trisol 任务。
- 小试配置在 `configs/generation/TNFA_bindcraft_smoke*.json`。`max_trajectories=2` 计数的是已松弛轨迹，不能代替硬超时。

详见 `../docs/CPU准备_2026-11-11.md`。不要把 CPU 专用 JAX 环境直接认定为 GPU 镜像可用。
