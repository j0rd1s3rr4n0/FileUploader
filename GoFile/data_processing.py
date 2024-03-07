import json
import xml.etree.ElementTree as ET

class DataProcessor:
    @staticmethod
    def process_data(uploadedFile, format="json", verbose=False):
        def recursive_conversion(value):
            if isinstance(value, dict):
                return {key: recursive_conversion(val) for key, val in value.items()}
            return value

        processed_data = recursive_conversion(uploadedFile)

        if format == "json":
            return json.dumps(processed_data, indent=4)
        elif format == "xml":
            def dict_to_xml(dictionary, root):
                for key, value in dictionary.items():
                    if isinstance(value, dict):
                        elem = ET.Element(key)
                        dict_to_xml(value, elem)
                    else:
                        elem = ET.Element(key)
                        elem.text = str(value)
                    root.append(elem)
                return root

            root = ET.Element("uploadedFile")
            dict_to_xml(processed_data, root)
            xml_data = ET.tostring(root, encoding="unicode")
            xml_data = '<?xml version="1.0" encoding="UTF-8" ?>'+xml_data
            return xml_data
        elif format == "plaintext":
            def dict_to_plaintext(dictionary, indent=0):
                result = ""
                for key, value in dictionary.items():
                    if isinstance(value, dict):
                        result += " " * indent + f"{key} :\n{dict_to_plaintext(value, indent + 4)}"
                    else:
                        result += " " * indent + f"{key.ljust(15)} : {value}\n"
                return result

            return dict_to_plaintext(processed_data)
