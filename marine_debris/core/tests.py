"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry 
from core.models import DataSheet, Site, State, Event, Project
from pyquery import PyQuery as pq
import os
import datetime


class TestTransactionBulkUpload(TransactionTestCase):
    """
    Anything which causes an integrityError should go in here
    """
    fixtures = ['test_data',]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@madrona.org', password='pword')
        self.ds = DataSheet.objects.get(pk=18) 
        d = os.path.dirname(__file__)
        testdir = os.path.abspath(os.path.join(d, 'fixtures', 'testdata'))

        self.fpath = os.path.join(testdir, 'test_bulk.csv')
        self.fpath_events12 = os.path.join(testdir, 'test_bulk_events12.csv')
        self.fpath_events23 = os.path.join(testdir, 'test_bulk_events23.csv')
        self.fpath_notadup = os.path.join(testdir, 'test_derelict_not_actually_a_dup_event.csv')
        self.fpath_truedup = os.path.join(testdir, 'test_derelict_truedup_events.csv')

    def test_post(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        num_events = Event.objects.all().count()
        with open(self.fpath) as f:
            response = self.client.post(url, {
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'datasheet_id': self.ds.pk,
                'csvfile': f
                }
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.all().count(), num_events+3)
        # post again, should fail
        with open(self.fpath) as f:
            response = self.client.post(url, {
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'datasheet_id': self.ds.pk,
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 4, response.content) # 3 events that already exist plus a global error
        self.assertEqual(Event.objects.all().count(), num_events+3)

    def test_post_atomic(self):
        """
        Ensure that when bulk file with any existing events gets uploaded, NO events get committed (even the new ones)
        """
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        num_events = Event.objects.all().count()
        # post events 1 and 2
        with open(self.fpath_events12) as f:
            response = self.client.post(url, {
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'datasheet_id': self.ds.pk,
                'csvfile': f
                }
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.all().count(), num_events+2)
        # post again with events 2 and 3
        # should fail due to duplicate event 2 
        # nothing should be committed even though event 3 is new
        with open(self.fpath_events23) as f:
            response = self.client.post(url, {
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'datasheet_id': self.ds.pk,
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        # Expect 2 errors: "event 2 exists" AND "event 3 is new but not uploaded"
        self.assertEqual(len(el), 2) 
        self.assertIn("events were found but not loaded", el[0].text_content())
        self.assertIn("Duplicate Event", el[1].text_content())
        self.assertEqual(Event.objects.all().count(), num_events+2)

    def test_post_not_really_dups(self):
        """
        We might see a new row with the same lat/lon and date. 
        Is it truly NEW event that needs to be added (as looking for differing field values might indicate)
        """
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        num_events = Event.objects.all().count()
        with open(self.fpath_notadup) as f:
            response = self.client.post(url, {
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'datasheet_id': 19,
                'csvfile': f
                }
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.all().count(), num_events+3) # 3 new events

    def test_post_true_dups(self):
        """
        We might see a new row with the same lat/lon and date. 
        Is it really a duplicate (as the unique clause on the event model might indicate) OR
        """
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        num_events = Event.objects.all().count()
        with open(self.fpath_truedup) as f:
            response = self.client.post(url, {
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'datasheet_id': 19,
                'csvfile': f
                }
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Event.objects.all().count(), num_events)  # nothing added


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
        self.fpath_bad_state = os.path.join(testdir, 'test_bulk_bad_state.csv')
     
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

    def test_post_bad_date(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_date) as f:
            response = self.client.post(url, {
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'datasheet_id': self.ds.pk,
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 2, response.content)
        self.assertTrue("Enter a valid date" in el.html(), el.html())

    def test_post_bad_minmax(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_minmax) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 3)
        self.assertTrue("Ensure this value is greater than or equal to 0" in el[1].text_content())

    def test_post_bad_missing_cols(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_missing_cols) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 1)
        self.assertTrue("does not contain required column 'Created Date'" in el[0].text_content())

    def test_post_bad_extra_cols(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_extra_cols) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 1)
        self.assertTrue("contains column 'Extraneous Info' which is not recognized by this datasheet" in el[0].text_content())

    def test_post_bad_type(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_type) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 4)
        self.assertTrue( "Row 2, column 'Dump: Appliances'" in el[0].text_content(), response.content)
        self.assertTrue( "Enter a number" in el[3].text_content())

    def test_post_bad_csv(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_csv) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 1)
        self.assertTrue('Uploaded file does not contain any rows.' in el[0].text_content())

    def test_post_bad_site(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_site) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 1)
        self.assertTrue("TestSite3" in el[0].text_content(), el[0].text_content())
        self.assertTrue("is not in the database" in el[0].text_content(), el[0].text_content())

        # Now add the site
        ca = State.objects.get(name="California")
        testsite3 = Site(sitename="TestSite3", state=ca, county="Santa Cruz")
        testsite3.save()
        with open(self.fpath_bad_site) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(len(el), 0)

    def test_post_bad_state(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        with open(self.fpath_bad_state) as f:
            response = self.client.post(url, {
                'datasheet_id': self.ds.pk,
                'organization': 'Coast Savers', 
                'project_id': 1, 
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(len(el), 3)
        self.assertTrue('state' in el[0].text_content())
        self.assertTrue('State' in el[1].text_content())


class TestBulkCoordBased(TestCase):
    fixtures = ['test_data',]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@madrona.org', password='pword')
        self.ds = DataSheet.objects.get(pk=19) # northwest straights
        d = os.path.dirname(__file__)
        testdir = os.path.abspath(os.path.join(d, 'fixtures', 'testdata'))

        self.fpath = os.path.join(testdir, 'test_bulk_derelict.csv')
     
    def test_derelict_post(self):
        self.client.login(username='featuretest', password='pword')
        url = '/datasheet/bulk_import/'
        num_events = Event.objects.all().count()
        num_sites = Site.objects.all().count()
        with open(self.fpath) as f:
            response = self.client.post(url, {
                'organization': 'Northwest Straights', 
                'project_id': 1, 
                'datasheet_id': self.ds.pk,
                'csvfile': f
                }
            )
        d = pq(response.content)
        el = d("ul.errorlist li")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(len(el), 0)
        # should have 3 new events at 2 new sites
        self.assertEqual(Event.objects.all().count(), num_events+3)
        self.assertEqual(Site.objects.all().count(), num_sites+2)

class TestCounty(TestCase):
    fixtures = ['test_data', 'counties']

    def test_counties(self):
        pnt = GEOSGeometry('SRID=4326;POINT(-122 44)')
        s = Site(geometry = pnt)
        s.save()
        self.assertEqual(s.state.initials, 'OR')
        self.assertEqual(s.county, 'Lane')

    def test_offshore(self):
        pnt = GEOSGeometry('SRID=4326;POINT(-125 44)')
        s = Site(geometry = pnt)
        s.save()
        self.assertEqual(s.state.initials, 'OR')
        self.assertEqual(s.county, 'Lane')

    def test_way_offshore(self):
        pnt = GEOSGeometry('SRID=4326;POINT(-127 44)')
        s = Site(geometry = pnt)
        s.save()
        self.assertEqual(s.state, None)
        self.assertEqual(s.county, None)

    def test_edge_case(self):
        pnt = GEOSGeometry('SRID=4326;POINT(-124.014723 45.045150)')
        s = Site(geometry = pnt)
        s.save()
        self.assertEqual(s.state.initials, 'OR')
        self.assertEqual(s.county, 'Tillamook')

    def test_presave(self):
        pnt = GEOSGeometry('SRID=4326;POINT(-124.014723 45.045150)')
        site = Site(sitename="TestSite3", geometry=pnt)
        self.assertEqual(site.state, None)
        self.assertEqual(site.county, None)
        site.save()
        self.assertEqual(site.state.initials, "OR")
        self.assertEqual(site.county, "Tillamook")
