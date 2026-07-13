import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
import json

class DataExporter(ABC):
    @abstractmethod
    def export(self, data: list, output_path: str) -> None:
        pass

class XMLExporter(DataExporter):
    #writing data into XML format
    def export(self, data: list, output_path: str) -> None:

        root = ET.Element("results")
        for row in data:
            room_element = ET.SubElement(root, "room")
            
            id_element = ET.SubElement(room_element, "id")
            id_element.text = str(row["id"])
            
            name_element = ET.SubElement(room_element, "name")
            name_element.text = str(row["name"])
        
        tree = ET.ElementTree(root)        
        ET.indent(tree, space="    ")         
        tree.write(output_path, encoding='utf-8', xml_declaration=True)

class JSONExporter(DataExporter):
    #writing data into JSON format
    def export(self, data: list, output_path: str) -> None:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)