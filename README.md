# Django CSV Downloads

Django app for tracking queryset-backed CSV downloads

### Version support

The current version of the this app support **Python 3.8+** and **Django 2.2+**

## What does this app do?

This app is used to track user downloads of CSVs that are derived from Django QuerySets. You provide
the filename, queryset and the list of columns that you want to output.

It has a single model (`CsvDownload`) that tracks downloads and stores the user, filename, row count
and timestamp.

## Usage

The recommended way to use this app is to rely on `django_csv.views.download_csv`, which wraps up
the creation of the download object and the generation of the CSV itself:

```python
# DISPLAY PURPOSES ONLY: DO NOT ENABLE USER DATA DOWNLOADS IN PRODUCTION
def download_users(request: HttpRequest) -> HttpResponse:
    data = User.objects.all()
    columns = ("first_name", "last_name", "email")
    return download_csv(request.user, "users.csv", data, *columns)
```

## Settings

There is a `CSV_DOWNLOAD_MAX_ROWS` setting that is used to truncate output. Defaults to 10000.

## Examples

**Caution:** All of these examples involve the User model as it's ubiquitous - DO NOT DO THIS ON A
PRODUCTION ENVIRONMENT.

Example of writing a QuerySet to a file:

```python
>>> data = User.objects.all()
>>> columns = ("first_name", "last_name", "email")
>>> with open('users.csv', 'w') as csvfile:
>>>     csv.write_csv(csvfile, data, *columns)
10  #<--- row count
```

Example of writing to an HttpResponse:

```python
>>> response = HttpResponse(content_type="text/csv")
>>> response["Content-Disposition"] = 'attachment; filename="users.csv"'
>>> csv.write_csv(response, data, *columns)
10
```

Example of writing to an in-memory text buffer:

```python
>>> buffer = io.StringIO()
>>> csv.write_csv(buffer, data, *columns)
10
```
