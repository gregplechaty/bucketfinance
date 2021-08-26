import requests
import pygal
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import SuspiciousOperation
from django.utils import timezone
from apps.accounts.models import User
from apps.core.models import Bucket, Transaction, BankAccount, BankAccountStatus
from apps.core.forms import AddBucket, AddTransaction, AddBankAccount, AddBankAccountStatus
from .shared import bucket_amount_sum, get_buckets_transactions

#################### VIEWS ####################

@login_required
def monthly_check_in_1(request):
    context = {
        'user': request.user,
    }
    return render(request, 'pages/month_check_in_1.html', context)

@login_required
def monthly_check_in_2(request):
    if request.method == 'POST':
        account_status_array = create_account_status_array(request)
        save_account_status(account_status_array)
        return redirect('monthly_check_in_3')
    accounts = get_bank_account_info_two(request)
    context = {
        'user': request.user,
        'accounts': accounts,
    }
    return render(request, 'pages/month_check_in_2.html', context)

@login_required
def monthly_check_in_3(request):
    if request.method == 'POST':
        #TODO: Logic to reject bad add/remove amount
        bucket_id_array = create_post_type_array(request)
        transaction_array = create_array_from_form(request, bucket_id_array)
        save_check_in_transactions(request, transaction_array)
        return redirect(check_in_success)
    buckets, transactions, buckets_with_sum = get_buckets_transactions(request)
    context = {
        'user': request.user,
        'account_balance_change': change_in_all_accounts_balance(request),
        'buckets_with_sum': buckets_with_sum,
        'header_message': 'Step 3: Your account balance changed by:',  
    }
    return render(request, 'pages/form_fund_allocation.html', context)

@login_required
def check_in_success(request):
    context = {
        'user': request.user,
    }
    return render(request, 'pages/month_check_in_success.html', context)

#################### CRUD Operations ####################

def save_check_in_transactions(request, transaction_array):
    for transaction in transaction_array:
            new_transaction = AddTransaction().save(commit=False)
            new_transaction.user = request.user
            new_transaction.bucket = Bucket.objects.get(id=transaction["bucket_id"])
            new_transaction.amount = transaction["amount"]
            new_transaction.transactionDate = timezone.now()
            new_transaction.description = transaction["description"]
            new_transaction.save()


def save_account_status(account_status_array):
    for account in account_status_array:
            account_status = AddBankAccountStatus().save(commit=False)
            account_status.amount = account["amount"]
            account_status.status_date = account["date"]
            account_status.description = account["description"]
            current_bank_account = BankAccount.objects.get(id=int(account["account_id"]))
            account_status.bank_account = current_bank_account
            account_status.save()

@login_required
def create_account_2(request):
    if request.method == 'POST':
        form = AddBankAccount(request.POST)
        if form.is_valid():
            bucket = form.save(commit=False)
            bucket.user = request.user
            bucket.save()
            return redirect('monthly_check_in_2')
    else:
        form = AddBankAccount()
    context = {
        'form': form,
    }
    return render(request, 'pages/form_page.html', context)

############################# HELPER FUNCTIONS #############################


def get_bank_account_info_two(request,record="current"):
    accounts = BankAccount.objects.filter(user=request.user, removed_date__isnull=True)
    all_statuses_for_these_accounts = BankAccountStatus.objects.filter(bank_account__in=accounts).order_by('-status_date')
    ## Here we add last status check-in to the account info
    for account in accounts:
        account_statuses = BankAccountStatus.objects.filter(bank_account=account, removed_date__isnull=True).order_by('-status_date')
        if record == 'previous' and len(account_statuses) > 1:
            account_status = BankAccountStatus.objects.filter(bank_account=account, removed_date__isnull=True).order_by('-status_date')[1:2]
        # defaults to 'top of stack' record
        elif record == 'previous' and len(account_statuses) == 1:
            account_status = BankAccountStatus.objects.filter(bank_account=account, removed_date__isnull=True).order_by('-status_date')[:1]
            account_status[0].amount = 0
            account_status[0].status_date = timezone.now().replace(year=1800, month=1,day=1)
        else:
            account_status = BankAccountStatus.objects.filter(bank_account=account, removed_date__isnull=True).order_by('-status_date')[:1]
        if len(all_statuses_for_these_accounts) == 0:
            account.last_check_in_date = 'None. Start your first check-in below by clicking "Continue!"'
            account.newest_amount = 0
        else:
            account.last_check_in_date = account_status[0].status_date
            account.newest_amount = account_status[0].amount
    return accounts

def change_in_all_accounts_balance(request):
    accounts = get_bank_account_info_two(request)
    previous_account_info = get_bank_account_info_two(request, 'previous')
    change_in_all_accounts = sum_of_all_accounts(accounts) - sum_of_all_accounts(previous_account_info)
    return change_in_all_accounts

def sum_of_all_accounts(accounts):
    sum = 0
    for account in accounts:
        sum = sum + account.newest_amount
    return sum

def create_post_type_array(request):
    post_type_array = []
    i = 0
    for item in request.POST:
        idarray = item.split("__",1)
        if i == 0:
            i = i + 1
        elif i != 0:
            post_type_array.append(item.split("__",1)[1])
        i = i + 1
    return post_type_array


def create_array_from_form(request, post_type_array, description='Check-In adjustment'):
    new_array = []
    for item in post_type_array:
        input_amount = request.POST['addOrRemove__' + item]
        if input_amount == '':
            input_amount = 0
        new_array.append({
            'bucket_id': item,
            'amount': input_amount,
            'description': description,
        })
    return new_array

def create_account_status_array(request):
    account_status_array = []
    account_id_array = []
    i = 0
    for item in request.POST:
        idarray = item.split("__",1)
        if i == 0:
            i = i + 1
        elif str(idarray[1]) in account_id_array and i != 0:
            print('id already in account_id_array, do nothing')
        elif i != 0:
            account_id_array.append(item.split("__",1)[1])
        i = i + 1
    for item in account_id_array:
        account_status_array.append({
            'account_id': item,
            'date': request.POST['date__' + item],
            'amount': request.POST['amount__' + item],
            'description': 'Account value as of this date'
        })
    return account_status_array