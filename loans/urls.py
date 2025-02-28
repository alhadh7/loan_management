from django.urls import path

from auth.jwt_utils import CustomTokenObtainPairView
from .views import (
    LoanCreateView, LoanDetailView, LoanForecloseView, LoanDeleteView, LoanInstallmentPayView
)

urlpatterns = [
    # Loan endpoints
    path('loans/', LoanCreateView.as_view(), name='loan-create'),
    path('loans/detail/', LoanDetailView.as_view(), name='loan-detail'),  # No loan_id in URL
    path('loans/foreclose/', LoanForecloseView.as_view(), name='loan-foreclose'),  # No loan_id in URL
    path('loans/pay/', LoanInstallmentPayView.as_view(), name='loan-installment-pay'),  # No loan_id in URL
    path('loans-delete/', LoanDeleteView.as_view(), name='loan-delete'),  # No loan_id in URL
]

