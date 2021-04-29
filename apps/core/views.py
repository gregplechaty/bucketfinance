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
from apps.core.forms import AddBucket, AddTransaction, AddBankAccount


def home(request):
    context = {
        'example_context_variable': 'Change me.',
        'user': request.user,
    }
    return render(request, 'pages/home.html', context)

def about(request):
    context = {
        'user': request.user,
    }
    return render(request, 'pages/about.html', context)

@login_required
def dashboard(request):
    buckets = Bucket.objects.filter(user=request.user, removedDate__isnull=True)
    transactions = Transaction.objects.filter(user=request.user, removedDate__isnull=True).order_by('-transactionDate')
    buckets_with_sum = bucket_amount_sum(buckets)
    context = {
        'user': request.user,
        'transactions': transactions,
        'buckets_with_sum': buckets_with_sum,
    }
    return render(request, 'pages/dashboard.html', context)

def bucket_amount_sum(buckets):
    dict_transactions_sums = {}
    #TODO: filter out removed transactions
    all_transactions_for_these_buckets = Transaction.objects.filter(bucket__in=buckets)
    for transaction in all_transactions_for_these_buckets:
        if transaction.bucket_id not in dict_transactions_sums:
            dict_transactions_sums[transaction.bucket_id] = 0
        dict_transactions_sums[transaction.bucket_id] += transaction.amount
    for bucket in buckets:
            if bucket.id in dict_transactions_sums:
                bucket.total_amount = dict_transactions_sums[bucket.id]
            else:
                bucket.total_amount = 0
    return buckets

@login_required
def create_bucket(request):
    if request.method == 'POST':
        form = AddBucket(request.POST)
        print('Here is the request post:', request.POST)
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
            last_action = 'indeed'
            return redirect(dashboard, last_action='yup')
    else:
        form = AddBucket(instance=bucket_to_modify)
    context = {
        'form': form,
    }
    return render(request, 'pages/form_page.html', context)

@login_required
def delete_bucket(request, bucket_id):
    print('------------view: delete_bucket:', bucket_id)
    bucket_to_delete = Bucket.objects.get(id=bucket_id)
    if bucket_to_delete.user != request.user:
        raise SuspiciousOperation("Attempted to delete different user's bucket")
    else:
        bucket_to_delete.removedDate = datetime.datetime.now()
        bucket_to_delete.save()
        return redirect('/dashboard')


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
            return redirect('/dashboard')
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
    print('------------view: delete_bucket:', transaction_id)
    transaction_to_delete = Transaction.objects.get(id=transaction_id)
    if transaction_to_delete.user != request.user:
        raise SuspiciousOperation("Attempted to delete different user's transaction")
    else:
        transaction_to_delete.removedDate = datetime.datetime.now()
        transaction_to_delete.save()
        return redirect('/dashboard')


@login_required
def monthly_check_in_1(request):
    print('------------view: monthly_check_in_1:')
    context = {
        'user': request.user,
    }
    return render(request, 'pages/month_check_in_1.html', context)


def get_bank_account_info(request):
    # Getting user's bank accounts
    accounts = BankAccount.objects.filter(user=request.user, removed_date__isnull=True)
    all_statuses_for_these_accounts = BankAccountStatus.objects.filter(bank_account__in=accounts).order_by('-status_date')
    bank_account_last_check_in_date = {}
    for account in accounts:
        print('-------in accounts loop')
        #account_status = BankAccountStatus.objects.filter(bank_account=account, removed_date__isnull=True).order_by('status_date')[:1]
        if len(all_statuses_for_these_accounts) == 0:
            #bank_account_last_check_in_date[account.pk] = 'None. Start your first check-in below by clicking "Continue!"'
            account.last_check_in_date = 'None. Start your first check-in below by clicking "Continue!"'
        else:
            #bank_account_last_check_in_date[account.pk] = account_status.status_date
            account.last_check_in_date = account_status.status_date
    print('array for bank_account_last_check_in_date', bank_account_last_check_in_date)
    return accounts


@login_required
def monthly_check_in_2(request):
    print('------------view: monthly_check_in_2:')
    if request.method == 'POST':
        print('I need to work on this...')
    accounts = get_bank_account_info(request)
    context = {
        'user': request.user,
        'accounts': accounts,
    }
    return render(request, 'pages/month_check_in_2.html', context)



@login_required
def create_account(request):
    if request.method == 'POST':
        form = AddBankAccount(request.POST)
        print('Here is the request post:', request.POST)
        if form.is_valid():
            bucket = form.save(commit=False)
            bucket.user = request.user
            bucket.save()
            return redirect(monthly_check_in_2)
    else:
        form = AddBankAccount()
    context = {
        'form': form,
    }
    return render(request, 'pages/form_page.html', context)



#FLOW OF THE MONTHLY Check-in

#1. Give opportunity to record any one-off expenses from previous months. maybe redirect to
#homepage for now


#2. Ask user for:
# ---bank account (possibility for multiple accounts???) balance
# ---option to create new bank account
# ---Date of check-in
### might need to create a new model: Bank Balance (userID, Date, progress/stepID, bank account name,
### bank balance, maybe a link to the transactions table; create/saved/removed date)
### might need to add a new column to the

#3. Calculate the difference between last amount and new amount.

#4. Allocate (or withdraw) funds from buckets. Should be done on a single page.



def stock_info(request):
    if 'stock_symbol' in request.GET and request.GET['stock_symbol']:
        stock_symbol = request.GET['stock_symbol']
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + stock_symbol + '&apikey=AYGLUKRBOXGJSVWO'
        response = requests.get(url)
        stock_data = response.json()
        x_values, y_values = stock_chart_value_generation(stock_data)
        chart = stock_chart_generation(stock_symbol, x_values, y_values)
        context = {
            'chart': chart,
        }
        return render(request, 'pages/stock_info.html', context)
    
    return render(request, 'pages/stock_info.html')

def stock_chart_value_generation(dataset):
    print('-------view: stock_chart_generation')
    x_values = ['2021-04-12', '2021-04-09', '2021-04-08', '2021-04-07', '2021-04-06']
    y_values = []
    for item in x_values:
        y_values.append(float(dataset['Time Series (Daily)'][item]['4. close']))
        x_values.reverse()
        y_values.reverse()
    return x_values, y_values

def stock_chart_generation(stock_symbol, x_values, y_values):
    line_chart = pygal.Line(x_label_rotation=70)
    line_chart.title = 'Recent Stock Closing prices for ' + stock_symbol.upper()
    line_chart.x_labels = map(str, x_values)
    line_chart.add(stock_symbol.upper(), y_values)
    stat_line_chart = line_chart.render_data_uri()
    return stat_line_chart