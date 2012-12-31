import os
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from core.models import *
from pytz import timezone
import pytz

class Command(BaseCommand):
            
    def handle(self, *args, **options):
        pacific = timezone('US/Pacific')
        for media in Media.objects.all():
            media.published = media.published.astimezone(pacific)
            media.save()
        
        for transaction in UserTransaction.objects.all():
            transaction.created_date = transaction.created_date.astimezone(pacific)
            transaction.save()
            