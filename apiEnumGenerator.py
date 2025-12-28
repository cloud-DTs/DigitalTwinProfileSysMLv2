import json

def generate_sysml_files(schema_path):
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    schemas = schema.get('components', {}).get('schemas', {})
    

    unique_owners = sorted([name for name in schemas.keys() if "Request" not in name])

    with open("src/api/ApiModels/ApiTypes.py", "w") as f:
        f.write("from enum import Enum\n\nclass ApiTypes(Enum):\n")
        f.write("    ALL = 'ALL'\n")
        for owner in unique_owners:
            key = owner.upper().replace("-", "_").replace(".", "_")
            if key[0].isdigit(): key = "T_" + key
            f.write(f"    {key} = '{owner}'\n")

    field_map = {}
    for owner_name, content in schemas.items():
        if "Request" in owner_name: continue
        
        props = {}
        if 'properties' in content: props.update(content['properties'])
        for group in ['allOf', 'anyOf']:
            if group in content:
                for sub in content[group]:
                    if 'properties' in sub: props.update(sub['properties'])

        for p_name, p_info in props.items():
            json_type = p_info.get('type')
            if json_type == "array": py_type = "list"
            elif json_type == "object" or "$ref" in p_info: py_type = "dict"
            elif json_type == "boolean": py_type = "bool"
            elif json_type in ["number", "integer"]: py_type = "float"
            else: py_type = "str"
                
            if p_name not in field_map:
                field_map[p_name] = {"type": py_type, "owners": set()}
            field_map[p_name]["owners"].add(owner_name)

    with open("src/api/ApiModels/Fields.py", "w") as f:
        f.write("from enum import Enum\nfrom .ApiTypes import ApiTypes\n\nclass Fields(Enum):\n")
        for f_name in sorted(field_map.keys()):
            info = field_map[f_name]
            key = f_name.replace('@', '').replace('-', '_').upper()
            if not key or key[0].isdigit(): key = "F_" + key
            
            owners = sorted(list(info['owners']))
            if len(owners) > 25: 
                owners_str = "ApiTypes.ALL.value"
            else:
                owner_refs = [f"ApiTypes.{o.upper().replace('-', '_').replace('.', '_')}.value" for o in owners]
                owners_str = "[" + ", ".join(owner_refs) + "]"
            
            f.write(f"    {key} = ('{f_name}', {info['type']}, {owners_str})\n")

generate_sysml_files('ptc-25-02-30.json')