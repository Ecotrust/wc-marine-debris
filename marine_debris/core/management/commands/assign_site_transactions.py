import os
from django.core.management.base import BaseCommand, CommandError
from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        sites = [x for x in Site.objects.filter(transaction=None)]
        print "%s sites found with no associated transaction." % sites.__len__()
        transactions = UserTransaction.objects.filter(status="accepted")
        if not sites == [] :
            if transactions.count() > 0:
                print "Assigning transaction id %s to sites" % transactions[0].id
                for site in sites:
                    site.transaction = transactions[0]
                    site.save()
            else:
                print "No accepted transactions exist. Please accept a transaction before running this command again."
        