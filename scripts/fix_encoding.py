import sys
p = sys.argv[1]
data = open(p, "rb").read()
out = bytearray()
for b in data:
    if 0x80 <= b <= 0x9F:
        out.append(b + 0x40)
    elif 0xE0 <= b <= 0xFF:
        out.append(b + 0x20)
    else:
        out.append(b)
text = out.decode("cp1251")
open(p, "w", encoding="cp1251").write(text)
print("fixed", p, len(out))
