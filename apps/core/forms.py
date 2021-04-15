from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from .models import Bucket, Transaction
    
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

#class TypeAddTransaction(AddTransaction):
    #transaction_type = forms.CharField(max_length=50)

    #class Meta(AddTransaction.Meta):
        #fields = (AddTransaction.Meta.fields, 'transaction_type')

