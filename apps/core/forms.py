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
