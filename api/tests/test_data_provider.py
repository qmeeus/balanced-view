import unittest
from api.data_provider import __main__ as main


class TestDataProvider(unittest.TestCase):

    def test_data_provider(self):
        main()


if __name__ == '__main__':
    unittest.main()
