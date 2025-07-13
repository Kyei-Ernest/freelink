from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from jobs.models import Job
from wallet.models import Wallet

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_client:
            total_jobs = Job.objects.filter(client=user).count()
            open_jobs = Job.objects.filter(client=user, status='open').count()
            completed_jobs = Job.objects.filter(client=user, status='completed').count()
        else:
            total_jobs = Job.objects.filter(applications__freelancer=user).count()
            open_jobs = Job.objects.filter(applications__freelancer=user, status='assigned').count()
            completed_jobs = Job.objects.filter(applications__freelancer=user, status='completed').count()

        balance = Wallet.objects.get(user=user).balance

        data = {
            "user": user.username,
            "role": "Client" if user.is_client else "Freelancer",
            "wallet_balance": balance,
            "total_jobs": total_jobs,
            "open_jobs": open_jobs,
            "completed_jobs": completed_jobs,
        }
        return Response(data)