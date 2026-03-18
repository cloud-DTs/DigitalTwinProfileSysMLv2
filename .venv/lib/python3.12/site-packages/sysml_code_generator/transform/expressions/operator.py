supported_operators = {
    ">": ">",
    ">=": ">=",
    "<": "<",
    "<=": "<=",
    "and": "&&",
    "or": "||",
    "not": "!",
    "==": "==",
    "!=": "!=",
}

supported_operation_types = {
    ">": ["ScalarValues::Integer", "ScalarValues::Real"],
    ">=": ["ScalarValues::Integer", "ScalarValues::Real"],
    "<": ["ScalarValues::Integer", "ScalarValues::Real"],
    "<=": ["ScalarValues::Integer", "ScalarValues::Real"],
    "and": ["ScalarValues::Boolean"],
    "or": ["ScalarValues::Boolean"],
    "not": ["ScalarValues::Boolean"],
    "==": [
        "ScalarValues::Boolean",
        "ScalarValues::Integer",
        "ScalarValues::Real",
    ],
    "!=": [
        "ScalarValues::Boolean",
        "ScalarValues::Integer",
        "ScalarValues::Real",
    ],
}
