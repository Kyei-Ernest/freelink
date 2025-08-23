from rest_framework import permissions

class IsClientOrFreelancer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.client or request.user == obj.freelancer or request.user.is_staff

class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_client

class IsFreelancer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_freelancer

class IsContractParty(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.contract.client or request.user == obj.contract.freelancer or request.user.is_staff

