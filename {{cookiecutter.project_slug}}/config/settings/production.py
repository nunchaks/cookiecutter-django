"""
Production Configurations

- Use Amazon's S3 for storing static files and uploaded media
- Use mailgun to send emails
- Use Redis for cache
{% if cookiecutter.use_sentry_for_error_reporting == 'y' %}
- Use sentry for error logging
{% endif %}
{% if cookiecutter.use_opbeat == 'y' %}
- Use opbeat for error reporting
{% endif %}
"""

{% if cookiecutter.use_sentry_for_error_reporting == 'y' %}
import logging
{% endif %}

from .base import *  # noqa

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env('DJANGO_SECRET_KEY')


# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

{%- if cookiecutter.use_sentry_for_error_reporting == 'y' %}
# raven sentry client
# See https://docs.sentry.io/clients/python/integrations/django/
INSTALLED_APPS += ['raven.contrib.django.raven_compat', ]
{% endif %}
{%- if cookiecutter.use_whitenoise == 'y' %}
# Use Whitenoise to serve static files
# See: https://whitenoise.readthedocs.io/
WHITENOISE_MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ]
MIDDLEWARE = WHITENOISE_MIDDLEWARE + MIDDLEWARE
{% endif %}
{%- if cookiecutter.use_sentry_for_error_reporting == 'y' -%}
RAVEN_MIDDLEWARE = ['raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware']
MIDDLEWARE = RAVEN_MIDDLEWARE + MIDDLEWARE
{% endif %}
{%- if cookiecutter.use_opbeat == 'y' -%}
# opbeat integration
# See https://opbeat.com/languages/django/
INSTALLED_APPS += ['opbeat.contrib.django', ]
OPBEAT = {
    'ORGANIZATION_ID': env('DJANGO_OPBEAT_ORGANIZATION_ID'),
    'APP_ID': env('DJANGO_OPBEAT_APP_ID'),
    'SECRET_TOKEN': env('DJANGO_OPBEAT_SECRET_TOKEN')
}
MIDDLEWARE = ['opbeat.contrib.django.middleware.OpbeatAPMMiddleware', ] + MIDDLEWARE
{% endif %}

# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy

# HTTP Strict Transport Security - Force modern browsers to connect to the domain name
# only through HTTPS and refuse insecure connection through this time.
# Set this to 60 seconds and then to 518400 (6 days) when you can prove it works
# Should be used only if everything is sure to be served by HTTPS and stay this way!
SECURE_HSTS_SECONDS = 60
# Add includeSubDomains tag to subdomains. Apply if all subdomains are sure to be in HTTPS as well...
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
# Only helps if Django is the front server for serving MEDIA files
# In this case, activate this setting if you wish for the browser not to guess the Content-Type automatically
# and only refer to the Content-Type header, to avoid potential security issue.
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    'DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
# Force browser to block what seems to be XSS attack (JS in GET or POST parameters for instance)
SECURE_BROWSER_XSS_FILTER = True
# Whether to use a secure cookie for the session cookie.
# If this is set to True, the cookie will be marked as “secure,” which means browsers may ensure
# that the cookie is only sent under an HTTPS connection.
SESSION_COOKIE_SECURE = True
# Whether to use HTTPOnly flag on the session cookie. If this is set to True,
# client-side JavaScript will not to be able to access the session cookie.
# There’s not much excuse for leaving this off, either: if your code depends on
# reading session cookies from JavaScript, you’re probably doing it wrong.
SESSION_COOKIE_HTTPONLY = True
# Redirect HTTP to HTTPS through 301. Should be done through nginx for instance for performance reason.
# Intended to be used when this is not an option.
SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
# Whether to use a secure cookie for the CSRF cookie.
CSRF_COOKIE_SECURE = True
# Whether to use HttpOnly flag on the CSRF cookie.
# If you enable this and need to send the value of the CSRF token with Ajax requests, your JavaScript will need
# to pull the value from a hidden CSRF token form input on the page instead of from the cookie.
CSRF_COOKIE_HTTPONLY = True
# Used to prevent clickjacking - fraudulous use of iframe to make people click on other sites without their consent.
# Modern browsers honor the X-Frame-Options HTTP header that indicates whether or not
# a resource is allowed to load within a frame or iframe.
# If the response contains the header with a value of SAMEORIGIN then the browser will only load the resource
# in a frame if the request originated from the same site. If the header is set to DENY then the browser will
# block the resource from loading in a frame no matter which site made the request.
X_FRAME_OPTIONS = 'DENY'

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['{{cookiecutter.domain_name}}', ])
# END SITE CONFIGURATION

INSTALLED_APPS += ['gunicorn', 'django_jenkins', 'django_extensions']


# STORAGE CONFIGURATION
# ------------------------------------------------------------------------------


# Static Assets
# ------------------------
{% if cookiecutter.use_whitenoise == 'y' -%}
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
{%- endif %}


{% if cookiecutter.use_compressor == 'y'-%}
# COMPRESSOR
# ------------------------------------------------------------------------------
COMPRESS_URL = STATIC_URL
COMPRESS_ENABLED = env.bool('COMPRESS_ENABLED', default=True)
{%- endif %}

# EMAIL
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL',
                         default='{{cookiecutter.project_name}} <noreply@{{cookiecutter.domain_name}}>')
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[{{cookiecutter.project_name}}] ')
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

# Anymail with Mailgun
INSTALLED_APPS += ['anymail', ]
ANYMAIL = {
    "SENDGRID_API_KEY": env('DJANGO_SENDGRID_API_KEY'),
}
EMAIL_BACKEND = 'anymail.backends.sendgrid.SendGridBackend'


# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader', ]),
]

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# Use the Heroku-style specification
# Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
DATABASES['default'] = env.db('DATABASE_URL')

# CACHING
# ------------------------------------------------------------------------------
REDIS_LOCATION = '{0}/{1}'.format(env('REDIS_URL', default='redis://127.0.0.1:6379'), 0)

# Heroku URL does not pass the DB number, so we parse it in
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_LOCATION,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,  # mimics memcache behavior.
                                        # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        }
    }
}

{% if cookiecutter.use_sentry_for_error_reporting == 'y' %}
# Sentry Configuration
SENTRY_DSN = env('DJANGO_SENTRY_DSN')
SENTRY_CLIENT = env('DJANGO_SENTRY_CLIENT', default='raven.contrib.django.raven_compat.DjangoClient')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry', ],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', ],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console', ],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console', ],
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry', ],
            'propagate': False,
        },
    },
}
SENTRY_CELERY_LOGLEVEL = env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO)
RAVEN_CONFIG = {
    'CELERY_LOGLEVEL': env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO),
    'DSN': SENTRY_DSN
}
{% elif cookiecutter.use_sentry_for_error_reporting == 'n' %}
# LOGGING CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', ],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', ],
            'level': 'ERROR',
            'propagate': True
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console', 'mail_admins', ],
            'propagate': True
        }
    }
}
{% endif %}
# Custom Admin URL, use {% raw %}{% url 'admin:index' %}{% endraw %}
ADMIN_URL = env('DJANGO_ADMIN_URL')

# Your production stuff: Below this line define 3rd party library settings
# -------------------------------------------------------------------------
PROJECT_APPS = LOCAL_APPS
JENKINS_TASKS = (
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.run_pep8',
)