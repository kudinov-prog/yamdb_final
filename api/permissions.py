from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """ Проверка на автора
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(
            user.is_staff or
            user.role == user.ADMIN or
            obj.username == request.user
        )


class IsRoleModeratorPermission(permissions.BasePermission):
    """ Проверка на роль модератора
    """

    def has_premission(self, request, view):
        return request.user.role == request.user.MODERATOR


class IsRoleAdminPermission(permissions.BasePermission):
    """ Проверка на роль администратора
    """

    def has_premission(self, request, view):
        return request.user.role == request.user.ADMIN


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        if user.is_authenticated:
            return bool(user.is_staff or user.role == user.ADMIN)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                view.action in ['update', 'partial_update', 'destroy',
                                'create', ] and
                request.user.role == request.user.ADMIN)


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                view.action in ['update', 'partial_update', 'destroy',
                                'create', ] and
                request.user.role == request.user.MODERATOR)


class IsAnon(permissions.BasePermission):
    def has_permission(self, request, view):
        return (not request.user.is_authenticated and
                view.action in ['list', 'retrieve'])


class RetrieveUpdateDestroyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if (request.method in ['PUT', 'PATCH', 'DELETE'] and
                request.user.is_authenticated):
            return (
                    obj.author == request.user or
                    request.user.role == request.user.ADMIN or
                    request.user.role == request.user.MODERATOR
            )
        elif request.method in ['GET']:
            return True
