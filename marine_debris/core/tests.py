"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from core.models import DataSheet
import os


class TestBulkUpload(TestCase):
    fixtures = ['test_data',]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@madrona.org', password='pword')
        self.ds = DataSheet.objects.get(pk=18) 
        d = os.path.dirname(__file__)
        self.fpath = os.path.abspath(os.path.join(d, 'fixtures', 'testdata', 'test_bulk.csv'))
        self.fpath_invalid = os.path.abspath(os.path.join(d, 'fixtures', 'testdata', 'test_bulk_invalid.csv'))
     
    def test_bulk_csv_header(self):
        response = self.client.get('/datasheet/csv_header/%d' % self.ds.pk)
        self.assertEqual(response.status_code, 200)

    def test_bulk_import_unauth(self):
        response = self.client.post('/datasheet/bulk_import/')
        self.assertEqual(response.status_code, 302) #login required

    def test_bulk_import_get(self):
        self.client.login(username='featuretest', password='pword')
        response = self.client.get('/datasheet/bulk_import/')
        self.assertEqual(response.status_code, 200)

    def test_bulk_import_post_no_datasheetid(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath) as f:
            response = self.client.post(url, { 'csvfile': f }) # no datasheet_id
        self.assertEqual(response.status_code, 400)

    def test_bulk_import_post(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath) as f:
            response = self.client.post(url, {
                'organization': 'Coast Savers', 
                'project': 'Beach Cleanups', 
                'data_sheet': 'Coast Savers Cleanup Data', 
                'datasheet_id': self.ds.pk,
                'csvfile': f
                }
            )
        self.assertEqual(response.status_code, 200)

    def test_bulk_import_post_validation_error(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_invalid) as f:
            response = self.client.post(url, {
                'organization': 'Coast Savers', 
                'project': 'Beach Cleanups', 
                'data_sheet': 'Coast Savers Cleanup Data', 
                'datasheet_id': self.ds.pk,
                'csvfile': f
                }
            )
        self.assertEqual(response.status_code, 400, response.content)
