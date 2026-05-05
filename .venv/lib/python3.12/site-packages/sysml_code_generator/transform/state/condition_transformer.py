from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.expression import Expression
from sysml_code_generator.model.sysml.transition_usage import TransitionUsage
from sysml_code_generator.search.transition_usage.guard_collector import GuardCollector
from sysml_code_generator.transform.guards.get_guard_c_expressions import (
    GuardCTransformer,
)


class ConditionTransformer:
    def __init__(
        self,
        guard_collector: GuardCollector,
        repository: RepositoryInterface,
        guard_c_transformer: GuardCTransformer,
    ):
        self.__guard_collector = guard_collector
        self.__repository = repository
        self.__guard_c_transformer = guard_c_transformer

    def transform(
        self,
        transition: TransitionUsage,
    ) -> str:
        condition = ""

        guards = self.__guard_collector.get_guards(
            transition_usage=transition,
        )

        if len(guards) > 1:
            raise Exception("Not implemented. (more than one guard)")

        if len(guards) == 1:
            guard_id = guards[0].id
            guard = self.__repository.get(guard_id)

            if not isinstance(guard, Expression):
                type_ = type(guard)
                raise ValueError(
                    f"Expected item to be of type Expression. {guard_id} {type_}"
                )

            condition = self.__guard_c_transformer.transform(
                guard=guard,
            )

        return condition
