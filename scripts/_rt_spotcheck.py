import io, sys, os, difflib
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\MyProjects\APKTechPlan\src\cfe\ПланированиеТехникиАПК'
DST = r'C:\Users\r.edokov\AppData\Local\Temp\rt_dump_apktechplan'

def canon(path):
    tree = ET.parse(path)
    def strip(e):
        for at in list(e.attrib):
            pass
        return e
    # canonical: tags + text, ignoring attrib order; keep attribs sorted
    out = []
    def walk(e, d=0):
        tag = e.tag.split('}')[-1]
        at = dict(sorted(e.attrib.items()))
        txt = (e.text or '').strip()
        out.append('%s%s %s %s' % ('  ' * d, tag, at, txt))
        for c in e:
            walk(c, d + 1)
    walk(tree.getroot())
    return out

pairs = [
    ('InformationRegisters/Тх_КоэффициентыПересчетаРабот.xml', 20),
    ('InformationRegisters/Тх_ДефицитТехники.xml', 15),
    ('Enums/Тх_ВидыТехники.xml', 30),
    ('Roles/Тх_Чтение/Ext/Rights.xml', 30),
    ('Reports/Тх_ДефицитТехники/Templates/ОсновнаяСхемаКомпоновкиДанных/Ext/Template.xml', 12),
    ('Subsystems/Тх_ПланированиеТехники/Ext/CommandInterface.xml', 40),
]
for rel, maxlines in pairs:
    a = canon(os.path.join(SRC, rel))
    b = canon(os.path.join(DST, rel))
    diff = [l for l in difflib.unified_diff(a, b, lineterm='', n=0)]
    real = [l for l in diff if l.startswith(('+', '-'))]
    print('=== %s: %d diff lines' % (rel, len(real)))
    for l in real[:maxlines]:
        print('  ', l[:150])
