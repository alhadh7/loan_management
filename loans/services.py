# services.py
from decimal import Decimal
import datetime
from .models import Loan, LoanInstallment

def calculate_loan_details(amount, tenure, interest_rate):
    """
    Calculate EMI-based loan details using the reducing balance method.
    """
    # Convert to Decimal for precision
    amount = Decimal(str(amount))
    tenure = int(tenure)
    interest_rate = Decimal(str(interest_rate))

    # Calculate monthly interest rate
    monthly_interest_rate = (interest_rate / 100) / 12

    # Correct EMI formula
    emi = (amount * monthly_interest_rate * (1 + monthly_interest_rate) ** tenure) / ((1 + monthly_interest_rate) ** tenure - 1)

    # Total interest
    total_amount = emi * tenure
    total_interest = total_amount - amount

    return (
        emi.quantize(Decimal('0.01')),
        total_amount.quantize(Decimal('0.01')),
        total_interest.quantize(Decimal('0.01'))
    )

def create_installment_schedule(loan):
    """
    Create monthly installment schedule for a loan.
    """
    today = datetime.date.today()
    remaining_principal = loan.amount
    monthly_interest_rate = loan.interest_rate / 100 / 12
    next_due_date = None
    
    for month in range(1, loan.tenure + 1):
        # Calculate next due date
        due_date = today.replace(day=1) + datetime.timedelta(days=32 * month)
        due_date = due_date.replace(day=min(today.day, [31, 29 if due_date.year % 4 == 0 and (due_date.year % 100 != 0 or due_date.year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][due_date.month - 1]))
        
        if month == 1:
            next_due_date = due_date
        
        # Calculate interest for this month
        interest = remaining_principal * monthly_interest_rate
        
        # Calculate principal for this month
        principal = loan.monthly_installment - interest
        
        # Create installment record
        LoanInstallment.objects.create(
            loan=loan,
            installment_no=month,
            due_date=due_date,
            amount=loan.monthly_installment,
            principal=principal.quantize(Decimal('0.01')),
            interest=interest.quantize(Decimal('0.01')),
            status='PENDING'
        )
        
        # Update remaining principal
        remaining_principal -= principal
    
    # Update loan with next due date
    if next_due_date:
        loan.next_due_date = next_due_date
        loan.save(update_fields=['next_due_date'])



def calculate_foreclosure_amount(loan, foreclosure_date=None):
    """
    Calculate foreclosure amount for a loan. If foreclosure_date is not provided,
    use today's date.
    """
    if foreclosure_date is None:
        foreclosure_date = datetime.date.today()
    
    # Get paid installments
    paid_installments = loan.installments.filter(status='PAID')
    
    # Calculate paid principal
    paid_principal = sum(installment.principal for installment in paid_installments)
    
    # Calculate remaining principal
    remaining_principal = loan.amount - paid_principal
    
    # Calculate interest until foreclosure date
    # For simplicity, we'll charge interest for the current month only
    # monthly_interest_rate = loan.interest_rate / 100 / 12
    
    #code for daily pro-rata foreclosure 
    # days_in_month = (foreclosure_date - last_paid_date).days
    # interest_until_foreclosure = remaining_principal * monthly_interest_rate * (days_in_month / 30)

    # interest_until_foreclosure = remaining_principal * monthly_interest_rate
    
    interest_until_foreclosure = 0  # No interest charged for current month if foreclosure happens before due date as this is a 100% customer friendly bank


    # Total foreclosure amount
    foreclosure_amount = remaining_principal + interest_until_foreclosure
    
    # Apply a foreclosure discount (example: 5% of remaining interest)
    total_remaining_interest = loan.total_interest - sum(installment.interest for installment in paid_installments)
    # foreclosure_discount = total_remaining_interest * Decimal('0.05')
    # forclosure with 100% interest Waiver
    foreclosure_discount = total_remaining_interest
    final_settlement_amount = foreclosure_amount - foreclosure_discount
    
    return (
        foreclosure_amount.quantize(Decimal('0.01')),
        foreclosure_discount.quantize(Decimal('0.01')),
        final_settlement_amount.quantize(Decimal('0.01'))
    )


# def calculate_foreclosure_amount(loan, foreclosure_date=None):
#     """
#     Calculate foreclosure amount for a loan. If foreclosure_date is not provided,
#     use today's date.
#     """
#     if foreclosure_date is None:
#         foreclosure_date = datetime.date.today()
    
#     # Get paid installments
#     paid_installments = loan.installments.filter(status='PAID')
    
#     # Calculate paid principal
#     paid_principal = sum(installment.principal for installment in paid_installments)
    
#     # Calculate remaining principal
#     remaining_principal = loan.amount - paid_principal
    
#     # Calculate interest until foreclosure date
#     # For simplicity, we'll charge interest for the current month only
#     monthly_interest_rate = loan.interest_rate / 100 / 12
#     interest_until_foreclosure = remaining_principal * monthly_interest_rate
    
#     # Total foreclosure amount
#     foreclosure_amount = remaining_principal + interest_until_foreclosure
    
#     # Apply a foreclosure discount (example: 5% of remaining interest)
#     total_remaining_interest = loan.total_interest - sum(installment.interest for installment in paid_installments)
#     foreclosure_discount = total_remaining_interest * Decimal('0.05')
    
#     final_settlement_amount = foreclosure_amount - foreclosure_discount
    
#     return (
#         foreclosure_amount.quantize(Decimal('0.01')),
#         foreclosure_discount.quantize(Decimal('0.01')),
#         final_settlement_amount.quantize(Decimal('0.01'))
#     )
