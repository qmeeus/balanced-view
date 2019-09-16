from tests.integration_tests.test_balancedview import test_balancedview
from tests.integration_tests.test_spider import test_source, test_source_collection

__all__ = [
    "test_balancedview",
    "test_source",
    "test_source_collection",
]

def main():
    test_balancedview()
    test_source()
    test_source_collection()
