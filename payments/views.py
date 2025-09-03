from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import DepositSerializer, TransferRecipientSerializer
import uuid
from .services.paystack import initialize_payment, verify_payment, initiate_transfer, create_transfer_recipient


class InitPaymentView(APIView):
    serializer_class = DepositSerializer

    def post(self, request):
        user = request.user
        amount = request.data.get("amount")

        res = initialize_payment(user, amount)

        if res.get("status"):
            return Response(res, status=status.HTTP_200_OK)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)




class VerifyPaymentView(APIView):
    def get(self, request):
        reference = request.query_params.get("reference")
        result = verify_payment(reference)

        if "error" in result:
            return Response({"error": result["error"]}, status=result["status_code"])

        return Response(result["response"], status=result["status_code"])




class InitiateTransferView(APIView):
    def post(self, request):
        user = request.user
        amount = request.data.get("amount")
        recipient_code = request.data.get("recipient_code")

        if not amount or not recipient_code:
            return Response({"error": "Amount and recipient_code are required"}, status=status.HTTP_400_BAD_REQUEST)

        reference = str(uuid.uuid4()).replace("-", "")[:12]  # unique transaction ref

        try:
            transfer_data = initiate_transfer(float(amount), recipient_code, reference)
            return Response({"message": "Transfer initiated", "data": transfer_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateTransferRecipientView(APIView):
    serializer_class = TransferRecipientSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                recipient_code = create_transfer_recipient(
                    serializer.validated_data["name"],
                    serializer.validated_data["account_number"],
                    serializer.validated_data["service_provider"],
                )

                return Response(
                    {
                        "status": "success",
                        "message": "Recipient created successfully",
                        "data": {"recipient_code": recipient_code},
                    },
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                return Response(
                    {
                        "status": "error",
                        "message": "Failed to create recipient",
                        "details": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
