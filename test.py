from typing import Any, Optional

# create a method that takes in a type, and either returns the type if it's a single type, or if it is a union, returns a list of the types within the union
def parse_annotation(annotation: Any) -> Any:
    if getattr(annotation, "__origin__", None) is Union:
        return [arg for arg in annotation.__args__]
    return annotation

if __name__ == "__main__":
    from typing import Union
    print(parse_annotation(str|None))