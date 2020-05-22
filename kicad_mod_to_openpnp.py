import argparse
import os
import re
import xml.etree.ElementTree as ET

from pathlib import Path
from xml.dom import minidom


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', type=str, required=True,
        help="Input file or directory with files in .kicad_mod format")
    parser.add_argument('--output', '-o', type=str, required=True,
        help="Output file in OpenPnP XML format")
    args = parser.parse_args()
    
    if os.path.isdir(args.input):
        inputs = [f for f in os.listdir(args.input) if os.path.splitext(f)[1].lower() == ".kicad_mod"]
        inputs = [os.path.join(args.input, f) for f in inputs]
        inputs = [f for f in inputs if not os.path.isdir(f)]
    else:
        inputs = [args.input]
    
    packages = ET.Element("openpnp-packages")
    
    for input_filename in inputs:
        name = Path(input_filename).stem
        
        with open(input_filename, 'r') as in_file:
            in_data = in_file.read()
        
        pads = []
        pad_def = re.compile(r"\(pad (?P<name>.+) smd (?P<type>.+) \(at (?P<x>[-\d.]+) (?P<y>[-\d.]+)(?: (?P<rotation>[-\d.]+))*\) \(size (?P<width>[-\d.]+) (?P<height>[-\d.]+)\) \(layers .+?\)(?: \(roundrect_rratio (?P<roundness>[-\d.]+)\))*\)")
        for line in in_data.splitlines():
            match = pad_def.search(line)
            if match:
                pads.append(match.groupdict())
        
        if not pads:
            print("No pads found! Skipping.")
            continue
        
        package = ET.SubElement(packages, "package", version="1.1", id=name)
        footprint = ET.SubElement(package, "footprint", units="Millimeters")
        for pad in pads:
            if pad['type'] == 'rect':
                ET.SubElement(footprint, "pad",
                    name=pad['name'],
                    x=pad['x'],
                    y=str(float(pad['y'])*-1),
                    width=pad['width'],
                    height=pad['height'],
                    rotation=pad['rotation'] or "0.0",
                    roundness="0.0"
                )
            elif pad['type'] == 'roundrect':
                ET.SubElement(footprint, "pad",
                    name=pad['name'],
                    x=pad['x'],
                    y=str(float(pad['y'])*-1),
                    width=pad['width'],
                    height=pad['height'],
                    rotation=pad['rotation'] or "0.0",
                    roundness=str(float(pad['roundness'])*200)
                )
            elif pad['type'] == 'circle':
                ET.SubElement(footprint, "pad",
                    name=pad['name'],
                    x=pad['x'],
                    y=str(float(pad['y'])*-1),
                    width=pad['width'],
                    height=pad['width'],
                    rotation="0.0",
                    roundness="100.0"
                )
            elif pad['type'] == 'oval':
                ET.SubElement(footprint, "pad",
                    name=pad['name'],
                    x=pad['x'],
                    y=str(float(pad['y'])*-1),
                    width=pad['width'],
                    height=pad['height'],
                    rotation=pad['rotation'] or "0.0",
                    roundness="100.0"
                )
    
    xml_str = minidom.parseString(ET.tostring(packages)).toprettyxml(indent="   ")
    xml_lines = xml_str.splitlines()
    xml_str = "\n".join(xml_lines[1:]) # Remove XML declaration
    with open(args.output, 'w') as out_file:
        out_file.write(xml_str)


if __name__ == "__main__":
    main()
