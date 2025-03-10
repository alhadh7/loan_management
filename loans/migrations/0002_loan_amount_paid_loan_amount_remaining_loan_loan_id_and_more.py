# Generated by Django 5.1.5 on 2025-02-26 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("loans", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="loan",
            name="amount_paid",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="loan",
            name="amount_remaining",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="loan",
            name="loan_id",
            field=models.CharField(
                default="LOAN000", editable=False, max_length=10, unique=True
            ),
        ),
        migrations.AddField(
            model_name="loan",
            name="next_due_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="loaninstallment",
            name="installment_no",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
