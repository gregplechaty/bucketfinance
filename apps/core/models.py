from django.db import models
from apps.accounts.models import User
# Create your models here.
class Bucket(models.Model):
    # A very simple model example
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    bucketName = models.CharField(max_length=100)
    bucketDescription = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True) # Add current date
    lastModified = models.DateTimeField(auto_now=True)
    removedDate = models.DateTimeField(null=True)

class Transaction(models.Model):
    # A very simple model example
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    bucket = models.ForeignKey(
        Bucket,
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transactionDate = models.DateTimeField()
    description = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True) # Add current date
    lastModified = models.DateTimeField(auto_now=True)
    removedDate = models.DateTimeField(null=True)

class BankAccount(models.Model):
    # A very simple model example
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    accountName = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True) # Add current date
    last_modified = models.DateTimeField(auto_now=True)
    removed_date = models.DateTimeField(null=True)

class BankAccountStatus(models.Model):
    # A very simple model example
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status_date = models.DateTimeField()
    description = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True) # Add current date
    last_modified = models.DateTimeField(auto_now=True)
    removed_date = models.DateTimeField(null=True)