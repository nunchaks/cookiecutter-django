# -*- coding: utf-8 -*-

"""Update user created_by and modified_by foreign key fields to any model automatically.
   Almost entirely taken from https://github.com/Atomidata/django-audit-log/blob/master/audit_log/middleware.py"""
from django.conf import settings
from django.db.models import signals
from django.utils.functional import curry

AUTHOR_CREATED_BY_FIELD_NAME = getattr(settings, 'AUTHOR_CREATED_BY_FIELD_NAME', 'created_by')
AUTHOR_UPDATED_BY_FIELD_NAME = getattr(settings, 'AUTHOR_UPDATED_BY_FIELD_NAME', 'updated_by')


# Source: https://gist.github.com/mindlace/3918300
class AuthorMiddleware(object):
    def process_request(self, request):
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user
            else:
                user = None

            mark_whodid = curry(self.mark_whodid, user)
            signals.pre_save.connect(mark_whodid, dispatch_uid=(self.__class__, request,), weak=False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        return response

    def mark_whodid(self, user, sender, instance, **kwargs):
        if not getattr(instance, '%s_id' % AUTHOR_CREATED_BY_FIELD_NAME, None):
            setattr(instance, AUTHOR_CREATED_BY_FIELD_NAME, user)
        if hasattr(instance, '%s_id' % AUTHOR_UPDATED_BY_FIELD_NAME):
            setattr(instance, AUTHOR_UPDATED_BY_FIELD_NAME, user)
