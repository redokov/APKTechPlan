import os, shutil, io, uuid, sys
sys.stdout.reconfigure(encoding='utf-8')

base = os.path.join('src', 'cfe', 'ПланированиеТехникиАПК',
                    'Reports', 'Тх_ДефицитТехники', 'Templates')
tpl_dir = os.path.join(base, 'ОсновнаяСхемаКомпоновкиДанных')

# 1. move Template.xml -> Ext/Template.xml
old = os.path.join(tpl_dir, 'Template.xml')
new_dir = os.path.join(tpl_dir, 'Ext')
os.makedirs(new_dir, exist_ok=True)
assert os.path.isfile(old), 'Template.xml not found at old location'
shutil.move(old, os.path.join(new_dir, 'Template.xml'))
print('moved Template.xml -> Ext/Template.xml')

# 2. create template metadata XML beside the dir
new_uuid = str(uuid.uuid4())
meta = (
 '<?xml version="1.0" encoding="UTF-8"?>\n'
 '<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses"'
 ' xmlns:app="http://v8.1c.ru/8.2/managed-application/core"'
 ' xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config"'
 ' xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi"'
 ' xmlns:ent="http://v8.1c.ru/8.1/data/enterprise"'
 ' xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform"'
 ' xmlns:style="http://v8.1c.ru/8.1/data/ui/style"'
 ' xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system"'
 ' xmlns:v8="http://v8.1c.ru/8.1/data/core"'
 ' xmlns:v8ui="http://v8.1c.ru/8.1/data/ui"'
 ' xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web"'
 ' xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows"'
 ' xmlns:xen="http://v8.1c.ru/8.3/xcf/enums"'
 ' xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef"'
 ' xmlns:xr="http://v8.1c.ru/8.3/xcf/readable"'
 ' xmlns:xs="http://www.w3.org/2001/XMLSchema"'
 ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">\n'
 '\t<Template uuid="' + new_uuid + '">\n'
 '\t\t<Properties>\n'
 '\t\t\t<Name>ОсновнаяСхемаКомпоновкиДанных</Name>\n'
 '\t\t\t<Synonym>\n'
 '\t\t\t\t<v8:item>\n'
 '\t\t\t\t\t<v8:lang>ru</v8:lang>\n'
 '\t\t\t\t\t<v8:content>Основная схема компоновки данных</v8:content>\n'
 '\t\t\t\t</v8:item>\n'
 '\t\t\t</Synonym>\n'
 '\t\t\t<Comment/>\n'
 '\t\t\t<TemplateType>DataCompositionSchema</TemplateType>\n'
 '\t\t</Properties>\n'
 '\t</Template>\n'
 '</MetaDataObject>\n'
)
meta_path = os.path.join(base, 'ОсновнаяСхемаКомпоновкиДанных.xml')
with io.open(meta_path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
    f.write(meta)
print('created', meta_path, 'uuid=' + new_uuid)
