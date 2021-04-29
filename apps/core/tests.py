import requests
from django.test import TestCase, Client
from django.contrib.auth.models import User
from http import HTTPStatus
from apps.accounts.models import User
from apps.core.models import Bucket
from apps.core.forms import AddBucket

class BucketModuleUnitTestCase(TestCase):
    def setUp(self):
        fake_user = User.objects.create(username='test_user')
        fake_user.set_password('1234')
        fake_user.save()
        
        user_count = User.objects.count()
        self.assertEqual(user_count, 1)
        print('setup complete')
        #self.assertEqual(Bucket.objects.count(), 3) 

    

    def test_Bucket_creation(self):
        self.assertEqual(Bucket.objects.count(),0)
        #self.client.login(username='test_user', password='1234')
        c = Client()
        cat = c.login(username='test_user', password='1234')
        response = c.get('/dashboard/')
        print('------dashboard view:', response)
        self.assertContains(response, 'Create Bucket')
        print('OK, trying to create a bucket...')
        #form = AddBucket(data={"bucketName": "Test Bucket 1", "bucketDescription": "Test description 1"})
        
        self.client.post(
            "/dashboard/buckets/", data={"bucketName": "Test Bucket 1", "bucketDescription": "Test description 1"}
        )
        #print('--------testing response out here:', response)
        #self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Bucket.objects.count(),1)