DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SITE_ID = 1
DEBUG = True

CELERY_ALWAYS_EAGER = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'data_exporter',
    'data_exporter.tests',
    'djcelery',
]

DATA_EXPORTER_CHANNELS = {
    'polls': 'data_exporter.tests.exports.PollExport'
}
