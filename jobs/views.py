from rest_framework import generics, permissions, viewsets
from .models import Job, Skill
from .serializers import JobSerializer, JobDetailSerializer, JobStatusSerializer, SkillSerializer


class IsClientUser(permissions.BasePermission):
    """
    Custom permission to only allow 'client' users to create jobs.
    Assumes your User model has a 'user_type' field.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_client == True


class IsJobOwner(permissions.BasePermission):
    """
    Custom permission to only allow the owner (client who posted the job)
    to edit, update, or delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user


class JobListCreateView(generics.ListCreateAPIView):
    """
    API endpoint:
    - GET: List all jobs.
    - POST: Create a new job (only allowed for clients).
    """
    queryset = Job.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # Use JobSerializer for creation, JobDetailSerializer for listing
        if self.request.method == 'POST':
            return JobSerializer
        return JobDetailSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.IsAuthenticated, IsClientUser]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Automatically set the client to the logged-in user
        serializer.save(client=self.request.user)


class JobRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, or deleting a job.

    - GET: Retrieve a specific job by ID.
    - PUT/PATCH: Update a job (only the client who created it can update).
    - DELETE: Delete a job (only the client who created it can delete).
    """
    queryset = Job.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsJobOwner]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return JobSerializer
        return JobDetailSerializer


class JobUpdateStatusView(generics.UpdateAPIView):
    """
    API endpoint for updating the status of a job.
    Example: A client marking the job as 'completed' or 'cancelled'.

    - PATCH: Update only the status field.
    """
    queryset = Job.objects.all()
    serializer_class = JobStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobOwner]


class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin users (is_staff=True)."""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class SkillViewSet(viewsets.ModelViewSet):
    """
    API endpoint for admins to manage skills.
    - GET: List all skills
    - POST: Create a new skill
    - PUT/PATCH: Update an existing skill
    - DELETE: Remove a skill
    """
    queryset = Skill.objects.all().order_by("name")
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

