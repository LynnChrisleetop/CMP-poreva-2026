#!/usr/bin/env python3
"""CPU-only input/runtime checks. Never launches BindCraft or requests a GPU."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--settings', required=True)
    p.add_argument('--pdb', help='Local override of container PDB path')
    p.add_argument('--bindcraft', required=True)
    p.add_argument('--runtime', action='store_true', help='Also verify imports, weights and native libraries')
    p.add_argument('--report', required=True)
    args = p.parse_args()
    checks = []
    def check(name, ok, detail):
        checks.append(dict(name=name, ok=bool(ok), detail=detail))
    bc = Path(args.bindcraft).resolve()
    try:
        settings = json.loads(Path(args.settings).read_text())
        required = {'design_path','binder_name','starting_pdb','chains','target_hotspot_residues','lengths','number_of_final_designs'}
        check('settings_keys', required <= settings.keys(), sorted(required - settings.keys()))
        lengths = settings.get('lengths', [])
        check('lengths', len(lengths)==2 and all(type(x) is int for x in lengths) and 0 < lengths[0] <= lengths[1] <= 300, lengths)
        check('design_count', type(settings.get('number_of_final_designs')) is int and settings['number_of_final_designs'] > 0, settings.get('number_of_final_designs'))
        path = Path(args.pdb or settings['starting_pdb'])
        residues = {}; duplicates = []; nonfinite = []
        models = 0
        for line in path.read_text().splitlines():
            if line.startswith('MODEL '): models += 1
            if not line.startswith('ATOM  '): continue
            key = (line[21], line[22:26].strip(), line[26])
            atom = line[12:16].strip()
            entry = residues.setdefault(key, {'name':line[17:20].strip(),'atoms':set()})
            if atom in entry['atoms']: duplicates.append([*key,atom])
            entry['atoms'].add(atom)
            if not all(math.isfinite(float(line[a:b])) for a,b in [(30,38),(38,46),(46,54)]): nonfinite.append(key)
        selected = settings['chains'].split(',')
        counts = {c:sum(k[0]==c for k in residues) for c in selected}
        check('single_model', models <= 1, models)
        check('selected_chains', all(counts.values()), counts)
        check('unique_atoms', not duplicates, duplicates[:10])
        check('finite_coordinates', not nonfinite, nonfinite[:10])
        missing = [list(k) for k,v in residues.items() if k[0] in selected and not {'N','CA','C','O'} <= v['atoms']]
        check('backbone_complete_observed_residues', not missing, missing[:20])
        standard = set('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split())
        bad = [list(k) for k,v in residues.items() if v['name'] not in standard]
        check('standard_residue_names', not bad, bad[:10])
        check('pdb_sha256', True, hashlib.sha256(path.read_bytes()).hexdigest())
        if len(lengths)==2: check('complex_residue_range', True, [sum(counts.values())+v for v in lengths])
    except Exception as e:
        check('input_parse', False, str(e))
    check('bindcraft_entrypoint', (bc/'bindcraft.py').is_file(), str(bc/'bindcraft.py'))
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='', JAX_PLATFORMS='cpu', MPLBACKEND='Agg')
    env['LD_LIBRARY_PATH'] = str(Path(sys.prefix)/'lib') + (':' + env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
    if args.runtime:
        for module in ['numpy','pandas','scipy','matplotlib','Bio','jax','jaxlib','haiku','flax','optax','chex','pdbfixer','pyrosetta','colabdesign']:
            try:
                r = subprocess.run([sys.executable,'-c',f'import {module}; print(getattr({module}, "__version__", "import OK"))'],env=env,capture_output=True,text=True,timeout=90)
                check('import:'+module, r.returncode==0, (r.stdout+r.stderr)[-1500:])
            except subprocess.TimeoutExpired:
                check('import:'+module, False, '90 second timeout')
        if all(c['ok'] for c in checks if c['name'].startswith('import:')):
            r = subprocess.run([sys.executable,'-c','import functions; print("BINDCRAFT_FUNCTIONS_IMPORT_OK")'],cwd=bc,env=env,capture_output=True,text=True,timeout=120)
            check('bindcraft_functions_import', r.returncode==0, (r.stdout+r.stderr)[-2000:])
        for family in ['ptm','multimer_v3']:
            for i in range(1,6):
                f = bc/'params'/f'params_model_{i}_{family}.npz'
                check('weight:'+f.name, f.is_file() and f.stat().st_size > 0, str(f))
        for name in ['dssp','DAlphaBall.gcc']:
            f = bc/'functions'/name
            check('executable:'+name, os.access(f,os.X_OK), str(f))
            if f.is_file():
                try:
                    r = subprocess.run(['ldd',str(f)],env=env,capture_output=True,text=True,timeout=15)
                    msg=r.stdout+r.stderr
                    check('shared_libraries:'+name, 'not found' not in msg and (r.returncode==0 or 'not a dynamic executable' in msg or 'statically linked' in msg), msg)
                except (OSError, subprocess.TimeoutExpired) as e: check('shared_libraries:'+name,False,str(e))
    result = {'mode':'cpu_runtime' if args.runtime else 'input_only','python':sys.executable,'gpu_tested':False,'design_run':False,'passed':all(c['ok'] for c in checks),'checks':checks}
    out=Path(args.report); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'mode':result['mode'],'failed_checks':[c['name'] for c in checks if not c['ok']],'report':str(out)}))
    return 0 if result['passed'] else 2

if __name__ == '__main__':
    raise SystemExit(main())
