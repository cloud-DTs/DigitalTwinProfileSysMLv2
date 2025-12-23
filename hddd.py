import syside
syside.Compiler
from syside import get_attribute_value
model, _ = syside.load_model([r"path/to/model.sysml"])
for part in model.elements(syside.AttributeUsage):
    print(f"UUsage: {part.name}")