from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.expression import Expression
from sysml_code_generator.model.sysml.transition_usage import TransitionUsage


class GuardCollector:
    def __init__(
        self,
        repository: RepositoryInterface,
    ):
        self.__repository = repository

    def get_guards(
        self,
        transition_usage: TransitionUsage,
    ) -> list[Expression]:
        guards = []

        for guard_id in transition_usage.guard_expression_ids:
            guard = self.__repository.get(item_id=guard_id)

            if not isinstance(guard, Expression):
                type_ = type(guard)
                raise ValueError(
                    f"Expected guard to be of type Expression: {guard_id} {type_}"
                )

            if guard is not None:
                guards.append(guard)

        return guards
