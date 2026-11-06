import json, os, re
from pathlib import Path

BSL_DIR = 'src/cfe/ПланированиеТехникиАПК'
os.makedirs('tmp', exist_ok=True)

print('>>> Local pre-analysis...')
bsl_files = []
for root, _dirs, files in os.walk(BSL_DIR):
    for f in files:
        if f.endswith('.bsl') or f.endswith('.os'):
            bsl_files.append(os.path.join(root, f))

def size(p):
    try: return os.path.getsize(p)
    except Exception: return 0

mod_map = sorted(((os.path.relpath(f, BSL_DIR), size(f)) for f in bsl_files), key=lambda x: -x[1])
print(f'Found {len(bsl_files)} BSL/O.S. files. Top modules:')
for rel, sz in mod_map[:8]:
    print(f'  {sz:>7}  {rel}')

submods = sum(1 for _ in Path(BSL_DIR).rglob('*/Subsystems'))
commonmods = sum(1 for _ in Path(BSL_DIR).rglob('CommonModules/*'))
ext_names = set()
for f in bsl_files:
    m = re.search(r'CommonModules/([^/]+)/Ext/', f)
    if m: ext_names.add(m[1])
print(f'\nCommonModules: {commonmods}; extensions: {sorted(ext_names)}')
print(f'Subsystems dirs: {submods}')

json.dump({
    'bslCount': len(bsl_files),
    'topFiles': [[r, s] for r, s in mod_map],
    'extensions': sorted(ext_names),
    'submodules': submods,
}, open('tmp/preanalysis.json', 'w'), ensure_ascii=False, indent=2)
print('\nPre-analysis saved to tmp/preanalysis.json')
