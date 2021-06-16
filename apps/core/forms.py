from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from .models import Bucket, Transaction, BankAccount, BankAccountStatus
    
class AddBucket(forms.ModelForm):
    class Meta:
        model = Bucket
        fields = ['bucketName', 'bucketDescription']


transaction_choices = [
    ('add', 'Adding'),
    ('subtract', 'Removing'),
    ]
class AddTransaction(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transactionDate', 'description']
    transaction_type = forms.CharField(label='Are you adding or removing money?', widget=forms.Select(choices=transaction_choices))

class AddBankAccount(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['accountName', 'description']

class AddBankAccountStatus(forms.ModelForm):
    class Meta:
        model = BankAccountStatus
        fields = ['amount', 'status_date', 'description']