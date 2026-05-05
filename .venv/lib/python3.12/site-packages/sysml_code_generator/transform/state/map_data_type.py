def map_data_type(
    data_type_sysml: str,
) -> str:
    map_ = {  # DataTyp qualifiedName
        "ScalarValues::Boolean": "bool",
        "ScalarValues::Integer": "int",
        "ScalarValues::Real": "double",
    }

    if data_type_sysml not in map_:
        raise ValueError(f"SysML datatype not mapped: {data_type_sysml}")

    return map_[data_type_sysml]
