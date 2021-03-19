"""SFTP upload functions."""
import contextlib
import io
import tempfile
from typing import Generator, Optional

try:
    import paramiko
except ImportError:
    raise ImportError("You cannot use the django_csv.sftp module without paramiko.")


@contextlib.contextmanager
def sftp_upload(
    hostname: str,
    username: str,
    filepath: str,
    port: int = 22,
    password: Optional[str] = None,
    pkey: Optional[paramiko.PKey] = None,
) -> Generator:
    """
    Return context manager that can be used to upload to csv.

    This context manager writes to a NamedTemporaryFile and then uses
    the paramiko client put method to upload the file.

    One of password / pkey must be passed - see paramiko docs.

    >>> with sftp_upload("server", "user", "filename.csv", password="password") as fileobj:  # noqa
    ...     write_csv(fileobj, queryset, "col1", "col2")

    """
    # triple-nested context managers looks complicated, but we are dealing with
    # three objects that need cleanup post-use - the inner TextIO to which the
    # csv is written, the middle TemporaryFile used to persist the csv to disk
    # and the outer SFTP client through which the contents of the TemporaryFile
    # are written.
    with sftp_client(hostname, username, port, password, pkey) as client:
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
) -> Generator:
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
