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

#################### VIEWS ####################

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

############################# HELPER FUNCTIONS #############################

def get_buckets_transactions(request):
    buckets = Bucket.objects.filter(user=request.user, removedDate__isnull=True)
    transactions = Transaction.objects.filter(user=request.user, removedDate__isnull=True).order_by('-transactionDate')
    buckets_with_sum = bucket_amount_sum(buckets)
    return buckets, transactions, buckets_with_sum

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
def get_account_data(request):
    accounts = BankAccount.objects.filter(user=request.user, removed_date__isnull=True)
    accounts_statuses = BankAccountStatus.objects.filter(bank_account__in=accounts, removed_date__isnull=True).order_by('-status_date')
    for account in accounts:
        account.current_balance = accounts_statuses.filter(bank_account=account, removed_date__isnull=True).order_by('-status_date')[0].amount
    return accounts, accounts_statuses

############################# STOCK INFO WIP #############################

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