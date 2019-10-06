import json
import xml.etree.ElementTree as ET


class Serializer:
    def serialize_json(self, toJsonObj):
        return json.dumps(toJsonObj)

    def deserialize_json(self, jsonContent):
        return json.loads(jsonContent)

    def serialize_xml(self):
        pass

    def deserialize_xml(self, content):
        return ET.fromstringlist(content)
