#!/bin/bash
set -euo pipefail
export BINDCRAFT_PYTHON=/opt/bindcraft-env/bin/python
export BINDCRAFT_DIR=/opt/BindCraft
export PATH="/opt/bindcraft-env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export LD_LIBRARY_PATH="/opt/bindcraft-env/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export MPLBACKEND=Agg
MODE="${1:-cpu-check}"
case "$MODE" in
  cpu-check)
    export CUDA_VISIBLE_DEVICES=""
    export JAX_PLATFORMS=cpu
    REPORT="${CPU_REPORT_DIR:-/tmp/poreva-cpu-check}"
    mkdir -p "$REPORT"
    "$BINDCRAFT_PYTHON" /opt/poreva/tools/preflight_bindcraft.py --settings /opt/poreva/configs/generation/TNFA_bindcraft_smoke.json --pdb /opt/poreva/tests/tnfa.pdb --bindcraft "$BINDCRAFT_DIR" --runtime --report "$REPORT/preflight.json"
    "$BINDCRAFT_PYTHON" /opt/poreva/tools/image_cpu_check.py "$REPORT"
    "$BINDCRAFT_PYTHON" -m pip check
    ;;
  validate-input)
    export CUDA_VISIBLE_DEVICES=""
    export JAX_PLATFORMS=cpu
    REPORT="${CPU_REPORT_DIR:-/tmp/poreva-input-check}"
    mkdir -p "$REPORT"
    "$BINDCRAFT_PYTHON" /opt/poreva/tools/preflight_bindcraft.py --settings /opt/poreva/configs/generation/TNFA_bindcraft_smoke.json --bindcraft "$BINDCRAFT_DIR" --runtime --report "$REPORT/preflight.json"
    ;;
  design)
    exec /bin/bash /opt/poreva/tools/run_bindcraft_smoke.sh
    ;;
  *) echo "Usage: entrypoint.sh [cpu-check|validate-input|design]" >&2; exit 2 ;;
esac
