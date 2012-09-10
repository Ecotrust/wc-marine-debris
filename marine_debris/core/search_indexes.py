import datetime
from haystack import indexes
from core.models import FieldValue


class FieldValueIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # author = indexes.CharField(model_attr='user')
    date_created = indexes.DateTimeField(model_attr='creation_date')

    def get_model(self):
        return FieldValue

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())