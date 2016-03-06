"""
Django settings for mentor project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
import pymysql
from fnmatch import fnmatch
from varlet import variable
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

pymysql.install_as_MySQLdb()

# set this to false in dev
DEBUG = variable("DEBUG", False)
TEMPLATE_DEBUG = DEBUG
# a list of 2-tuples containing a name and email address. No need to set in dev
ADMINS = variable("ADMINS", [("John Doe", "foo@example.com")])
# the default is safe to use
SECRET_KEY = variable("SECRET_KET", os.urandom(64).decode("latin1"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # database name
        'NAME': variable("DB_NAME", 'mentor'),
        # DB username. The default is fine for dev
        'USER': variable("DB_USER", "root"),
        # DB password. The default is fine for dev
        'PASSWORD': variable("DB_PASSWORD", ''),
        # DB host. The default is fine for dev
        'HOST': variable("DB_HOST", ''),
    }
}

DJANGO_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__)))
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.normpath(os.path.join(DJANGO_DIR, "../"))

AUTH_USER_MODEL = 'users.User'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

ALLOWED_HOSTS = ['.pdx.edu'] + (["*"] if DEBUG else [])

TEST_RUNNER = 'mentor.test_runner.TestRunner'

# allow the use of wildcards in the INTERAL_IPS setting
class IPList(list):
    # do a unix-like glob match
    # E.g. '192.168.1.100' would match '192.*'
    def __contains__(self, ip):
        for ip_pattern in self:
            if fnmatch(ip, ip_pattern):
                return True
        return False

INTERNAL_IPS = IPList(['10.*', '192.168.*'])


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    # 'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'arcutils',
    'permissions',
    'mentor.questionaire',
    'mentor.users',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


# CAS authentication settings
AUTHENTICATION_BACKENDS = (
    'arcutils.cas.backends.CASModelBackend',
    'django.contrib.auth.backends.ModelBackend',
)


ROOT_URLCONF = 'mentor.urls'

WSGI_APPLICATION = 'mentor.wsgi.application'


# Email domain is used to send email to a user, the address is formed by username@EMAIL_DOMAIN
# EMAIL_FROM is the email address that email will be sent from
# EMAIL_LIST is the email address that email will be sent to inform client (specified by client)
EMAIL_DOMAIN = 'pdx.edu'
EMAIL_FROM = 'mentor_no_reply@pdx.edu'
EMAIL_LIST = 'UNST-MAPS-Group@pdx.edu'



# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = False

USE_L10N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(DJANGO_DIR, "static"),
)

STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = '/media/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(DJANGO_DIR, "templates"),
)

# The HOST:PORT of the logstash server you want to pipe logs to
LOGSTASH_ADDRESS = variable("LOGSTASH_ADDRESS", "localhost:5000")

LOGGING_CONFIG = 'arcutils.logging.basic'
