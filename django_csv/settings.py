from django.conf import settings

# Cap on the number of rows that can be downloaded
MAX_ROWS = getattr(settings, "CSV_DOWNLOAD_MAX_ROWS", 10000)
