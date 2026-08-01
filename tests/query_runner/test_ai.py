import unittest

from redash.query_runner.ai import AI
from redash.query_runner.pg import PostgresSQL

class TestAIQueryRunner(unittest.TestCase):
    def setUp(self):
        self.query_runner = PostgresSQL({})

    def test_apply_ai_query(self):
        ai_instance = AI(self.query_runner)

        input_query = "Create a simple 'select 1' query"

        transformed_query = ai_instance.apply_ai_query(input_query)

        self.assertEqual(transformed_query, "SELECT 1")