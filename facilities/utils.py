from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime

class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj) 