from django.test import SimpleTestCase
from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class CommandTest(SimpleTestCase):
    @patch('recipe.management.commands.wait_for_db.Command.check')
    def test_wait_for_db_ready(self, patched_check):
        patched_check.return_value = True
        call_command('wait_for_db')
        patched_check.assert_called_once_with(databases=['default'])

    @patch('recipe.management.commands.wait_for_db.Command.check')
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        patched_check.side_effect = [Psycopg2Error] * 2 + [OperationalError] * 3 + [True] # noqa
        call_command('wait_for_db')
        patched_check.assert_called_with(databases=['default'])
        self.assertEqual(patched_check.call_count, 6)
