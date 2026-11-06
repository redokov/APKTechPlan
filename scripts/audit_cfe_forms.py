"""Audit helper: summarize 1C MDClasses Ext/Form.xml files (elements, attrs, events)."""
import glob
import io
import sys
import xml.etree.ElementTree as ET

NS = {
    "md": "http://v8.1c.ru/8.3/MDClasses",
    "lf": "http://v8.1c.ru/8.2/managed-application/logform",
    "v8": "http://v8.1c.ru/8.1/data/core",
    "xr": "http://v8.1c.ru/8.3/xcf/readable",
}


def local(tag):
    return tag.split("}", 1)[-1]


def text(el, name):
    for c in el.iter():
        if local(c.tag) == name and (c.text or "").strip():
            return (c.text or "").strip()
    return ""


def summarize(path, out):
    tree = ET.parse(path)
    root = tree.getroot()

    def p(*a):
        out.write(" ".join(str(x) for x in a) + "\n")

    p("=========", path)

    # events: <Event name=..><Handler>..</Handler>
    for el in root.iter():
        if local(el.tag) == "Event":
            handler = text(el, "Handler")
            p("  EVENT", el.get("name"), "->", handler)

    # form attributes
    for el in root.iter():
        if local(el.tag) == "Attribute" and el.get("name"):
            ty = [text(c, "Type") for c in el.iter() if local(c.tag) == "Type"]
            ty = [t for t in ty if t]
            p("  FATTR", el.get("name"), "| type=", ty)

    # elements (ChildItems tree)
    def walk(node, depth):
        for c in node:
            t = local(c.tag)
            if t in ("ChildItems", "Attributes", "Events", "Commands", "Form"):
                walk(c, depth)
                continue
            if c.get("name"):
                ty = ""
                dp = ""
                cmd = ""
                for sub in c:
                    st = local(sub.tag)
                    if st == "Type" and (sub.text or "").strip():
                        ty = (sub.text or "").strip()
                    if st == "DataPath" and (sub.text or "").strip():
                        dp = (sub.text or "").strip()
                    if st == "CommandName" and (sub.text or "").strip():
                        cmd = (sub.text or "").strip()
                p("  " + "  " * min(depth, 6) + t, c.get("name"), "| type=", ty, "| path=", dp, "| cmd=", cmd)
            walk(c, depth + 1)

    for el in root.iter():
        if local(el.tag) == "ChildItems":
            walk(el, 1)

    # commands
    for el in root.iter():
        if local(el.tag) == "Command" and el.get("name"):
            p("  CMD", el.get("name"), "| action=", text(el, "Action"), "| handler=", text(el, "Handler"))


def main():
    out = io.open(sys.argv[1] if len(sys.argv) > 1 else "forms_audit.txt", "w", encoding="utf-8")
    for f in sorted(glob.glob("**/Ext/Form.xml", recursive=True)):
        summarize(f, out)
    out.close()


if __name__ == "__main__":
    main()
