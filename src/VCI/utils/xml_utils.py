from xml.etree import ElementTree
from xml.dom import minidom
from lxml import etree as ET

def get_dom_tree(tree: ElementTree.ElementTree) -> minidom.Document:
    '''Returns a pretty printed string of the xml tree'''
    rough_string = ElementTree.tostring(tree.getroot())
    reparsed = minidom.parseString(rough_string)
    return reparsed

def write_root(root: ET.Element, output: str, *args, **kargs) -> None:
    '''Writes the root to a file'''
    tree = root.getroottree()
    tree.write(output, pretty_print=True, xml_declaration=True, encoding="utf-8")