from django.utils import timezone

from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Job, JobApplication
from .serializers import JobSerializer, JobApplicationSerializer

from .serializers import JobCompletionSerializer


class JobListView(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

class JobCreateView(generics.CreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_client:
            return Response({"error": "Only profiles can create jobs."}, status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

class JobDetailView(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]

class ApplyToJobView(generics.ListCreateAPIView):
    queryset = JobApplication.objects.all()
    lookup_field = 'pk'
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_freelancer:
            raise PermissionDenied("Only freelancers can apply to jobs.")
        serializer.save(freelancer=self.request.user)

class ClientJobApplicationsView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_client:
            return JobApplication.objects.none()
        return JobApplication.objects.filter(job__client=user)

class SelectFreelancerView(generics.UpdateAPIView):
    serializer_class = JobApplicationSerializer
    queryset = JobApplication.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        application = self.get_object()
        if application.job.client != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        application.is_selected = True
        application.selected_at = timezone.now()
        application.save()
        application.job.is_open = False
        application.job.save()
        return Response({"message": "Freelancer selected."})

class CompleteJobView(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobCompletionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        job = self.get_object()
        if request.user != job.client:
            return Response({"error": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        job.status = 'completed'
        job.save()
        return Response({"message": "Job marked as completed."})

