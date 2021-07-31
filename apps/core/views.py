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

def get_buckets_transactions(request):
    buckets = Bucket.objects.filter(user=request.user, removedDate__isnull=True)
    transactions = Transaction.objects.filter(user=request.user, removedDate__isnull=True).order_by('-transactionDate')
    buckets_with_sum = bucket_amount_sum(buckets)
    return buckets, transactions, buckets_with_sum

@login_required
def dashboard(request):
    buckets, transactions, buckets_with_sum = get_buckets_transactions(request)
    context = {
        'user': request.user,
        'transactions': transactions,
        'buckets_with_sum': buckets_with_sum,
    }
    return render(request, 'pages/dashboard.html', context)

def bucket_amount_sum(buckets):
    dict_transactions_sums = {}
    all_transactions_for_these_buckets = Transaction.objects.filter(bucket__in=buckets, removedDate__isnull=True)
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
            return redirect(dashboard)
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
    print('################', accounts)
    all_statuses_for_these_accounts = BankAccountStatus.objects.filter(bank_account__in=accounts).order_by('-status_date')
    #print('################', all_statuses_for_these_accounts)
    bank_account_last_check_in_date = {}
    ## Here we add last status check-in to the account info
    for account in accounts:
        print('-------in accounts loop')
        account_status = BankAccountStatus.objects.filter(bank_account=account, removed_date__isnull=True).order_by('status_date')[:1]
        #print('****************account status:', account, account_status)
        if len(all_statuses_for_these_accounts) == 0:
            account.last_check_in_date = 'None. Start your first check-in below by clicking "Continue!"'
        else:
            account.last_check_in_date = account_status[0].status_date
            account.last_amount = account_status[0].amount
            print('LAST_AMOUNT:', account_status[0].amount)
    #print('array for bank_account_last_check_in_date', bank_account_last_check_in_date)
    return accounts



@login_required
def monthly_check_in_2(request):
    print('------------view: monthly_check_in_2:')
    if request.method == 'POST':
        print('Working on Check-In-POST...')
        print("-----here's the post request:", request.POST)
        account_status_array = create_account_status_array(request)
        save_account_status(account_status_array)
        return redirect('pages/month_check_in_3.html')
    accounts = get_bank_account_info(request)
    context = {
        'user': request.user,
        'accounts': accounts,
    }
    return render(request, 'pages/month_check_in_2.html', context)


def tryMyLogic(request):
    accounts = get_bank_account_info(request)
    print('account:', accounts)



@login_required
def monthly_check_in_3(request):
    print('------------view: monthly_check_in_3:')
    if request.method == 'POST':
        print("-----here's the post request:", request.POST)
        return redirect('/dashboard')
    accounts = get_bank_account_info(request)
    tryMyLogic(request)
    context = {
        'user': request.user,
        'accounts': accounts, 
    }
    return render(request, 'pages/month_check_in_3.html', context)

#@login_required
#def monthly_check_in_3(request):
#    print('------------view: monthly_check_in_3:')
#    buckets, transactions, buckets_with_sum = get_buckets_transactions(request)
#    accounts = get_bank_account_info(request)
#    context = {
#       'user': request.user,
#        'accounts': accounts,
#    }
#    return render(request, 'pages/month_check_in_2.html', context)





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
            'amount': request.POST['amount__' + item]
        })
    return account_status_array

def save_account_status(account_status_array):
    for account in account_status_array:
            new_bank_account_status = AddBankAccountStatus()
            account_status = new_bank_account_status.save(commit=False)
            account_status.amount = account["amount"]
            account_status.status_date = account["date"]
            account_status.description = 'hardcoded description text. You have no control!'
            current_bank_account = BankAccount.objects.get(id=int(account["account_id"]))
            account_status.bank_account = current_bank_account
            print('account status:', account_status)
            account_status.save()
            print('Save of account status successful!')

@login_required
def create_account(request):
    if request.method == 'POST':
        form = AddBankAccount(request.POST)
        #print('Here is the request post:', request.POST)
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