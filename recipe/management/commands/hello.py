from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string


class Command(BaseCommand):
    help = "This is help text for"

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='count of generated string') # noqa
        parser.add_argument('multy_arguments', nargs='*',
                            help='* -> zero or more, + -> one or more, also we can add type option') # noqa
        parser.add_argument('-p', '--prefix', type=str, help='- or -- flag mean is optional_arg') # noqa
        parser.add_argument('--valid', action='store_true')

    def handle(self, *args, **options):
        # print(options)
        count = options.get('count')
        multy_arguments = options.get('multy_arguments')
        prefix = options.get('prefix')
        valid = options.get('valid')

        print(multy_arguments)

        print(valid)

        for i in range(count):
            if prefix:
                self.stdout.write(f'{prefix}.{get_random_string(length=10)}')
            else:
                self.stdout.write(get_random_string(length=10))
