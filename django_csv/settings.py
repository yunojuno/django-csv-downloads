from django.conf import settings

# Cap on the number of rows that can be downloaded
MAX_ROWS = getattr(settings, "CSV_DOWNLOAD_MAX_ROWS", 10000)

# Default page size used by PagedQuerySetWriter
DEFAULT_PAGE_SIZE = getattr(settings, "CSV_DOWNLOAD_PAGE_SIZE", 10000)
