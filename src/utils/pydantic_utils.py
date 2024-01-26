import json

from pydantic import BaseModel


def pretty_print_pydantic(obj: BaseModel):
    # Convert the Pydantic model to a dictionary
    obj_dict = obj.model_dump()
    # Pretty print the dictionary as a JSON string
    pretty_json = json.dumps(obj_dict, indent=4, sort_keys=True)
    print(pretty_json)
