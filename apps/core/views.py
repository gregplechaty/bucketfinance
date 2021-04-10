from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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
    print('------------view: dashboard, user:', request.user)
    buckets = Bucket.objects.filter(userID=request.user)
    print(buckets)
    #if readinglist.creator_user != request.user:
    #    raise SuspiciousOperation("Attempted to access different user's dashboard")
    context = {
        'user': request.user,
        'buckets': buckets,
    }

    return render(request, 'pages/dashboard.html', context)

@login_required
def create_bucket(request):
    print('------------view: manage_buckets, user:', request.user)
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request
        form = AddBucket(request.POST)
        if form.is_valid():
            # C in CRUD --- CREATE reading list in database
            bucket = form.save(commit=False)
            bucket.userID = request.user
            print('----printing user_id:', bucket.userID)
            bucket.save()
            
            return render(request, 'pages/dashboard.html')
    else:
        # if a GET  we'll create a blank form
        form = AddBucket()

    context = {
        'form': form,
    }
    return render(request, 'pages/form_page.html', context)

