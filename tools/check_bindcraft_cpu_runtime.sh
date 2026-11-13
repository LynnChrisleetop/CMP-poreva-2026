#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/vendor/envs/bindcraft-cpu/bin/python"
export CUDA_VISIBLE_DEVICES=""
export JAX_PLATFORMS=cpu
export MPLBACKEND=Agg
export LD_LIBRARY_PATH="$ROOT/vendor/envs/bindcraft-cpu/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
REPORT="${1:-$ROOT/reports/cpu_preflight/2026-11-11}"
mkdir -p "$REPORT"
"$PY" "$ROOT/tools/preflight_bindcraft.py" \
  --settings "$ROOT/configs/generation/TNFA_bindcraft_smoke.json" \
  --pdb "$ROOT/trisol_staging/tnfa_dataset/1TNF_assembly_ABC.pdb" \
  --bindcraft "$ROOT/vendor/BindCraft" --runtime --report "$REPORT/prepared_cpu_runtime.json"
"$PY" - "$ROOT" > "$REPORT/cpu_smoke.log" 2>&1 <<'PY'
import sys
from pathlib import Path
import jax
import jax.numpy as jnp
assert all(d.platform=='cpu' for d in jax.devices()),jax.devices()
x=jnp.ones((16,16)); y=(x@x).block_until_ready()
assert float(y[0,0])==16.0
print('JAX_CPU_MATMUL_OK',jax.__version__,jax.devices(),flush=True)
import pyrosetta
pyrosetta.init('-mute all -ignore_unrecognized_res')
pdb=Path(sys.argv[1])/'trisol_staging/tnfa_dataset/1TNF_assembly_ABC.pdb'
pose=pyrosetta.pose_from_pdb(str(pdb))
assert pose.total_residue()==456,pose.total_residue()
assert pose.num_chains()==3,pose.num_chains()
print('PYROSETTA_CPU_PDB_OK',pose.total_residue(),pose.num_chains(),flush=True)
print('CPU_SMOKE_OK_NO_DESIGN_RUN',flush=True)
PY
cat "$REPORT/cpu_smoke.log"
