import json
from pathlib import Path

DATA_DIR=Path(__file__).resolve().parent.parent/"data"

def read_json(file_name):
    path=DATA_DIR/file_name
    if not path.exists():
        return []
    with open(path,"r",encoding="utf-8") as file:
        return json.load(file)

def write_json(file_name,rows):
    path=DATA_DIR/file_name
    path.parent.mkdir(parents=True,exist_ok=True)
    with open(path,"w",encoding="utf-8") as file:
        json.dump(rows,file,indent=2)

def next_id(items):
    if not items:
        return 1
    biggest_id=max(item.id for item in items)
    return biggest_id+1