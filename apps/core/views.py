import datetime
import requests
import pygal
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import SuspiciousOperation

from apps.accounts.models import User
from apps.core.models import Bucket, Transaction
from apps.core.forms import AddBucket, AddTransaction


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
    #dict_transactions_sums = bucket_amount_sum(request, buckets, transactions)
    joined_Transaction_Bucket = bucket_transaction_join(request)
    context = {
        'user': request.user,
        'buckets': buckets,
        'transactions': transactions,
        'table': joined_Transaction_Bucket
        #'dict_transactions_sums': dict_transactions_sums,
    }
    return render(request, 'pages/dashboard.html', context)


def bucket_transaction_join(request):
    joined_table = Transaction.objects.select_related('bucket')
    filtered_joined_table = joined_table.filter(user=request.user, removedDate__isnull=True)
    return(filtered_joined_table)


def bucket_amount_sum(request, buckets, transactions):
    dict_transactions_sums = {}
    for bucket in buckets:
        bucket_transactions = transactions.filter(bucket=bucket)
        if len(bucket_transactions) > 0:
            temp_dict = bucket_transactions.aggregate(Sum('amount'))
            dict_transactions_sums[bucket.id] = temp_dict['amount__sum']
        else:
            dict_transactions_sums[bucket.id] = 0
    return(dict_transactions_sums)

    


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
            return redirect('/dashboard')
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
            transaction_to_modify = form.save()
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