import json
from os import path

from google.protobuf.json_format import MessageToJson

import tachiyomi_pb2

ScriptDir = path.dirname(__file__)
output_fileName = 'data.json'
backup_path = input("Write the path to your .proto backup file\n>")

with open(backup_path, 'rb') as f:
    read_metric = tachiyomi_pb2.Backup()
    read_metric.ParseFromString(f.read())

json_str = MessageToJson(read_metric)
json_obj = json.loads(json_str)

with open(output_fileName, 'w', encoding='utf-8') as f:
    json.dump(json_obj, f, ensure_ascii=False, indent=4)

print(f"Saved to {ScriptDir}/{output_fileName}")
