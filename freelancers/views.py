# freelancer/views.py
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import FreelancerProfile
from .serializers import FreelancerProfileSerializer
import logging

logger = logging.getLogger(__name__)

class FreelancerProfileView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        if not request.user.is_freelancer:
            return Response({'error': 'Only freelancers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_verified:
            return Response({'error': 'Account must be verified to access profile'}, status=status.HTTP_403_FORBIDDEN)
        try:
            profile = request.user.freelancer_profile
            serializer = FreelancerProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FreelancerProfile.DoesNotExist:
            return Response({'error': 'Freelancer profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if not request.user.is_freelancer:
            return Response({'error': 'Only freelancers can create a profile'}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_verified:
            return Response({'error': 'Account must be verified to create a profile'}, status=status.HTTP_403_FORBIDDEN)
        if hasattr(request.user, 'freelancer_profile'):
            return Response({'error': 'Freelancer profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FreelancerProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            logger.info(f"Profile created for user: {request.user.username} (Phone: {request.user.phone}, Role: Freelancer)")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if not request.user.is_freelancer:
            return Response({'error': 'Only freelancers can update their profile'}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_verified:
            return Response({'error': 'Account must be verified to update profile'}, status=status.HTTP_403_FORBIDDEN)
        try:
            profile = request.user.freelancer_profile
        except FreelancerProfile.DoesNotExist:
            return Response({'error': 'Freelancer profile not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FreelancerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Profile updated for user: {request.user.username} (Phone: {request.user.phone}, Role: Freelancer)")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


