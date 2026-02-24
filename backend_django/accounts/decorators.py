from functools import wraps

from django.core.exceptions import PermissionDenied

from .roles import has_role


def role_required(*roles: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                raise PermissionDenied("Требуется авторизация.")
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            if not any(has_role(user, role) for role in roles):
                raise PermissionDenied("Недостаточно прав.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
