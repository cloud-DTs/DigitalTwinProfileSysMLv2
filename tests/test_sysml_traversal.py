import unittest

from src.api.ElementRepository import ElementRepository
from src.api.SysmlElement import SysmlElement
from src.api.SysmlTraversal import SysmlTraversal


class StrategyParameterTraversalTests(unittest.TestCase):
    def setUp(self):
        self.repo = ElementRepository()
        self.traversal = SysmlTraversal(self.repo)

    def add_element(self, element_id, name=None, **fields):
        element = SysmlElement.parseRaw(
            {"@id": element_id, "@type": "AttributeUsage", "name": name, **fields}
        )
        self.repo.elements[element_id] = element
        return element

    def add_subset(self, element_id, name, target):
        subset = self.add_element(
            element_id + "-subset", subsettedFeature={"@id": target.id}
        )
        return self.add_element(
            element_id, name, ownedSubsetting=[{"@id": subset.id}]
        )

    def test_collects_inherited_named_parameters(self):
        for collection in ("inputParameters", "outputParameters"):
            with self.subTest(collection=collection):
                declaration = self.add_element(collection, collection)
                binding = self.add_subset(collection + "-binding", "temperature", declaration)
                action = self.add_element(
                    "action",
                    inheritedFeature=[{"@id": declaration.id}, {"@id": binding.id}],
                )

                self.assertEqual(
                    self.traversal.getAllParametersByParent(action, collection),
                    [binding],
                )

    def test_collection_declarations_are_not_parameter_bindings(self):
        for collection in ("inputParameters", "outputParameters"):
            with self.subTest(collection=collection):
                declaration = self.add_element(collection, collection)
                redefinition = self.add_element(
                    collection + "-redefinition",
                    redefinedFeature={"@id": declaration.id},
                )
                inherited = self.add_element(
                    collection + "-inherited",
                    collection,
                    ownedRedefinition=[{"@id": redefinition.id}],
                )
                action = self.add_element(
                    "action",
                    ownedFeature=[{"@id": declaration.id}],
                    inheritedFeature=[{"@id": inherited.id}],
                )

                self.assertEqual(
                    self.traversal.getAllParametersByParent(action, collection), []
                )

    def test_local_subset_replaces_inherited_parameter_binding(self):
        for collection in ("inputParameters", "outputParameters"):
            with self.subTest(collection=collection):
                declaration = self.add_element(collection, collection)
                inherited = self.add_subset(collection + "-base", "temperature", declaration)
                local = self.add_subset(collection + "-local", "localTemperature", inherited)
                action = self.add_element(
                    "action",
                    ownedFeature=[{"@id": local.id}],
                    inheritedFeature=[{"@id": declaration.id}, {"@id": inherited.id}],
                )

                self.assertEqual(
                    self.traversal.getAllParametersByParent(action, collection),
                    [local],
                )


if __name__ == "__main__":
    unittest.main()
