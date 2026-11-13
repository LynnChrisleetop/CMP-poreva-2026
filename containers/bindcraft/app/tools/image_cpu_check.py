import json,sys,importlib.metadata as metadata,hashlib,subprocess
from packaging.requirements import Requirement
from pathlib import Path
import jax,jax.numpy as jnp,pyrosetta
assert all(x.platform=='cpu' for x in jax.devices()),jax.devices()
x=jnp.ones((16,16)); assert float((x@x).block_until_ready()[0,0])==16
pyrosetta.init('-mute all -ignore_unrecognized_res')
p=pyrosetta.pose_from_pdb('/opt/poreva/tests/tnfa.pdb')
assert p.total_residue()==456 and p.num_chains()==3
sys.path.insert(0,'/opt/BindCraft')
import functions
versions={name:metadata.version(name) for name in ['jax','jaxlib','jax-cuda12-plugin','jax-cuda12-pjrt','dm-haiku','pyrosetta','colabdesign']}
assert versions['jax']=='0.4.35' and versions['jaxlib']=='0.4.34'
assert versions['jax-cuda12-plugin']==versions['jax-cuda12-pjrt']=='0.4.35'
for spec in metadata.requires('jax-cuda12-plugin'):
 req=Requirement(spec)
 if req.marker is None or req.marker.evaluate({'extra':'with-cuda'}):
  assert metadata.version(req.name) in req.specifier,(req.name,metadata.version(req.name),str(req.specifier))
manifest=json.loads(Path('/opt/poreva/provenance/weights_manifest.json').read_text())['weights']
for name,expected in manifest.items():
 h=hashlib.sha256()
 with Path('/opt/BindCraft/params',name).open('rb') as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
 assert h.hexdigest()==expected['sha256'],name
ptxas='/opt/bindcraft-env/lib/python3.10/site-packages/nvidia/cuda_nvcc/bin/ptxas'
r=subprocess.run([ptxas,'--version'],capture_output=True,text=True,check=True)
print('PTXAS_CPU_EXECUTABLE_OK',r.stdout.strip())
report={'passed':True,'gpu_used':False,'gpu_runtime_verified':False,'design_run':False,'residues':p.total_residue(),'chains':p.num_chains(),'versions':versions}
Path(sys.argv[1],'cpu_smoke.json').write_text(json.dumps(report,indent=2)+'\n')
print('IMAGE_CPU_CHECK_OK',json.dumps(report),flush=True)
