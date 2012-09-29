"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from core.models import DataSheet, Site, State
from pyquery import PyQuery as pq
import os


class TestBulkUpload(TestCase):
    fixtures = ['test_data',]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@madrona.org', password='pword')
        self.ds = DataSheet.objects.get(pk=18) 
        d = os.path.dirname(__file__)
        testdir = os.path.abspath(os.path.join(d, 'fixtures', 'testdata'))

        self.fpath = os.path.join(testdir, 'test_bulk.csv')
        self.fpath_bad_date = os.path.join(testdir, 'test_bulk_bad_date.csv')
        self.fpath_bad_minmax = os.path.join(testdir, 'test_bulk_bad_minmax.csv')
        self.fpath_bad_missing_cols = os.path.join(testdir, 'test_bulk_bad_missing_cols.csv')
        self.fpath_bad_extra_cols = os.path.join(testdir, 'test_bulk_bad_extra_cols.csv')
        self.fpath_bad_type = os.path.join(testdir, 'test_bulk_bad_type.csv')
        self.fpath_bad_csv = os.path.join(testdir, 'test_bulk_bad_csv.csv')
        self.fpath_bad_site = os.path.join(testdir, 'test_bulk_bad_site.csv')
     
    def test_bulk_csv_header(self):
        response = self.client.get('/datasheet/csv_header/%d' % self.ds.pk)
        self.assertEqual(response.status_code, 200)

    def test_unauth(self):
        response = self.client.post('/datasheet/bulk_import/')
        self.assertEqual(response.status_code, 302) #login required

    def test_get(self):
        self.client.login(username='featuretest', password='pword')
        response = self.client.get('/datasheet/bulk_import/')
        self.assertEqual(response.status_code, 200)

    def test_post_no_datasheetid(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath) as f:
            response = self.client.post(url, { 'csvfile': f }) # no datasheet_id
        self.assertEqual(response.status_code, 400)

    def test_post(self):
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

    def test_post_bad_date(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_date) as f:
            response = self.client.post(url, {
                'organization': 'Coast Savers', 
                'project': 'Beach Cleanups', 
                'data_sheet': 'Coast Savers Cleanup Data', 
                'datasheet_id': self.ds.pk,
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 1)
        self.assertTrue("Enter a valid date/time" in el.html(), el.html())

    def test_post_bad_minmax(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_minmax) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project': 'Beach Cleanups', 
                'data_sheet': 'Coast Savers Cleanup Data', 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 3)
        self.assertTrue("Ensure this value is greater than or equal to 0" in el[1].text)

    def test_post_bad_missing_cols(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_missing_cols) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project': 'Beach Cleanups', 
                'data_sheet': 'Coast Savers Cleanup Data', 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 1)
        self.assertTrue("does not contain required column 'Created Date'" in el[0].text)

    def test_post_bad_extra_cols(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_extra_cols) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project': 'Beach Cleanups', 
                'data_sheet': 'Coast Savers Cleanup Data', 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 1)
        self.assertTrue("contains column 'Extraneous Info' which is not recognized by this datasheet" in el[0].text)

    def test_post_bad_type(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_type) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project': 'Beach Cleanups', 
                'data_sheet': 'Coast Savers Cleanup Data', 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 4)
        self.assertTrue( "Row 1, 'Dump: Appliances' is invalid: * Enter a number." in el[0].text)
        self.assertTrue( "Row 2, 'Dump: 55-Gal. Drums' is invalid: * Enter a number." in el[3].text)

    def test_post_bad_csv(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_csv) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project': 'Beach Cleanups', 
                'data_sheet': 'Coast Savers Cleanup Data', 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 1)
        self.assertTrue('Uploaded file does not contain any rows.' in el[0].text)

    def test_post_bad_site(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_site) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project': 'Beach Cleanups', 
                'data_sheet': 'Coast Savers Cleanup Data', 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 1)
        self.assertTrue("Site 'TestSite3' is not in the database" in el[0].text, el[0].text)
        # Now add the site
        ca = State.objects.get(name="California")
        testsite3 = Site(sitename="TestSite3", state=ca, county="Santa Cruz")
        testsite3.save()
        with open(self.fpath_bad_site) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project': 'Beach Cleanups', 
                'data_sheet': 'Coast Savers Cleanup Data', 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(len(el), 0)

