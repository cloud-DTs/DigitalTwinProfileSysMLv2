import ast
from .twin_measureAttribute import MeasureAttribute, AttributeDataType
from dataclasses import dataclass


@dataclass
class ConstAttribute(MeasureAttribute):
    value: str = ""

    def to_iot_device_dict(self) -> dict:
        base_dict = super().to_iot_device_dict()
        base_dict.update({
            "initValue": self._cast_value()
        })
        return base_dict

    def to_event_dict(self) -> dict:
        base_dict = super().to_event_dict()
        base_dict.update({
            "value": self._cast_value()
        })
        return base_dict

    def _cast_value(self):
        if self.dataType in (
            AttributeDataType.VECTOR_DOUBLE,
            AttributeDataType.VECTOR_INTEGER,
            AttributeDataType.VECTOR_STRING,
        ):
            return self._cast_vector()
        return self.pythonTypes()(self.value)

    def _cast_vector(self):
        raw = self.value
        parsed = raw if isinstance(raw, (list, tuple)) else ast.literal_eval(raw)
        elem_type = {
            AttributeDataType.VECTOR_DOUBLE: float,
            AttributeDataType.VECTOR_INTEGER: int,
            AttributeDataType.VECTOR_STRING: str,
        }[self.dataType]
        return [elem_type(x) for x in parsed]

    def pythonTypes(self):
        if self.dataType == AttributeDataType.STRING:
            return str
        elif self.dataType == AttributeDataType.INTEGER:
            return int
        elif self.dataType == AttributeDataType.DOUBLE:
            return float
        else:
            return str