from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import ClientProfile
from .serializers import ClientProfileSerializer
import logging

logger = logging.getLogger(__name__)


class ClientProfileView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        if not request.user.is_client:
            return Response({'error': 'Only clients can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_verified:
            return Response({'error': 'Account must be verified to access profile'}, status=status.HTTP_403_FORBIDDEN)
        try:
            profile = request.user.client_profile
            serializer = ClientProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ClientProfile.DoesNotExist:
            return Response({'error': 'Client profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if not request.user.is_client:
            return Response({'error': 'Only clients can create a profile'}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_verified:
            return Response({'error': 'Account must be verified to create a profile'}, status=status.HTTP_403_FORBIDDEN)
        if hasattr(request.user, 'client_profile'):
            return Response({'error': 'Client profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ClientProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            logger.info(f"Client profile created for user: {request.user.username} (Phone: {request.user.phone}, Role: Client)")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if not request.user.is_client:
            return Response({'error': 'Only clients can update their profile'}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_verified:
            return Response({'error': 'Account must be verified to update profile'}, status=status.HTTP_403_FORBIDDEN)
        try:
            profile = request.user.client_profile
        except ClientProfile.DoesNotExist:
            return Response({'error': 'Client profile not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClientProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Client profile updated for user: {request.user.username} (Phone: {request.user.phone}, Role: Client)")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)