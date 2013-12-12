from django.conf import settings

# crowd control
LOGIN_REQUIRED = getattr(settings, 'KNOWLEDGE_LOGIN_REQUIRED', False)
LOGIN_URL = getattr(settings, 'LOGIN_URL', '/accounts/login/')
ALLOW_ANONYMOUS = getattr(settings, 'KNOWLEDGE_ALLOW_ANONYMOUS', False)
AUTO_PUBLICIZE = getattr(settings, 'KNOWLEDGE_AUTO_PUBLICIZE', False)
FREE_RESPONSE = getattr(settings, 'KNOWLEDGE_FREE_RESPONSE', True)

# alerts
ALERTS = getattr(settings, 'KNOWLEDGE_ALERTS', False)
ALERTS_FUNCTION_PATH = getattr(settings, 'KNOWLEDGE_ALERTS_FUNCTION_PATH', 'knowledge.signals.send_alerts')
KN_REDIRECT_PATH = getattr(settings, 'KNOWLEDGE_REDIREC_PATH', 'knowledge_index')

# misc
SLUG_URLS = getattr(settings, 'KNOWLEDGE_SLUG_URLS', True)

NO_SEND_MAIL = getattr(settings, 'KNOWLEDGE_NO_SEND_MAIL', None)