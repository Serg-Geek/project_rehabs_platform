from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from django.core.files.base import File
from django.core.files.uploadedfile import UploadedFile

class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, (File, UploadedFile)):
            # Обрабатываем ImageFieldFile и другие файловые объекты
            if hasattr(obj, 'name') and obj.name:
                return obj.name
            elif hasattr(obj, 'url'):
                return obj.url
            else:
                return str(obj)
        return super().default(obj) 