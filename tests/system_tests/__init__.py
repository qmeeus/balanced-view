from tests.system_tests.test_api import test_balancedview, test_rss
from tests.system_tests.test_ui import test_ui

__all__ = [
    "test_balancedview",
    "test_rss",
    "test_ui",
]

def main():
    test_balancedview()
    test_rss()
    test_ui()
