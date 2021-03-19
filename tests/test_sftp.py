import pytest

from django_csv import sftp


@pytest.mark.parametrize(
    "url,scheme,username,password,hostname,port,path",
    (
        (
            "sftp://username:password@hostname:22/path",
            "sftp",
            "username",
            "password",
            "hostname",
            22,
            "path",
        ),
        (
            "username:password@hostname:22/path",
            "sftp",
            "username",
            "password",
            "hostname",
            22,
            "path",
        ),
    ),
)
def test_parse_url(url, scheme, username, password, hostname, port, path):
    assert sftp.parse_url(url) == (hostname, username, password, port, path)


@pytest.mark.parametrize(
    "url",
    (
        "",
        "username:password",
        "username@hostname",
        "username@hostname:20",
        "sftp://username:@hostname:20/path",
        "sftp://:password@hostname:20/path",
        "sftp://username:password@hostname:20/",
    ),
)
def test_parse_url__error(url):
    with pytest.raises(ValueError):
        sftp.parse_url(url)
