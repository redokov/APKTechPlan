#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate test extension object: info register with dimension typed to
CatalogRef.АпкМоделиСХТехники (object owned by ANOTHER extension) + register
it in the extension Configuration.xml ChildObjects."""
import os, re, uuid as uuidlib

NS = ('xmlns="http://v8.1c.ru/8.3/MDClasses" '
      'xmlns:app="http://v8.1c.ru/8.2/managed-application/core" '
      'xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" '
      'xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" '
      'xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" '
      'xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" '
      'xmlns:pal="http://v8.1c.ru/8.1/data/ui/colors/palette" '
      'xmlns:style="http://v8.1c.ru/8.1/data/ui/style" '
      'xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" '
      'xmlns:v8="http://v8.1c.ru/8.1/data/core" '
      'xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
      'xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" '
      'xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" '
      'xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" '
      'xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" '
      'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" '
      'xmlns:xs="http://www.w3.org/2001/XMLSchema" '
      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.22"')

EXT_DIR = os.path.join('src', 'cfe', 'ТестКроссСсылок')
NAME = 'ТестКроссСсылок_Регистр'
DIM_NAME = 'МодельТехники'
DIM_TYPE = 'CatalogRef.АпкМоделиСХТехники'   # owned by other extension!

def u():
    return str(uuidlib.uuid4())

REG_UUID = '11111111-2222-3333-4444-555555555555'  # fixed, reused in both files

cats = ['Record', 'Manager', 'Selection', 'List', 'RecordSet', 'RecordKey', 'RecordManager']
gen_types = []
for c in cats:
    gen_types.append(
        f'\t\t\t<xr:GeneratedType name="InformationRegister{c}.{NAME}" category="{c}">\r\n'
        f'\t\t\t\t<xr:TypeId>{u()}</xr:TypeId>\r\n'
        f'\t\t\t\t<xr:ValueId>{u()}</xr:ValueId>\r\n'
        f'\t\t\t</xr:GeneratedType>')
gi = '\r\n'.join(gen_types)

xml = ('\ufeff<?xml version="1.0" encoding="UTF-8"?>\r\n'
       f'<MetaDataObject {NS}>\r\n'
       f'\t<InformationRegister uuid="{REG_UUID}">\r\n'
       f'\t\t<InternalInfo>\r\n{gi}\r\n\t\t</InternalInfo>\r\n'
       '\t\t<Properties>\r\n'
       f'\t\t\t<Name>{NAME}</Name>\r\n'
       '\t\t\t<Synonym>\r\n\t\t\t\t<v8:item>\r\n\t\t\t\t\t<v8:lang>ru</v8:lang>\r\n'
       '\t\t\t\t\t<v8:content>Тест кросс-ссылок (регистр)</v8:content>\r\n'
       '\t\t\t\t</v8:item>\r\n\t\t\t</Synonym>\r\n'
       '\t\t\t<Comment/>\r\n'
       '\t\t\t<UseStandardCommands>true</UseStandardCommands>\r\n'
       '\t\t\t<EditType>InDialog</EditType>\r\n'
       '\t\t\t<DefaultRecordForm/>\r\n'
       '\t\t\t<DefaultListForm/>\r\n'
       '\t\t\t<RecordSetScript/>\r\n'
       '\t\t\t<RunFilling>false</RunFilling>\r\n'
       '\t\t\t<DataLockControlMode>Managed</DataLockControlMode>\r\n'
       '\t\t\t<InformationRegisterPeriodicity>Nonperiodic</InformationRegisterPeriodicity>\r\n'
       '\t\t\t<WriteOnPost>Write</WriteOnPost>\r\n'
       '\t\t\t<DataHistory>false</DataHistory>\r\n'
       '\t\t\t<InformationRegisterWriteMode>Independent</InformationRegisterWriteMode>\r\n'
       '\t\t\t<InformationRegisterMainFilterOnDimension/>\r\n'
       '\t\t</Properties>\r\n'
       '\t\t<ChildObjects>\r\n'
       f'\t\t\t<Dimension uuid="{u()}">\r\n'
       '\t\t\t\t<Properties>\r\n'
       f'\t\t\t\t\t<Name>{DIM_NAME}</Name>\r\n'
       '\t\t\t\t\t<Synonym>\r\n\t\t\t\t\t\t<v8:item>\r\n\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>\r\n'
       '\t\t\t\t\t\t\t<v8:content>Модель техники</v8:content>\r\n'
       '\t\t\t\t\t\t</v8:item>\r\n\t\t\t\t\t</Synonym>\r\n'
       '\t\t\t\t\t<Comment/>\r\n'
       '\t\t\t\t\t<Type>\r\n'
       f'\t\t\t\t\t\t<v8:Type>{DIM_TYPE}</v8:Type>\r\n'
       '\t\t\t\t\t</Type>\r\n'
       '\t\t\t\t\t<PasswordMode>false</PasswordMode>\r\n'
       '\t\t\t\t\t<Format/>\r\n\t\t\t\t\t<EditFormat/>\r\n'
       '\t\t\t\t\t<ToolTip/>\r\n'
       '\t\t\t\t\t<MarkNegatives>false</MarkNegatives>\r\n'
       '\t\t\t\t\t<Mask/>\r\n'
       '\t\t\t\t\t<MultiLine>false</MultiLine>\r\n'
       '\t\t\t\t\t<ExtendedEdit>false</ExtendedEdit>\r\n'
       '\t\t\t\t\t<MinValue xsi:type="xs:dateTime"/>\r\n'
       '\t\t\t\t\t<MaxValue xsi:type="xs:dateTime"/>\r\n'
       '\t\t\t\t\t<FillFromFillingValue>false</FillFromFillingValue>\r\n'
       '\t\t\t\t\t<FillChecking>DontCheck</FillChecking>\r\n'
       '\t\t\t\t\t<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>\r\n'
       '\t\t\t\t\t<ChoiceParameterLinks/>\r\n\t\t\t\t\t<ChoiceParameters/>\r\n'
       '\t\t\t\t\t<QuickChoice>false</QuickChoice>\r\n'
       '\t\t\t\t\t<CreateOnInput>Use</CreateOnInput>\r\n'
       '\t\t\t\t\t<ChoiceHistoryMode>Auto</ChoiceHistoryMode>\r\n'
       '\t\t\t\t\t<DataHistory>Write</DataHistory>\r\n'
       '\t\t\t\t\t<Indexing>DontIndex</Indexing>\r\n'
       '\t\t\t\t</Properties>\r\n'
       '\t\t\t</Dimension>\r\n'
       '\t\t</ChildObjects>\r\n'
       '\t</InformationRegister>\r\n'
       '</MetaDataObject>')

out_dir = os.path.join(EXT_DIR, 'InformationRegisters')
os.makedirs(out_dir, exist_ok=True)
open(os.path.join(out_dir, NAME + '.xml'), 'w', encoding='utf-8', newline='').write(xml)
print('register xml written, bytes:', len(xml.encode('utf-8')))

# patch Configuration.xml: add to ChildObjects (create section if missing)
cfg_path = os.path.join(EXT_DIR, 'Configuration.xml')
cfg = open(cfg_path, encoding='utf-8').read()
entry = f'\t\t<InformationRegister uuid="{REG_UUID}">\r\n\t\t\t<Properties>\r\n\t\t\t\t<Name>{NAME}</Name>\r\n\t\t\t\t<Synonym/>\r\n\t\t\t</Properties>\r\n\t\t</InformationRegister>\r\n'
if '<ChildObjects>' in cfg:
    cfg = cfg.replace('<ChildObjects>', '<ChildObjects>\r\n' + entry, 1)
else:
    # insert before </Configuration>
    cfg = cfg.replace('\t</Configuration>', '\t\t<ChildObjects>\r\n' + entry + '\t\t</ChildObjects>\r\n\t</Configuration>', 1)
open(cfg_path, 'w', encoding='utf-8', newline='').write(cfg)
print('Configuration.xml patched, has ChildObjects:', '<ChildObjects>' in cfg)
