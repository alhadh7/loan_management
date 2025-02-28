# serializers.py
from rest_framework import serializers
from .models import Loan, LoanInstallment


class LoanInstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanInstallment
        fields = ['installment_no', 'due_date', 'amount']

class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['amount', 'tenure', 'interest_rate']
        
    def validate_amount(self, value):
        """
        Validate that amount is a number between 1,000 and 100,000.
        """
        if value < 1000 or value > 100000:
            raise serializers.ValidationError("Amount must be between ₹1,000 and ₹100,000.")
        return value
    
    def validate_tenure(self, value):
        """
        Validate that tenure is a whole number between 3 and 24 months.
        """
        if not isinstance(value, int) or value < 3 or value > 24:
            raise serializers.ValidationError("Tenure must be a whole number between 3 and 24 months.")
        return value

class LoanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['loan_id', 'amount', 'tenure', 'monthly_installment', 'total_amount', 
                  'amount_paid', 'amount_remaining', 'next_due_date', 'status', 'created_at']

    def to_representation(self, instance):
        # Get the default representation of the object
        representation = super().to_representation(instance)
        
        # Check if the request is from a staff member
        if self.context['request'].user.is_staff:
            # Add the user field if the request is from a staff member
            representation['user'] = instance.user.username  # You can customize what to show (e.g., username)

        return representation
