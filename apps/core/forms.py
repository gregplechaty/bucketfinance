from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from .models import Bucket, Transaction
    
class AddBucket(forms.ModelForm):
    class Meta:
        model = Bucket
        fields = ['bucketName', 'bucketDescription']

class AddTransaction(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transactionDate', 'description']

#class TypeAddTransaction(AddTransaction):
    #transaction_type = forms.CharField(max_length=50)

    #class Meta(AddTransaction.Meta):
        #fields = (AddTransaction.Meta.fields, 'transaction_type')

