import os
from django.conf import settings

class DiskUsageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        usage = self.get_disk_usage()
        request.disk_usage_exceeded = usage > 10 * 1024 * 1024 * 1024  # 10GB threshold
        return self.get_response(request)

    def get_disk_usage(self):
        total_size = 0
        for dirpath, _, filenames in os.walk(settings.MEDIA_ROOT):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
        return total_size

