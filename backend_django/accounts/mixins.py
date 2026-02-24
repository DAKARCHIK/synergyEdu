from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

from .roles import has_role


class RoleRequiredMixin(AccessMixin):
    allowed_roles: tuple[str, ...] = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not any(has_role(request.user, role) for role in self.allowed_roles):
            raise PermissionDenied("Недостаточно прав для доступа к разделу.")
        return super().dispatch(request, *args, **kwargs)
