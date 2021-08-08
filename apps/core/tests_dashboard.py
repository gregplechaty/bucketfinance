from django.db.models.fields import NullBooleanField
import requests
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from http import HTTPStatus
from django.utils import timezone
from apps.accounts.models import User
from apps.core.models import Bucket, Transaction, BankAccount, BankAccountStatus
from apps.core.forms import AddBucket, AddTransaction
from apps.core.views.shared import get_buckets_transactions

class GetBucketsTransactionsTestCase(TestCase):
    #Tests get_buckets_transactions function
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.client.login(username='jacob', password='top_secret')
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Emergency Fund", "bucketDescription": "Emergency Fund"}
        )
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Slush Fund", "bucketDescription": "extra funds to cover day-to-day expenses"}
        )
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Wedding Fund", "bucketDescription": "One-time fund. This will be deleted for this test."}
        )
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Fun Money", "bucketDescription": "No justification needed!"}
        )
        responseTwo = self.client.post(
            "/dashboard/transaction/1/", follow=True, data={"amount": "5000", "transactionDate": "01/01/2021", "description": "baseline emergency fund", "transaction_type": "add"}
        )
        responseTwo = self.client.post(
            "/dashboard/transaction/2/", follow=True, data={"amount": "1000", "transactionDate": "02/03/2021", "description": "baseline slush", "transaction_type": "add"}
        )
        responseTwo = self.client.post(
            "/dashboard/transaction/3/", follow=True, data={"amount": "30000", "transactionDate": "03/04/2021", "description": "baseline wedding", "transaction_type": "add"}
        )
        responseTwo = self.client.post(
            "/dashboard/transaction/4/", follow=True, data={"amount": "400", "transactionDate": "04/21/2021", "description": "baseline fun money", "transaction_type": "add"}
        )
        responseTwo = self.client.post(
            "/dashboard/transaction/3/", follow=True, data={"amount": "26000", "transactionDate": "05/15/2021", "description": "wedding expense", "transaction_type": "subtract"}
        )

    def test_setup(self):
        self.assertEqual(Bucket.objects.count(),4)
        self.assertEqual(Transaction.objects.count(),5)

    def test_bucket_sums(self):
        # Create an instance of a GET request.
        request = self.factory.get('/dashboard/')
        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        request.user = self.user
        # Test my_view() as if it were deployed at /customer/details
        buckets, transactions, buckets_with_sum = get_buckets_transactions(request)
        bucket_emergency_fund = None
        bucket_wedding_fund = None
        for bucket in buckets_with_sum:
            #print(bucket, bucket.bucketName, ':', bucket.total_amount, bucket.id)
            if bucket.id == 1:
                bucket_emergency_fund = bucket
            elif bucket.id == 3:
                bucket_wedding_fund = bucket

        #bucket_emergency_fund = buckets_with_sum.get(id__exact=1)
        self.assertEqual(bucket_emergency_fund.total_amount,5000.00)
        self.assertEqual(bucket_wedding_fund.total_amount,4000.00)
  

class DeleteBucketReallocateFundsTestCase(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.client.login(username='jacob', password='top_secret')
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Emergency Fund", "bucketDescription": "Emergency Fund"}
        )
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Slush Fund", "bucketDescription": "extra funds to cover day-to-day expenses"}
        )
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Wedding Fund", "bucketDescription": "One-time fund. This will be deleted for this test."}
        )
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Fun Money", "bucketDescription": "No justification needed!"}
        )
        responseTwo = self.client.post(
            "/dashboard/transaction/1/", follow=True, data={"amount": "5000", "transactionDate": "01/01/2021", "description": "baseline emergency fund", "transaction_type": "add"}
        )
        responseTwo = self.client.post(
            "/dashboard/transaction/2/", follow=True, data={"amount": "1000", "transactionDate": "02/03/2021", "description": "baseline slush", "transaction_type": "add"}
        )
        responseTwo = self.client.post(
            "/dashboard/transaction/3/", follow=True, data={"amount": "30000", "transactionDate": "03/04/2021", "description": "baseline wedding", "transaction_type": "add"}
        )
        responseTwo = self.client.post(
            "/dashboard/transaction/4/", follow=True, data={"amount": "400", "transactionDate": "04/21/2021", "description": "baseline fun money", "transaction_type": "add"}
        )
        responseTwo = self.client.post(
            "/dashboard/transaction/3/", follow=True, data={"amount": "26000", "transactionDate": "05/15/2021", "description": "wedding expense", "transaction_type": "subtract"}
        )

    def test_setup(self):
        self.assertEqual(Bucket.objects.count(),4)
        self.assertEqual(Transaction.objects.count(),5)

    def test_delete_bucket_allocate_funds(self):
        response = self.client.post(
            "/dashboard/buckets/delete/3/", follow=True, data={'csrfmiddlewaretoken': ['TESTCONTENT123456'],   "addOrRemove__1": "1000.00", "addOrRemove__2": "500.00", "addOrRemove__4": "2500.00",}
        )
        request = self.factory.get('/dashboard/')
        request.user = self.user
        buckets, transactions, buckets_with_sum = get_buckets_transactions(request)
        bucket_emergency_fund = None
        bucket_slush_fund = None
        bucket_fun_money = None
        for bucket in buckets_with_sum:
            if bucket.id == 1:
                bucket_emergency_fund = bucket
            elif bucket.id == 2:
                bucket_slush_fund = bucket
            elif bucket.id == 4:
                bucket_fun_money = bucket
        self.assertEqual(bucket_emergency_fund.total_amount,6000.00)
        self.assertEqual(bucket_slush_fund.total_amount,1500.00)
        self.assertEqual(bucket_fun_money.total_amount,2900.00)
