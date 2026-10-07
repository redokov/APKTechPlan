import os, sys, glob
sys.stdout.reconfigure(encoding='utf-8')

OURS = 'src/cfe/ПланированиеТехникиАПК'
REF = ['C:/MyProjects/APKModSrc', 'C:/MyProjects/ERPsrc']

# collect per-kind layout signature from reference dumps:
# for each object: which xml files sit BESIDE the object dir, which INSIDE.
def signature(base, kind, obj):
    d = os.path.join(base, kind, obj)
    if not os.path.isdir(d):
        return None
    sig = {}
    beside = os.path.join(base, kind, obj + '.xml')
    sig['beside_xml'] = os.path.isfile(beside)
    for root, dirs, files in os.walk(d):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), d)
            sig.setdefault('inner', []).append(rel)
    return sig

def ref_patterns(kind, limit=3):
    out = {}
    for base in REF:
        kd = os.path.join(base, kind)
        if not os.path.isdir(kd):
            continue
        for obj in sorted(os.listdir(kd)):
            s = signature(base, kind, obj)
            if s:
                # normalize: keep relative shape (dirs vs file names)
                inner = sorted(tuple(os.path.normpath(r).split(os.sep)) for r in s['inner'])
                key = (s['beside_xml'], tuple(inner))
                out.setdefault(key, []).append(obj)
    return out

for kind in ['CommonModules', 'DataProcessors', 'Documents', 'Enums',
             'InformationRegisters', 'Reports', 'Roles', 'Subsystems', 'Languages']:
    pats = ref_patterns(kind)
    print('===', kind, '(%d pattern(s))' % len(pats))
    for key, objs in sorted(pats.items(), key=lambda kv: -len(kv[1])):
        print('  beside=%s n=%d e.g. %s' % (key[0], len(objs), objs[0]))
        for item in key[1][:8]:
            print('     ', '/'.join(item))
    # ours
    kd = os.path.join(OURS, kind)
    if not os.path.isdir(kd):
        continue
    for obj in sorted(os.listdir(kd)):
        s = signature(OURS, kind, obj)
        if s:
            inner = sorted(tuple(os.path.normpath(r).split(os.sep)) for r in s['inner'])
            ours_key = (s['beside_xml'], tuple(inner))
            status = 'OK (known pattern)' if ours_key in pats else '<<< UNKNOWN PATTERN'
            print('  OURS %s beside=%s %s' % (obj, s['beside_xml'], status))
            for item in inner[:8]:
                print('     ', '/'.join(item))
