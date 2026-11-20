"""Style supported Mermaid sequence SVG exports. Python 3.9+, standard library."""
import argparse
import copy
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

SVG = "{http://www.w3.org/2000/svg}"
ET.register_namespace("", SVG[1:-1])
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def has(node, word):
    return word in node.get("class", "").split()


def paint(node, attribute, value):
    if not isinstance(value, str) or not re.fullmatch(r"#[a-fA-F0-9]{6}", value):
        raise ValueError("Use a six-digit hex color")
    node.set("style", node.get("style", "").rstrip("; ") + f";{attribute}:{value} !important;")


def inventory(root):
    actors, messages = {}, {}
    for n in root.iter(SVG+"rect"):
        if has(n,"actor") and n.get("name"):
            actors.setdefault(n.get("name"), []).append(n)
    for group in root.iter():
        pending = None
        for n in group:
            if has(n, "messageText"):
                if pending is not None:
                    raise ValueError("Multiple labels precede one arrow; unsupported renderer layout")
                pending = n
            elif has(n, "messageLine0") or has(n, "messageLine1"):
                if pending is None:
                    raise ValueError("Arrow lacks a sibling label; unsupported renderer layout")
                label = " ".join("".join(pending.itertext()).split())
                messages.setdefault(label, []).append((pending, n))
                pending = None
        if pending is not None:
            raise ValueError("Label lacks its arrow; unsupported renderer layout")
    if not actors and not messages:
        raise ValueError("No supported sequence elements")
    return actors, messages


def recolor(root, rules):
    actors, messages = inventory(root)
    allowed = {"actors", "messages"}
    if not isinstance(rules, dict) or not rules or set(rules)-allowed:
        raise ValueError("Expected actors and/or messages")
    ids = {n.get("id"):n for n in root.iter() if n.get("id")}
    defs = root.find(SVG+"defs")
    if defs is None:
        defs = ET.SubElement(root, SVG+"defs")
    selected = set()
    boxes = 0
    for name, color in rules.get("actors", {}).items():
        if name not in actors:
            raise ValueError(f"Unknown actor: {name}")
        for box in actors[name]:
            paint(box, "fill", color)
            boxes += 1
    for rule in rules.get("messages", []):
        matches = messages.get(rule["label"], [])
        position = rule.get("occurrence", 1 if len(matches)==1 else None)
        if type(position) is not int or not 1 <= position <= len(matches):
            raise ValueError(f"Unknown or ambiguous label: {rule['label']}")
        label, line = matches[position-1]
        if line in selected:
            raise ValueError("Conflicting rules for one message")
        selected.add(line)
        color = rule["color"]
        paint(label, "fill", color)
        paint(line, "stroke", color)
        for attr in ("marker-start", "marker-end"):
            marker = line.get(attr)
            if not marker or marker=="none":
                continue
            ref = re.fullmatch(r"url\(#([^)]+)\)", marker)
            if not ref or ref[1] not in ids:
                raise ValueError("Unsupported marker reference")
            original = ids[ref[1]]
            if original.tag != SVG+"marker":
                raise ValueError("Reference is not a marker")
            clone = copy.deepcopy(original)
            new_id = f"palette-{len(ids)}"
            while new_id in ids:
                new_id += "x"
            clone.set("id",new_id)
            for shape in clone.iter():
                if shape is clone:
                    continue
                if shape.get("id"):
                    raise ValueError("Nested marker IDs require manual review")
                if shape.tag in {SVG+t for t in ("path","polygon","polyline","line","circle")}:
                    if shape.get("fill") != "none" and not re.search(r"fill\s*:\s*none",shape.get("style","")):
                        paint(shape,"fill",color)
                    paint(shape,"stroke",color)
            defs.append(clone)
            ids[new_id]=clone
            line.set(attr,f"url(#{new_id})")
    if not boxes and not selected:
        raise ValueError("Empty selection")
    return {"boxes":boxes,"messages":len(selected)}


if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("svg",type=Path)
    ap.add_argument("rules",nargs="?",type=Path)
    ap.add_argument("output",nargs="?",type=Path)
    args=ap.parse_args()
    try:
        tree=ET.parse(args.svg)
        if args.rules is None and args.output is None:
            actors,messages=inventory(tree.getroot())
            print(json.dumps({"actors":list(actors),"messages":{k:len(v) for k,v in messages.items()}},ensure_ascii=True))
        elif args.rules and args.output:
            report=recolor(tree.getroot(),json.loads(args.rules.read_text(encoding="utf-8-sig")))
            with args.output.open("xb") as out:
                tree.write(out,encoding="utf-8",xml_declaration=True)
            print(json.dumps(report))
        else:
            ap.error("Supply both rules and output")
    except (OSError, ValueError, TypeError, KeyError, ET.ParseError) as exc:
        ap.exit(2,f"{exc}\n")
