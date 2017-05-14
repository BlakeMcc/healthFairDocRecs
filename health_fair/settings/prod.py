from .base import *
import sys

if 'test' in sys.argv:
    from .test import *
    INSTALLED_APPS += TEST_APPS
else:
    ENVIRONMENT = 'production'
    DEBUG = False

    # LOGGING = {
    #     'version': 1,
    #     'disable_existing_loggers': False,
    #     'filters': {
    #         'require_debug_false': {
    #             '()': 'django.utils.log.RequireDebugFalse'
    #         }
    #     },
    #     'formatters': {
    #         'verbose': {
    #             'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
    #             'datefmt': "%d/%b/%Y %H:%M:%S"
    #         },
    #         'simple': {
    #             'format': '%(levelname)s %(message)s'
    #         },
    #     },
    #     'handlers': {
    #         'mail_admins': {
    #             'level': 'ERROR',
    #             'filters': ['require_debug_false'],
    #             'class': 'django.utils.log.AdminEmailHandler'
    #         },
    #         'error': {
    #             'level': 'DEBUG',
    #             'class': 'logging.FileHandler',
    #             'filename': os.path.join(BASE_DIR, 'health_fair', 'log', 'error.log'),
    #             'formatter': 'verbose',
    #         },
    #         'screener': {
    #             'level': 'DEBUG',
    #             'class': 'logging.FileHandler',
    #             'filename': os.path.join(BASE_DIR, 'health_fair', 'log', 'screener.log'),
    #             'formatter': 'verbose',
    #         }
    #     },
    #     'loggers': {
    #         'django': {
    #             'handlers': ['error', 'mail_admins'],
    #             'level': 'ERROR',
    #             'propagate': True,
    #         },
    #         'django.request': {
    #             'handlers': ['error'],
    #             'level': 'ERROR',
    #             'propagate': True,
    #         },
    #         'screener': {
    #             'handlers': ['screener'],
    #             'level': 'DEBUG',
    #             'propagate': True,
    #         }
    #     }
    # }
