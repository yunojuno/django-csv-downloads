from django.contrib import admin

from .models import CsvDownload


class CsvDownloadAdmin(admin.ModelAdmin):
    list_display = ("user", "timestamp", "row_count", "filename")
    list_filter = ("timestamp",)
    search_fields = ("user", "filename")
    raw_id_fields = ("user",)
    readonly_fields = (
        "user",
        "timestamp",
        "filename",
        "row_count",
        "columns",
    )


admin.site.register(CsvDownload, CsvDownloadAdmin)
