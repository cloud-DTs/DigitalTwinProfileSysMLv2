import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from src.api.ElementRepository import ElementRepository
from src.api.SysmlElement import SysmlElement
from src.api.SysmlTraversal import SysmlTraversal
from src.mapper.ModelMapper import ModelMapper, StrategyRoutine
from src.path_mapping import PATH_MAP_ENV
from src.TargetModel.twin_condition import Condition
from src.TargetModel.twin_measureAttribute import MeasureAttribute
from src.utils.Repository import Repository
import src.utils.globals as globals


class StrategyRoutineTests(unittest.TestCase):
    def setUp(self):
        database = Repository()
        self.condition = Condition(name="limits")
        database.shared_id_wrapper.dataTable[("condition",)] = self.condition
        database_patch = patch.object(globals, "DATABASE", database)
        database_patch.start()
        self.addCleanup(database_patch.stop)
        self.element = SysmlElement.parseRaw(
            {"@id": "action", "@type": "PartUsage", "name": "setTemperature"}
        )
        self.traversal = Mock(spec=SysmlTraversal)
        self.traversal.resolve_enum_ref.side_effect = lambda element, name: {
            "strategyType": "LAMBDA", "feedbackTopicType": "NOFEEDBACK"
        }.get(name)
        self.strings = {"pathToCode": "/host/code/action"}
        self.traversal.resolve_string.side_effect = lambda element, name: self.strings.get(name)
        self.traversal.resolve_bool.return_value = True
        self.traversal.resolve_chain_ref.return_value = None
        self.traversal.getAllParametersByParent.return_value = []
        mapper = ModelMapper(ElementRepository(), {}, {}, {})
        mapper.traversal = self.traversal
        self.routine = StrategyRoutine(mapper)

    def map_strategy(self):
        return self.routine.map(self.element, None, ["condition", "action"], ["condition"])

    def test_maps_named_input_and_output_parameter_bindings(self):
        measured = MeasureAttribute(name="measuredTemperature")
        target = MeasureAttribute(name="targetTemperature")
        bindings = {
            "inputParameters": [SysmlElement.parseRaw({"@id": "input", "name": "measured"})],
            "outputParameters": [SysmlElement.parseRaw({"@id": "output", "name": "target"})],
        }
        self.traversal.getAllParametersByParent.side_effect = lambda element, name: bindings[name]
        self.traversal.resolve_chain_ref.side_effect = lambda element, name: {
            "measured": measured, "target": target
        }.get(name)

        strategy = self.map_strategy()

        self.assertEqual(
            [(p.customName, p.attribute) for p in strategy.inputParameters],
            [("measured", measured)],
        )
        self.assertEqual(
            [(p.customName, p.attribute) for p in strategy.outputParameters],
            [("target", target)],
        )
        self.assertEqual(self.condition.strategy, [strategy])

    def test_applies_configured_host_path_mapping_for_local_strategy(self):
        with tempfile.TemporaryDirectory() as directory:
            self.traversal.resolve_bool.return_value = False
            self.strings["pathToCode"] = r"C:\host\code\action"
            action_directory = Path(directory, "action")
            action_directory.mkdir()
            with patch.dict(os.environ, {PATH_MAP_ENV: f"C:\\host\\code={directory}"}):
                strategy = self.map_strategy()

            self.assertEqual(strategy.pathToCode, str(action_directory))

    def test_rejects_unresolved_named_parameter_bindings(self):
        binding = SysmlElement.parseRaw({"@id": "binding", "name": "temperature"})
        for collection in ("inputParameters", "outputParameters"):
            with self.subTest(collection=collection):
                self.traversal.getAllParametersByParent.side_effect = (
                    lambda element, name: [binding] if name == collection else []
                )

                with self.assertRaisesRegex(ValueError, "temperature"):
                    self.map_strategy()


if __name__ == "__main__":
    unittest.main()
