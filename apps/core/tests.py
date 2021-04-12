from django.test import TestCase

from apps.accounts.models import User
from apps.core.models import Bucket
from apps.core.forms import AddBucket

class BucketModuleUnitTestCase(TestCase):
    def setUp(self):
        fake_user = User.objects.create(username='test_user')
        fake_user.set_password('1234')
        fake_user.save()
        self.bucket = Bucket.objects.create(
            bucketName = 'Test Bucket 1',
            bucketDescription = 'Test Bucket Description 1',
            userID = fake_user
        )
        self.bucket = Bucket.objects.create(
            bucketName = 'Test Bucket 2',
            bucketDescription = 'Test Bucket Description 2',
            userID = fake_user
        )
        self.bucket = Bucket.objects.create(
            bucketName = 'Test Bucket 3',
            bucketDescription = 'Test Bucket Description 3',
            userID = fake_user
        )
        #self.client.login(username='test_user', password='1234')
        print('setup complete')
        self.assertEqual(Bucket.objects.count(), 3) 
    
    def test_increment_views(self):
        self.client.login(username='test_user', password='1234')
        fake_user = User.objects.get(id=1)
        #response = self.client.get('/dashboard/%i' % fake_user.id)
        response = self.client.get('/dashboard/1')
        print(response)
        self.assertEqual(Bucket.objects.count(), 3)
        self.assertContains(response, 'Dashboard')