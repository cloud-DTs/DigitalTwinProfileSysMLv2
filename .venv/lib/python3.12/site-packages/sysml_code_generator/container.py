from sysml_code_generator.configuration import Configuration
from sysml_code_generator.generator.auto.auto_generator import AutoGenerator
from sysml_code_generator.generator.c_action.action_c_generator import ActionCGenerator
from sysml_code_generator.generator.c_state.state_c_generator import (
    StateMachineCGenerator,
)
from sysml_code_generator.generator.c_state.state_c_sim_cli_generator import (
    StateMachineSimCliGenerator,
)
from sysml_code_generator.generator.c_state.state_c_sim_gui_generator import (
    StateMachineSimGuiGenerator,
)
from sysml_code_generator.loader.api.api import Api
from sysml_code_generator.loader.api.api_finder import ApiFinder
from sysml_code_generator.loader.api.api_loader import ApiLoader
from sysml_code_generator.loader.json.json_loader import JsonLoader
from sysml_code_generator.loader.repository import Repository
from sysml_code_generator.mapper.api_mapper import ApiMapper
from sysml_code_generator.renderer.common_renderer import Renderer
from sysml_code_generator.search.action.action_loader import ActionLoader
from sysml_code_generator.search.search import Search
from sysml_code_generator.search.state.outgoing_transition_collector import (
    OutgoingTransitionCollector,
)
from sysml_code_generator.search.state.state_machine_loader import StateMachineLoader
from sysml_code_generator.search.transition_usage.guard_collector import GuardCollector
from sysml_code_generator.tool.file_writer import FileWriter
from sysml_code_generator.tool.logger_factory import get_logger
from sysml_code_generator.tool.module_detector import ModuleDetector
from sysml_code_generator.transform.guards.get_guard_c_expressions import (
    GuardCTransformer,
)
from sysml_code_generator.transform.state.action_name_transformer import (
    ActionNameTransformer,
)
from sysml_code_generator.transform.state.collect_actions_from_state import (
    ActionNameCollector,
)
from sysml_code_generator.transform.state.collect_variables_from_state import (
    VariableCollector,
)
from sysml_code_generator.transform.state.condition_transformer import (
    ConditionTransformer,
)
from sysml_code_generator.transform.state.state_machine_transformer import (
    StateMachineTransformer,
)
from sysml_code_generator.transform.state.state_name_transformer import (
    StateNameTransformer,
)
from sysml_code_generator.transform.state.state_transition_transformer import (
    StateTransitionTransformer,
)
from sysml_code_generator.transform.state.state_usage_transformer import (
    StateUsageTransformer,
)


class Container:
    def __init__(
        self,
        config: Configuration = None,
    ):
        self.config = config or Configuration()

        self.mapper = ApiMapper()

        self.logger = get_logger()

        self.repository = Repository()

        self.json_loader = JsonLoader(
            mapper=self.mapper,
            logger=self.logger,
        )

        self.api = Api()

        self.api_finder = ApiFinder(
            api=self.api,
            logger=self.logger,
        )

        self.api_loader = ApiLoader(
            api=self.api,
            mapper=self.mapper,
            logger=self.logger,
        )

        self.search = Search(
            repository=self.repository,
        )

        self.state_machine_loader = StateMachineLoader(
            repository=self.repository,
            search=self.search,
        )

        self.action_loader = ActionLoader(
            repository=self.repository,
            search=self.search,
        )

        self.renderer = Renderer(
            template_folder=self.config.template_folder,
            logger=self.logger,
        )

        self.file_writer = FileWriter(
            logger=self.logger,
        )

        self.action_name_transformer = ActionNameTransformer(
            repository=self.repository,
        )

        self.state_name_transformer = StateNameTransformer(
            repository=self.repository,
        )

        self.outgoing_transition_collector = OutgoingTransitionCollector(
            repository=self.repository,
            search=self.search,
        )

        self.guard_collector = GuardCollector(
            repository=self.repository,
        )

        self.guard_c_transformer = GuardCTransformer(
            repository=self.repository,
        )

        self.condition_transformer = ConditionTransformer(
            guard_collector=self.guard_collector,
            repository=self.repository,
            guard_c_transformer=self.guard_c_transformer,
        )

        self.state_transition_transformer = StateTransitionTransformer(
            condition_transformer=self.condition_transformer,
            state_name_transformer=self.state_name_transformer,
            action_name_transformer=self.action_name_transformer,
            outgoing_transition_collector=self.outgoing_transition_collector,
            repository=self.repository,
        )

        self.state_usage_transformer = StateUsageTransformer(
            transition_transformer=self.state_transition_transformer,
            action_name_transformer=self.action_name_transformer,
        )

        self.action_name_collector = ActionNameCollector(
            action_name_transformer=self.action_name_transformer,
        )

        self.variable_collector = VariableCollector(
            repository=self.repository,
        )

        self.state_machine_transformer = StateMachineTransformer(
            repository=self.repository,
            state_usage_transformer=self.state_usage_transformer,
            state_name_transformer=self.state_name_transformer,
            action_name_collector=self.action_name_collector,
            variable_collector=self.variable_collector,
        )

        self.action_c_generator = ActionCGenerator(
            action_loader=self.action_loader,
            renderer=self.renderer,
        )

        self.state_machine_c_generator = StateMachineCGenerator(
            state_machine_loader=self.state_machine_loader,
            transformer=self.state_machine_transformer,
            renderer=self.renderer,
            logger=self.logger,
        )

        self.state_machine_sim_cli_generator = StateMachineSimCliGenerator(
            state_machine_loader=self.state_machine_loader,
            transformer=self.state_machine_transformer,
            renderer=self.renderer,
            logger=self.logger,
        )

        self.state_machine_sim_gui_generator = StateMachineSimGuiGenerator(
            state_machine_loader=self.state_machine_loader,
            transformer=self.state_machine_transformer,
            renderer=self.renderer,
            logger=self.logger,
        )

        self.module_detector = ModuleDetector(
            logger=self.logger,
            search=self.search,
            state_machine_c_generator=self.state_machine_c_generator,
            action_c_generator=self.action_c_generator,
        )

        self.auto_module = AutoGenerator(
            module_detector=self.module_detector,
        )
