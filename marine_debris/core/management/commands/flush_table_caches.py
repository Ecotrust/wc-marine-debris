from django.core.management.base import BaseCommand
import johnny.cache
from core.models import EventOntology

class Command(BaseCommand):
    """Call to reset caches on any tables that are modified outside of django.
    """
    def handle(self, *args, **options):
        johnny.cache.invalidate(EventOntology)
