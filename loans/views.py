from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Loan, LoanInstallment
from .serializers import LoanCreateSerializer, LoanListSerializer, LoanInstallmentSerializer
from .services import calculate_loan_details, create_installment_schedule, calculate_foreclosure_amount
from auth.permissions import IsAdmin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Loan, LoanInstallment
from .serializers import LoanInstallmentSerializer


class LoanCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Fetch all loans for the authenticated user.
        Admins can view all loans, while regular users can only see their own.
        """
        try:
            if request.user.is_staff:
                loans = Loan.objects.all().order_by('-created_at')
            else:
                loans = Loan.objects.filter(user=request.user).order_by('-created_at')

            # Apply filters if specified
            status_filter = request.query_params.get('status')
            if status_filter:
                loans = loans.filter(status=status_filter.upper())

            # Serialize the loan data
            serializer = LoanListSerializer(loans, many=True, context={'request': request})

            return Response({
                "status": "success",
                "data": {
                    "loans": serializer.data
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception if needed
            print(f"Error while fetching loans: {str(e)}")
            return Response({
                "status": "error",
                "message": "An error occurred while fetching the loans."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def post(self, request):
        try:
            # Deserialize data from request
            serializer = LoanCreateSerializer(data=request.data)
            if serializer.is_valid():
                # Calculate loan details
                monthly_installment, total_amount, total_interest = calculate_loan_details(
                    serializer.validated_data['amount'],
                    serializer.validated_data['tenure'],
                    serializer.validated_data['interest_rate']
                )

                # Create loan object
                loan = Loan.objects.create(
                    user=request.user,
                    amount=serializer.validated_data['amount'],
                    tenure=serializer.validated_data['tenure'],
                    interest_rate=serializer.validated_data['interest_rate'],
                    total_amount=total_amount,
                    total_interest=total_interest,
                    monthly_installment=monthly_installment,
                    amount_remaining=total_amount
                )

                # Create installment schedule
                create_installment_schedule(loan)

                # Get payment schedule
                installments = loan.installments.all().order_by('installment_no')
                installment_data = LoanInstallmentSerializer(installments, many=True).data

                return Response({
                    "status": "success",
                    "data": {
                        "loan_id": loan.loan_id,
                        "amount": float(loan.amount),
                        "tenure": loan.tenure,
                        "interest_rate": f"{loan.interest_rate}% yearly",
                        "monthly_installment": float(loan.monthly_installment),
                        "total_interest": float(loan.total_interest),
                        "total_amount": float(loan.total_amount),
                        "payment_schedule": installment_data
                    }
                }, status=status.HTTP_201_CREATED)

            return Response({
                "status": "error",
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as ve:
            # Handle specific known error cases like value errors
            return Response({
                "status": "error",
                "message": f"Invalid input: {str(ve)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error while creating loan: {str(e)}")
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while processing the loan."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoanDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Retrieve loan details using JSON input instead of URL parameters.
        JSON format: {"loan_id": "LOAN001"}
        """
        try:
            loan_id = request.data.get("loan_id")  # Get loan_id from request body

            if not loan_id:
                return Response({
                    "status": "error",
                    "message": "Loan ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the loan object, or return 404 if not found
            loan = get_object_or_404(Loan, loan_id=loan_id)

            # Check permissions: only the user who owns the loan or admins can access the details
            if not request.user.is_staff and loan.user != request.user:
                return Response({
                    "status": "error",
                    "message": "You don't have permission to view this loan."
                }, status=status.HTTP_403_FORBIDDEN)

            # Get installments associated with the loan
            installments = loan.installments.all().order_by('installment_no')
            installment_data = LoanInstallmentSerializer(installments, many=True).data

            # Return the loan details and installment schedule
            return Response({
                "status": "success",
                "data": {
                    "loan_id": loan.loan_id,
                    "amount": float(loan.amount),
                    "tenure": loan.tenure,
                    "interest_rate": f"{loan.interest_rate}% yearly",
                    "monthly_installment": float(loan.monthly_installment),
                    "total_interest": float(loan.total_interest),
                    "total_amount": float(loan.total_amount),
                    "amount_paid": float(loan.amount_paid),
                    "amount_remaining": float(loan.amount_remaining),
                    "next_due_date": loan.next_due_date,
                    "status": loan.status,
                    "created_at": loan.created_at,
                    "payment_schedule": installment_data
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error while retrieving loan details: {str(e)}")
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while retrieving loan details."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoanInstallmentPayView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Pay an installment for a loan.
        JSON format: {"loan_id": "LOAN001", "installment_no": 1}
        """
        try:
            loan_id = request.data.get("loan_id")
            installment_no = request.data.get("installment_no")

            # Validate input
            if not loan_id:
                return Response({
                    "status": "error",
                    "message": "Loan ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)

            if not installment_no:
                return Response({
                    "status": "error",
                    "message": "Installment number is required."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the loan
            loan = get_object_or_404(Loan, loan_id=loan_id)

            # Check permissions
            if not request.user.is_staff and loan.user != request.user:
                return Response({
                    "status": "error",
                    "message": "You don't have permission to pay installments for this loan."
                }, status=status.HTTP_403_FORBIDDEN)

            # Check if loan is active
            if loan.status != 'ACTIVE':
                return Response({
                    "status": "error",
                    "message": f"Cannot pay installment. Loan status is {loan.status}."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the installment
            try:
                installment = loan.installments.get(installment_no=installment_no)
            except LoanInstallment.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": f"Installment {installment_no} not found for loan {loan_id}."
                }, status=status.HTTP_404_NOT_FOUND)

            # Check if installment is already paid
            if installment.status == 'PAID':
                return Response({
                    "status": "error",
                    "message": f"Installment {installment_no} has already been paid."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Mark installment as paid
            installment.status = 'PAID'
            installment.save()

            # Update loan information
            loan.amount_paid += installment.amount
            loan.amount_remaining -= installment.amount

            # Find next due date from next pending installment
            next_pending = loan.installments.filter(status='PENDING').order_by('installment_no').first()
            if next_pending:
                loan.next_due_date = next_pending.due_date
            else:
                # All installments paid, close the loan
                loan.status = 'CLOSED'
                loan.next_due_date = None

            loan.save()

            # Get updated payment schedule
            installments = loan.installments.all().order_by('installment_no')
            installment_data = LoanInstallmentSerializer(installments, many=True).data

            return Response({
                "status": "success",
                "message": f"Installment {installment_no} paid successfully.",
                "data": {
                    "loan_id": loan.loan_id,
                    "amount_paid": float(loan.amount_paid),
                    "amount_remaining": float(loan.amount_remaining),
                    "next_due_date": loan.next_due_date,
                    "status": loan.status,
                    "payment_schedule": installment_data
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error while processing installment payment: {str(e)}")
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while processing the payment."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoanForecloseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Foreclose a loan using JSON input instead of URL parameters.
        JSON format: {"loan_id": "LOAN001"}
        """
        try:
            loan_id = request.data.get("loan_id")

            # Validate input
            if not loan_id:
                return Response({
                    "status": "error",
                    "message": "Loan ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the loan object or return 404 if not found
            loan = get_object_or_404(Loan, loan_id=loan_id)

            # Check permissions: only the user who owns the loan or an admin can foreclose it
            if not request.user.is_staff and loan.user != request.user:
                return Response({
                    "status": "error",
                    "message": "You don't have permission to foreclose this loan."
                }, status=status.HTTP_403_FORBIDDEN)

            # Check if loan is active
            if loan.status != 'ACTIVE':
                return Response({
                    "status": "error",
                    "message": "Only active loans can be foreclosed."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Calculate foreclosure amounts
            foreclosure_amount, foreclosure_discount, final_settlement_amount = calculate_foreclosure_amount(loan)

            # Get the amount already paid
            already_paid = loan.amount_paid

            # Update loan status
            loan.status = 'FORECLOSED'
            loan.amount_paid = already_paid + final_settlement_amount
            loan.amount_remaining = 0
            loan.save()

            # Update all pending installments to closed
            loan.installments.filter(status='PENDING').update(status='PAID')

            # Return the response with success status
            return Response({
                "status": "success",
                "message": "Loan foreclosed successfully.",
                "data": {
                    "loan_id": loan.loan_id,
                    "amount_paid": float(loan.amount_paid),  # Total amount paid
                    "foreclosure_amount": float(foreclosure_amount), #amount before discount
                    "foreclosure_discount": float(foreclosure_discount),
                    "final_settlement_amount": float(final_settlement_amount),
                    "status": "FORECLOSED"
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error while processing loan foreclosure: {str(e)}")
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while processing the loan foreclosure."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        # return Response({
        #     "status": "success",
        #     "message": "Loan foreclosed successfully.",
        #     "data": {
        #         "loan_id": loan.loan_id,
        #         "previous_amount_paid": float(already_paid),
        #         "foreclosure_amount": float(foreclosure_amount), #amount before discount
        #         "foreclosure_discount": float(foreclosure_discount),
        #         "final_settlement_amount": float(final_settlement_amount),
        #         "total_amount_paid": float(loan.amount_paid),
        #         "status": loan.status
        #     }
        # }, status=status.HTTP_200_OK)


class LoanDeleteView(APIView):
    permission_classes = [IsAdmin]  # Only admins can delete loans

    def delete(self, request):
        """
        Delete a loan using JSON input instead of URL parameters.
        JSON format: {"loan_id": "LOAN001"}
        """
        try:
            loan_id = request.data.get("loan_id")  # Get loan_id from request body

            # Validate input
            if not loan_id:
                return Response({
                    "status": "error",
                    "message": "Loan ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the loan object or return 404 if not found
            loan = get_object_or_404(Loan, loan_id=loan_id)

            # Delete the loan
            loan.delete()

            # Return success response
            return Response({
                "status": "success",
                "message": "Loan deleted successfully."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error while deleting loan {loan_id}: {str(e)}")
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while deleting the loan.",
                "error_details": str(e)  # Provide the exception details in the response

            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        

from django.http import JsonResponse

def custom_400(request, exception):
    return JsonResponse({
        'error': 'Bad Request',
        'message': 'The request could not be understood or was missing required parameters.'
    }, status=400)

def custom_403(request, exception):
    return JsonResponse({
        'error': 'Forbidden',
        'message': 'You do not have permission to access this resource.'
    }, status=403)

def custom_404(request, exception):
    return JsonResponse({
        'error': 'Not Found',
        'message': 'The requested resource was not found on this server.'
    }, status=404)

def custom_405(request, exception):
    return JsonResponse({
        'error': 'Method Not Allowed',
        'message': 'The method is not allowed for this endpoint.'
    }, status=405)

def custom_500(request):
    return JsonResponse({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred on the server.'
    }, status=500)
