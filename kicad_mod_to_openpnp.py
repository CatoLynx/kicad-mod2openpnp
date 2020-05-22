import argparse
import os
import xml.etree.ElementTree as ET

from pathlib import Path
from pykicad.module import Module
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
        mod = Module.from_file(input_filename)
        
        if not mod.pads:
            print("No pads found! Skipping.")
            continue
        
        package = ET.SubElement(packages, "package", version="1.1", id=name)
        footprint = ET.SubElement(package, "footprint", units="Millimeters")
        for pad in mod.pads:
            if pad.shape == 'rect':
                ET.SubElement(footprint, "pad",
                    name=pad.name,
                    x=str(pad.at[0]),
                    y=str(pad.at[1] * -1),
                    width=str(pad.size[0]),
                    height=str(pad.size[1]),
                    rotation=str(pad.at[2] if len(pad.at) > 2 else 0.0),
                    roundness="0.0"
                )
            elif pad.shape == 'roundrect':
                ET.SubElement(footprint, "pad",
                    name=pad.name,
                    x=str(pad.at[0]),
                    y=str(pad.at[1] * -1),
                    width=str(pad.size[0]),
                    height=str(pad.size[1]),
                    rotation=str(pad.at[2] if len(pad.at) > 2 else 0.0),
                    roundness=str(pad.roundrect_rratio * 200)
                )
            elif pad.shape == 'circle':
                ET.SubElement(footprint, "pad",
                    name=pad.name,
                    x=str(pad.at[0]),
                    y=str(pad.at[1] * -1),
                    width=str(pad.size[0]),
                    height=str(pad.size[0]),
                    rotation="0.0",
                    roundness="100.0"
                )
            elif pad.shape == 'oval':
                ET.SubElement(footprint, "pad",
                    name=pad.name,
                    x=str(pad.at[0]),
                    y=str(pad.at[1] * -1),
                    width=str(pad.size[0]),
                    height=str(pad.size[1]),
                    rotation=str(pad.at[2] if len(pad.at) > 2 else 0.0),
                    roundness="100.0"
                )
    
    xml_str = minidom.parseString(ET.tostring(packages)).toprettyxml(indent="   ")
    xml_lines = xml_str.splitlines()
    xml_str = "\n".join(xml_lines[1:]) # Remove XML declaration
    with open(args.output, 'w') as out_file:
        out_file.write(xml_str)


if __name__ == "__main__":
    main()
