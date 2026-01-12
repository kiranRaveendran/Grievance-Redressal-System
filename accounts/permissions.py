from rest_framework import permissions


class IsAdminPanel(permissions.BasePermission):
    """
    Allows access only to:
    - Django superusers
    - Staff users
    - Users with role = 'admin'
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.is_staff
                or getattr(user, 'role', None) == 'admin'
            )
        )

