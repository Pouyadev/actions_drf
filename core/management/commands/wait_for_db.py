import time
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_ready = False
        while not db_ready:
            try:
                self.check(databases=['default'])
                db_ready = True
            except (OperationalError, Psycopg2Error):
                self.stdout.write('Database unavailable, waiting for 1 second...') # noqa
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('✔ Database available'))
