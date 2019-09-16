from tests.unit_tests import main as make_unit_tests
from tests.integration_tests import main as make_integration_tests
from tests.system_tests import main as make_system_tests


__all__ = [
    "make_unit_tests",
    "make_integration_tests",
    "make_system_tests",
]


def main():
    make_unit_tests()
    make_integration_tests()
    make_system_tests()
