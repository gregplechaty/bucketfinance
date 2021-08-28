import datetime
import requests
import pygal
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import SuspiciousOperation
from apps.accounts.models import User
from apps.core.models import Bucket, Transaction, BankAccount, BankAccountStatus
from apps.core.forms import AddBucket, AddTransaction, AddBankAccount, AddBankAccountStatus
from .shared import bucket_amount_sum, get_buckets_transactions, get_account_data
from .monthly_check_in import create_post_type_array, create_array_from_form, save_check_in_transactions, difference_in_transactions_and_account_balances
from django.utils import timezone

#################### VIEWS ####################

@login_required
def dashboard(request):
    buckets, transactions, buckets_with_sum = get_buckets_transactions(request)
    accounts, statuses = get_account_data(request)
    #difference = difference_in_transactions_and_account_balances(request, buckets_with_sum, accounts)
    context = {
        'user': request.user,
        'transactions': transactions,
        'buckets_with_sum': buckets_with_sum,
        'accounts': accounts,
        'statuses': statuses,
        #'difference': difference,
    }
    return render(request, 'pages/dashboard.html', context)

#################### CRUD Operations: Buckets ####################

@login_required
def create_bucket(request):
    if request.method == 'POST':
        form = AddBucket(request.POST)
        if form.is_valid():
            bucket = form.save(commit=False)
            bucket.user = request.user
            bucket.save()
            return redirect('/dashboard')
    else:
        form = AddBucket()
    context = {
        'form': form,
    }
    return render(request, 'pages/form_page.html', context)

@login_required
def edit_bucket(request, bucket_id):
    bucket_to_modify = Bucket.objects.get(id=bucket_id)
    if request.method == 'POST':
        form = AddBucket(request.POST, instance=bucket_to_modify)
        if form.is_valid():
            bucket_to_modify = form.save()
            return redirect(dashboard)
    else:
        form = AddBucket(instance=bucket_to_modify)
    context = {
        'form': form,
    }
    return render(request, 'pages/form_page.html', context)

@login_required
def delete_bucket(request, bucket_id):
    bucket_to_delete = Bucket.objects.get(id=bucket_id)
    if bucket_to_delete.user != request.user:
        raise SuspiciousOperation("Attempted to delete different user's bucket")
    elif request.method == 'POST':
        #same functions from other check-in
        bucket_id_array = create_post_type_array(request)
        transaction_description = 'Reallocated from deleted bucket: ' + bucket_to_delete.bucketName
        transaction_array = create_array_from_form(request, bucket_id_array, transaction_description)
        save_check_in_transactions(request, transaction_array)
        bucket_to_delete.removedDate = timezone.now()
        bucket_to_delete.save()
        return redirect('/dashboard')
    
    buckets, transactions, buckets_with_sum = get_buckets_transactions(request)
    buckets_excluding_deleted = buckets_with_sum.exclude(id=bucket_id)
    buckets_sum = bucket_amount_sum(buckets_excluding_deleted)
    bucket_deleted_funds = bucket_amount_sum([Bucket.objects.get(id=bucket_id)])[0].total_amount
    message = "You have leftover funds from that bucket to reallocate:"
    context = {
        'user': request.user,
        'account_balance_change': bucket_deleted_funds,
        'buckets_with_sum': buckets_sum,
        'header_message': message,  
    }
    return render(request, 'pages/form_fund_allocation.html', context)
        

#################### CRUD Operations: Transactions ####################

@login_required
def create_transaction(request, bucket_id):
    if request.method == 'POST':
        bucket = Bucket.objects.get(id=bucket_id)
        form = AddTransaction(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.bucket = bucket
            transaction.amount = abs(transaction.amount)
            if request.POST['transaction_type'] == 'subtract':
                transaction.amount = transaction.amount * -1
            transaction.save()
            return redirect('monthly_check_in_3')
    else:
        form = AddTransaction()
    context = {
        'form': form,
    }
    return render(request, 'pages/form_page.html', context)

@login_required
def edit_transaction(request, transaction_id):
    transaction_to_modify = Transaction.objects.get(id=transaction_id)
    if request.method == 'POST':
        form = AddTransaction(request.POST, instance=transaction_to_modify)
        if form.is_valid():
            transaction_to_modify = form.save(commit=False)
            transaction_to_modify.amount = abs(transaction_to_modify.amount)
            if request.POST['transaction_type'] == 'subtract':
                transaction_to_modify.amount = transaction_to_modify.amount * -1
            transaction_to_modify.save()
            return redirect('/dashboard')
    else:
        form = AddTransaction(instance=transaction_to_modify)
    context = {
        'form': form,
    }
    return render(request, 'pages/form_page.html', context)

@login_required
def delete_transaction(request, transaction_id):
    transaction_to_delete = Transaction.objects.get(id=transaction_id)
    if transaction_to_delete.user != request.user:
        raise SuspiciousOperation("Attempted to delete different user's transaction")
    else:
        transaction_to_delete.removedDate = datetime.datetime.now()
        transaction_to_delete.save()
        return redirect('/dashboard')

#################### CRUD Operations: Accounts ####################

@login_required
def create_account(request):
    if request.method == 'POST':
        account = create_account_object(request)
        account_status = create_account_status_object(request, account)
        return redirect('/dashboard')
    else:
        form = AddBucket()
    context = {
        'form': form,
    }
    return render(request, 'pages/create-account.html', context)

def create_account_object(request):
    account = AddBankAccount().save(commit=False)
    account.user = request.user
    account.accountName = request.POST['name']
    account.description = request.POST['description']
    account.save()
    return account

def create_account_status_object(request, account):
    account_status = AddBankAccountStatus().save(commit=False)
    account_status.status_date = request.POST['date']
    account_status.amount = request.POST['amount']
    account_status.description = 'Funds in this account when baseline created'
    account_status.bank_account = account
    account_status.save()
    return account_status



def buckets_adjust_to_account_change(request):
    buckets, transactions, buckets_with_sum = get_buckets_transactions(request)
    context = {
        'user': request.user,
        'account_balance_change': net_account_change,
        'buckets_with_sum': buckets_with_sum,
        'header_message': message,  
    }
    return render(request, 'pages/form_fund_allocation.html', context)