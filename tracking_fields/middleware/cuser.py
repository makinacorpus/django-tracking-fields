from __future__ import unicode_literals
import threading
from django.contrib.auth import get_user_model


class CuserMiddleware:
    _thread_local = threading.local()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            self.__class__.set_user(request.user)
            response = self.get_response(request)
            return response
        finally:
            self.__class__.del_user()

    @classmethod
    def get_user(cls, default=None):
        """
        Retrieve user info
        """
        return getattr(cls._thread_local, 'user', default)

    @classmethod
    def set_user(cls, user):
        """
        Store user info
        """
        if isinstance(user, str):
            user_model = get_user_model()
            user = user_model.objects.get(username=user)
        cls._thread_local.user = user

    @classmethod
    def del_user(cls):
        """
        Delete user info
        """
        if hasattr(cls._thread_local, 'user'):
            del cls._thread_local.user