from rest_framework import permissions


class IsAdminOrSellerOrReadOnly(permissions.BasePermission):

    # Custom permission allowing read-only access to any user,and write access only to users with ADMIN or SELLER role.

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated and
            (request.user.is_admin or request.user.is_seller)
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_admin:
            return True
        return hasattr(obj, 'user') and obj.user == request.user


class IsReviewOwnerOrReadOnly(permissions.BasePermission):

     # Custom permission allowing review creation to authenticated users, and update/delete access only to the review owner or admin.

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_admin
