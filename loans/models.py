# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid



class Loan(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('FORECLOSED', 'Foreclosed'),
    )
    
    loan_id = models.CharField(max_length=10, unique=True, editable=False, default='LOAN000')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[
            MinValueValidator(1000, message="Minimum loan amount is ₹1,000"),
            MaxValueValidator(100000, message="Maximum loan amount is ₹100,000")
        ]
    )
    tenure = models.PositiveIntegerField(
        validators=[
            MinValueValidator(3, message="Minimum tenure is 3 months"),
            MaxValueValidator(24, message="Maximum tenure is 24 months")
        ]
    )
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Annual interest rate
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_interest = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_remaining = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    next_due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.loan_id or self.loan_id == "LOAN000":  # Generate only if loan_id is missing or default
            last_loan = Loan.objects.order_by('-id').first()  # Get last loan based on ID
            if last_loan and last_loan.loan_id.startswith("LOAN"):
                last_id = int(last_loan.loan_id.replace("LOAN", ""))  # Extract numeric part
                self.loan_id = f"LOAN{last_id + 1:03d}"  # Increment and format
            else:
                self.loan_id = "LOAN001"  # First loan should be LOAN001

        if self.amount_remaining is None:  # Ensure amount_remaining is set properly
            self.amount_remaining = self.total_amount

        super().save(*args, **kwargs)  # Save the loan object



class LoanInstallment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
    )
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='installments')
    installment_no = models.PositiveIntegerField(default=1)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    principal = models.DecimalField(max_digits=10, decimal_places=2)
    interest = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    def __str__(self):
        return f"Installment {self.installment_no} for {self.loan.loan_id} - ₹{self.amount} due on {self.due_date}"