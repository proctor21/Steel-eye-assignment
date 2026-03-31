import xml.etree.ElementTree as ET

tree = ET.parse("data/DLTINS_20210119_01of02.xml")
root = tree.getroot()

AUTH_NS = "urn:iso:std:iso:20022:tech:xsd:auth.036.001.02"

# Test 1: how many FinInstrm elements exist?
found = list(root.iter(f"{{{AUTH_NS}}}FinInstrm"))
print(f"FinInstrm count: {len(found)}")

# Test 2: print raw XML of the first one
if found:
    print("\nFirst FinInstrm raw XML:")
    print(ET.tostring(found[0], encoding="unicode")[:2000])
else:
    print("\nNot found via iter — trying full tree walk...")
    for elem in root.iter():
        if "FinInstrm" in elem.tag:
            print(f"  Partial match: {elem.tag!r}")
            print(ET.tostring(elem, encoding="unicode")[:500])
            print()
            break