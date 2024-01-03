from rest_framework import permissions


class UserInfoOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, userinfo):
        return request.user and request.user == userinfo.user
