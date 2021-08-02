import requests
from django.test import TestCase, Client
from django.contrib.auth.models import User
from http import HTTPStatus
from apps.accounts.models import User
from apps.core.models import Bucket, Transaction, BankAccount
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
    

class DashboardPageTestCase(TestCase):
    def setUp(self):
        fake_user = User.objects.create_user('test_user', 'testemail@testemail.com', '1234')
        self.client.login(username='test_user', password='1234')
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Test Bucket 1", "bucketDescription": "Test description 1"}
        )

    def test_dashboard_page(self):
        response = self.client.get('/dashboard/')
        self.assertContains(response, 'Hello')
        self.assertContains(response, 'Create Bucket')
        self.assertContains(response, 'Add or Remove Funds')  

class TransactionModuleUnitTestCase(TestCase):
    def setUp(self):
        fake_user = User.objects.create_user('test_user', 'testemail@testemail.com', '1234')
        self.client.login(username='test_user', password='1234')
        response = self.client.post(
            "/dashboard/buckets", follow=True, data={"bucketName": "Test Bucket 1", "bucketDescription": "Test description 1"}
        )

    def test_add_transaction_page(self):
        response = self.client.get('/dashboard/transaction/1/')
        self.assertContains(response, 'Save')

    def test_Transaction_creation(self):
        responseTwo = self.client.post(
            "/dashboard/transaction/1/", follow=True, data={"amount": "6500", "transactionDate": "08/01/2021", "description": "Testing my really expensive purchase", "transaction_type": "subtract"}
        )
        #open('_test.html', 'wb+').write(responseTwo.content)
        self.assertEqual(Transaction.objects.count(),1)

class BankAccountModuleTestCase(TestCase):
    def setUp(self):
        fake_user = User.objects.create_user('test_user', 'testemail@testemail.com', '1234')
        self.client.login(username='test_user', password='1234')

    def test_create_bank_account_page(self):
        response = self.client.get('/dashboard/check-in/account')
        self.assertContains(response, 'Save')
        self.assertContains(response, 'AccountName')


    def test_Transaction_creation(self):
        responseTwo = self.client.post(
            "/dashboard/check-in/account", follow=True, data={"accountName": "Gringotts Wizarding Bank", "description": "An arcane, underground vault guarded by a dragon. Only opened by authorized goblins.",}
        )
        open('_test.html', 'wb+').write(responseTwo.content)
        self.assertEqual(BankAccount.objects.count(),1)
        self.assertContains(responseTwo, 'Gringotts Wizarding Bank')