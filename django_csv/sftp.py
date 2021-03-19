"""SFTP upload functions."""
import contextlib
import io
import tempfile
from typing import Generator, Optional, TextIO, Tuple
from urllib.parse import urlparse

from django.db.models import QuerySet

from .csv import write_csv

try:
    import paramiko
except ImportError:
    raise ImportError("You cannot use the django_csv.sftp module without paramiko.")

# type used to represent "username:password@hostname:port/path" when parsed
SFTPUrl = Tuple[str, str, str, int, str]


@contextlib.contextmanager
def sftp_upload(
    client: paramiko.SFTPClient, filepath: str
) -> Generator[TextIO, None, None]:
    """
    Return context manager that can be used to upload to SFTP.

    This context manager writes to a NamedTemporaryFile and then uses
    the paramiko client `putfo` method to upload the file.

    >>> with sftp_upload(client, "path/to/file.csv) as fileobj:  # noqa
    ...     write_csv(fileobj, queryset, "col1", "col2")

    The client is not created inside the generator as it would have to then
    handle all of the various authentication mechanisms that SSH / paramiko
    support, and that is really up to the calling code. There is a convenience
    function, `write_csv_sftp` that handles the basic use case of a username
    and password auth.

    """
    with tempfile.TemporaryFile() as fileobj:
        with io.TextIOWrapper(
            fileobj,
            encoding="utf-8",
            newline="",
            write_through=True,
        ) as buffer:
            yield buffer
            fileobj.seek(0)
            client.putfo(fileobj, filepath)


@contextlib.contextmanager
def sftp_client(
    hostname: str,
    username: str,
    port: int = 22,
    password: Optional[str] = None,
    pkey: Optional[paramiko.PKey] = None,
) -> Generator[paramiko.SFTPClient, None, None]:
    """
    Connect to SFTP server and return client object.

    This is done as a context manager so that we always close the connection
    after use.

    """
    if not any([pkey, password]):
        raise ValueError("Unable to connect via SFTP without pkey or password")
    transport = paramiko.Transport((hostname, port))
    transport.connect(
        username=username,
        password=password,
        pkey=pkey,
    )
    if client := paramiko.SFTPClient.from_transport(transport):
        yield client
        client.close()
    else:
        raise Exception("Unable to connect to remote server.")


def parse_url(url: str) -> SFTPUrl:
    """Parse and validate url."""
    if not url.startswith("sftp://"):
        url = "sftp://" + url
    parts = urlparse(url)
    if parts.scheme != "sftp":
        raise ValueError("Invalid url: scheme must be 'sftp'.")
    if not parts.hostname:
        raise ValueError("Invalid url: hostname is missing.")
    if not parts.username:
        raise ValueError("Invalid url: username is missing.")
    if not parts.password:
        raise ValueError("Invalid url: password is missing.")
    if not parts.port:
        raise ValueError("Invalid url: port is missing.")
    if not parts.path.lstrip("/"):
        raise ValueError("Invalid url: file path is missing.")
    return (
        parts.hostname,
        parts.username,
        parts.password,
        parts.port,
        parts.path.lstrip("/"),
    )


def write_csv_sftp(
    url: str,
    queryset: QuerySet,
    *columns: str,
    header: bool = True,
    max_rows: int,
) -> int:
    """
    Write a csv to sftp.

    The url arg must be in the form:

        sftp://username:password@hostname:port/path

    All parts must exist, and a ValueError is raised if any
    are missing.

    """
    hostname, username, password, port, path = parse_url(url)
    with sftp_client(hostname, username, port=port, password=password) as client:
        with sftp_upload(client, path) as fileobj:
            return write_csv(
                fileobj, queryset, *columns, header=header, max_rows=max_rows
            )
