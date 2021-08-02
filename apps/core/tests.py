import requests
from django.test import TestCase, Client
from django.contrib.auth.models import User
from http import HTTPStatus
from apps.accounts.models import User
from apps.core.models import Bucket, Transaction
from apps.core.forms import AddBucket, AddTransaction

class BucketModuleUnitTestCase(TestCase):
    def setUp(self):
        #fake_user = User.objects.create(username='test_user')
        #fake_user.set_password('1234')
        #fake_user.save()
        fake_user = User.objects.create_user('test_user', 'testemail@testemail.com', '1234')

    

    def test_Bucket_creation(self):
        self.assertEqual(Bucket.objects.count(),0)
        self.client.login(username='test_user', password='1234')
     
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Test Bucket 1", "bucketDescription": "Test description 1"}
        )
        
        #open('_test.html', 'wb+').write(response.content)
        self.assertEqual(Bucket.objects.count(),1)
    


class TransactionModuleUnitTestCase(TestCase):
    def setUp(self):
        #fake_user = User.objects.create(username='test_user')
        #fake_user.set_password('1234')
        #fake_user.save()
        fake_user = User.objects.create_user('test_user', 'testemail@testemail.com', '1234')
        self.client.login(username='test_user', password='1234')
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Test Bucket 1", "bucketDescription": "Test description 1"}
        )

    def test_Transaction_creation(self):
        responseTwo = self.client.post(
            "dashboard/transaction/1", follow=True, data={"amount": "6500", "transactionDate": "08/01/2021", "description": "Testing my really expensive purchase", "transaction_type": "subtract"}
        )
        open('_test.html', 'wb+').write(responseTwo.content)
        self.assertEqual(Transaction.objects.count(),1)
    