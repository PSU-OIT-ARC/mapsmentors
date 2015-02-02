"""
This test runner loads the fixtures outside of the Django transaction test
system so they are not reloaded on EVERY test.
"""
from django.test.runner import DiscoverRunner
from django.core.management import call_command
from django.conf import settings

fixtures = [
    'choices',
]

class TestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        result = super(TestRunner, self).setup_databases(**kwargs)
        # load fixtures
        for fixture in fixtures:
            call_command('loaddata', fixture)

        # use the MD5 password hasher since it's way faster
        settings.PASSWORD_HASHERS = (
            'django.contrib.auth.hashers.MD5PasswordHasher',
        )
        return result


