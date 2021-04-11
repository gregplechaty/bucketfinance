import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import SuspiciousOperation
from apps.accounts.models import User
from apps.core.models import Bucket
from apps.core.forms import AddBucket

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
def dashboard(request, user_id):
    print('------------view: dashboard, user:', str(request.user.id))
    buckets = Bucket.objects.filter(userID=request.user, removedDate__isnull=True)
    #if readinglist.creator_user != request.user:
    #    raise SuspiciousOperation("Attempted to access different user's dashboard")
    context = {
        'user': request.user,
        'buckets': buckets,
    }

    return render(request, 'pages/dashboard.html', context)

@login_required
def create_bucket(request):
    print('------------view: create_bucket')
    if request.method == 'POST':
        form = AddBucket(request.POST)
        if form.is_valid():
            bucket = form.save(commit=False)
            bucket.userID = request.user
            bucket.save()
            #context = {
            #    'buckets': Bucket.objects.filter(userID=request.user),
            #    'user': request.user,
            #}
            return redirect('/dashboard/' + str(request.user.id))
    else:
        form = AddBucket()
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'pages/form_page.html', context)

@login_required
def edit_bucket(request, user_id, bucket_id):
    print('------------view: edit_bucket:', bucket_id)
    bucket_to_modify = Bucket.objects.get(id=bucket_id)
    Bucket.objects.filter(userID=request.user)
    if request.method == 'POST':
        form = AddBucket(request.POST, instance=bucket_to_modify)
        if form.is_valid():
            bucket_to_modify = form.save()
            return redirect('/dashboard/' + user_id)
    else:
        bucket_to_modify = Bucket.objects.get(id = bucket_id)
        form = AddBucket(instance=bucket_to_modify)
    context = {
        'form': form,
    }
    return render(request, 'pages/form_page.html', context)


@login_required
def delete_bucket(request, bucket_id):
    print('------------view: delete_bucket:', bucket_id)
    bucket_to_delete = Bucket.objects.get(id=bucket_id)
    if bucket_to_delete.userID != request.user:
        raise SuspiciousOperation("Attempted to delete different user's bucket")
    else:
        bucket_to_delete.removedDate = datetime.datetime.now()
        bucket_to_delete.save()
        return redirect('/dashboard/' + str(request.user.id))
    