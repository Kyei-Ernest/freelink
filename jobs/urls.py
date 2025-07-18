from django.urls import path
from .views import JobListView, JobCreateView, JobDetailView, ApplyToJobView, ClientJobApplicationsView, CompleteJobView
from .views import SelectFreelancerView

urlpatterns = [
    path('', JobListView.as_view(), name='job-list'),
    path('create', JobCreateView.as_view(), name='job-create'),
    path('<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('<int:pk>/apply/', ApplyToJobView.as_view(), name='apply-job'),
    path('applications/', ClientJobApplicationsView.as_view(), name='client-job-applications'),
    path('applications/<int:pk>/select/', SelectFreelancerView.as_view(), name='select-freelancer'),
    path('<int:pk>/job_status/', CompleteJobView.as_view(), name='complete-job'),
    ]
