#!/usr/bin/env bash
# Execute only INSIDE the prepared runtime. Does not allocate/submit a GPU.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
: "${BINDCRAFT_PYTHON:?Set the absolute path of the validated BindCraft Python}"
: "${BINDCRAFT_DIR:?Set the absolute path of the validated BindCraft source}"
BC="$(cd "$BINDCRAFT_DIR" && pwd)"
OUT="${BINDCRAFT_OUTPUT:-/trisol/output}"
LIMIT="${BINDCRAFT_TIMEOUT_SECONDS:-3600}"
[[ "$BINDCRAFT_PYTHON" = /* && -x "$BINDCRAFT_PYTHON" ]] || exit 2
[[ "$LIMIT" =~ ^[1-9][0-9]*$ ]] || exit 2
export LD_LIBRARY_PATH="$(dirname "$(dirname "$BINDCRAFT_PYTHON")")/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
command -v timeout >/dev/null
mkdir -p "$OUT"
"$BINDCRAFT_PYTHON" "$ROOT/tools/preflight_bindcraft.py" \
  --settings "$ROOT/configs/generation/TNFA_bindcraft_smoke.json" \
  --bindcraft "$BC" --runtime --report "$OUT/cpu_runtime_preflight.json"
"$BINDCRAFT_PYTHON" -c 'import jax; devices=jax.devices(); print(devices); assert any(d.platform == "gpu" for d in devices), "JAX GPU backend unavailable"'
"$BINDCRAFT_PYTHON" - "$ROOT" "$OUT" <<'PY'
import json,sys
from pathlib import Path
root,out=map(Path,sys.argv[1:])
s=json.loads((root/'configs/generation/TNFA_bindcraft_smoke.json').read_text())
s['design_path']=str(out/'designs')
(out/'settings.json').write_text(json.dumps(s,indent=2)+'\n')
PY
cd "$BC"
# max_trajectories counts relaxed outputs, not all failed attempts; wall time is the hard bound.
set +e
timeout --signal=TERM --kill-after=30s "${LIMIT}s" "$BINDCRAFT_PYTHON" -u "$BC/bindcraft.py" \
  --settings "$OUT/settings.json" \
  --advanced "$ROOT/configs/generation/TNFA_bindcraft_smoke_advanced.json" \
  --filters "$ROOT/configs/generation/TNFA_bindcraft_smoke_filters.json" 2>&1 | tee "$OUT/design.log"
RC=${PIPESTATUS[0]}
set -e
printf '{"exit_code":%s,"timeout_seconds":%s}\n' "$RC" "$LIMIT" > "$OUT/process_status.json"
exit "$RC"
