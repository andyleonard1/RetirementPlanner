import unittest
from pathlib import Path


class Sprint234LegacyAssumptionAccessGuardTests(unittest.TestCase):
    LEGACY_KEYS = ("inflation", "savings_interest", "pension_growth")

    def _planner_sources(self):
        root = Path("planner")
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts or path.name == "assumption_resolver.py":
                continue
            yield path, path.read_text(encoding="utf-8")

    def test_legacy_alias_reads_are_confined_to_resolver(self):
        forbidden_fragments = tuple(
            f'assumptions.get("{key}")' for key in self.LEGACY_KEYS
        ) + tuple(
            f"assumptions.get('{key}')" for key in self.LEGACY_KEYS
        )
        offenders = []
        for path, source in self._planner_sources():
            for fragment in forbidden_fragments:
                if fragment in source:
                    offenders.append(f"{path}: {fragment}")
        self.assertEqual([], offenders)

    def test_legacy_aliases_are_declared_only_by_assumption_resolver(self):
        source = Path("planner/assumption_resolver.py").read_text(encoding="utf-8")
        for key in self.LEGACY_KEYS:
            self.assertIn(f'"{key}"', source)

    def test_no_direct_legacy_index_reads_exist_in_planner_sources(self):
        forbidden_fragments = tuple(
            f'assumptions["{key}"]' for key in self.LEGACY_KEYS
        ) + tuple(
            f"assumptions['{key}']" for key in self.LEGACY_KEYS
        )
        offenders = []
        for path, source in self._planner_sources():
            for fragment in forbidden_fragments:
                if fragment in source:
                    offenders.append(f"{path}: {fragment}")
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
