from sysml_code_generator.mapper.exceptions import NoMappingForSysMLType
from sysml_code_generator.model.sysml.action_definition import ActionDefinition
from sysml_code_generator.model.sysml.action_usage import ActionUsage
from sysml_code_generator.model.sysml.attribute_usage import AttributeUsage
from sysml_code_generator.model.sysml.data_type import DataType
from sysml_code_generator.model.sysml.feature import Feature
from sysml_code_generator.model.sysml.feature_chain_expression import (
    FeatureChainExpression,
)
from sysml_code_generator.model.sysml.feature_reference_expression import (
    FeatureReferenceExpression,
)
from sysml_code_generator.model.sysml.not_implemented import NotImplementedSysMLEntity
from sysml_code_generator.model.sysml.operator_expression import OperatorExpression
from sysml_code_generator.model.sysml.part_definition import PartDefinition
from sysml_code_generator.model.sysml.perform_action_usage import PerformActionUsage
from sysml_code_generator.model.sysml.reference_usage import ReferenceUsage
from sysml_code_generator.model.sysml.state_definition import StateDefinition
from sysml_code_generator.model.sysml.state_subaction_membership import (
    StateSubactionMembership,
)
from sysml_code_generator.model.sysml.state_usage import StateUsage
from sysml_code_generator.model.sysml.succession_as_usage import SuccessionAsUsage
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity
from sysml_code_generator.model.sysml.transition_usage import TransitionUsage


class ApiMapper:
    def map(self, api_element: dict) -> SysMLEntity:
        type_ = api_element["@type"]

        if type_ == "StateDefinition":
            instance = StateDefinition.from_dict(api_element)
        elif type_ == "StateUsage":
            instance = StateUsage.from_dict(api_element)
        elif type_ == "ActionUsage":
            instance = ActionUsage.from_dict(api_element)
        elif type_ == "PerformActionUsage":
            instance = PerformActionUsage.from_dict(api_element)
        elif type_ == "SuccessionAsUsage":
            instance = SuccessionAsUsage.from_dict(api_element)
        elif type_ == "TransitionUsage":
            instance = TransitionUsage.from_dict(api_element)
        elif type_ == "FeatureReferenceExpression":
            instance = FeatureReferenceExpression.from_dict(api_element)
        elif type_ == "ReferenceUsage":
            instance = ReferenceUsage.from_dict(api_element)
        elif type_ == "DataType":
            instance = DataType.from_dict(api_element)
        elif type_ == "OperatorExpression":
            instance = OperatorExpression.from_dict(api_element)
        elif type_ == "Feature":
            instance = Feature.from_dict(api_element)
        elif type_ == "FeatureChainExpression":
            instance = FeatureChainExpression.from_dict(api_element)
        elif type_ == "PartDefinition":
            instance = PartDefinition.from_dict(api_element)
        elif type_ == "AttributeUsage":
            instance = AttributeUsage.from_dict(api_element)
        elif type_ == "ActionDefinition":
            instance = ActionDefinition.from_dict(api_element)
        elif type_ == "StateSubactionMembership":
            instance = StateSubactionMembership.from_dict(api_element)
        else:
            instance = NotImplementedSysMLEntity.from_dict(api_element)
            # raise NoMappingForSysMLType(f"Mapping for '{type_}' not implemented.")

        return instance
