"""Pure short-code and URL rules.

No database, no HTTP. This is the file to unit test.
"""
import re
from urllib.parse import urlsplit, urlunsplit

# Deliberately excludes 0/O and 1/l/I - a human reading a code aloud
# should not have to guess.
ALPHABET = "23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"
CODE_LEN = 7

# Paths the app itself uses. A short code must never shadow one.
RESERVED = {"api", "health", "static", "admin", "login", "docs", "openapi.json"}

_CODE_RE = re.compile(rf"^[{re.escape(ALPHABET)}]{{3,32}}$")


class LinkError(ValueError):
    pass


def encode(n):
    """Turn a positive integer into a short code.

    Using the row id rather than a random string means a code can never
    collide - the database already guarantees ids are unique.
    """
    if n < 0:
        raise LinkError("cannot encode a negative number")
    if n == 0:
        return ALPHABET[0]
    base = len(ALPHABET)
    out = []
    while n:
        n, rem = divmod(n, base)
        out.append(ALPHABET[rem])
    return "".join(reversed(out))


def decode(code):
    """Inverse of encode."""
    base = len(ALPHABET)
    n = 0
    for ch in code:
        idx = ALPHABET.find(ch)
        if idx < 0:
            raise LinkError(f"{ch!r} is not in the alphabet")
        n = n * base + idx
    return n


def validate_custom(code):
    """Check a user-supplied code before it is accepted."""
    c = str(code).strip()
    if not _CODE_RE.match(c):
        raise LinkError("a code must be 3-32 characters from the allowed alphabet")
    if c.lower() in RESERVED:
        raise LinkError(f"{c!r} is reserved")
    return c


def normalise_url(raw):
    """Tidy a URL so two spellings of the same page are treated as one.

    Lowercases the host, drops a default port, removes a trailing dot,
    and supplies a scheme when the user left it out.
    """
    if raw is None:
        raise LinkError("url is required")
    url = str(raw).strip()
    if not url:
        raise LinkError("url cannot be empty")
    if "://" not in url:
        url = "https://" + url

    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        raise LinkError("only http and https URLs are allowed")
    if not parts.hostname:
        raise LinkError("that URL has no host")

    host = parts.hostname.lower().rstrip(".")
    if parts.port and not (
        (parts.scheme == "http" and parts.port == 80)
        or (parts.scheme == "https" and parts.port == 443)
    ):
        host = f"{host}:{parts.port}"

    path = parts.path or "/"
    return urlunsplit((parts.scheme, host, path, parts.query, ""))


def is_safe(url):
    """Refuse URLs that would make the shortener attack its own network."""
    host = urlsplit(url).hostname or ""
    blocked = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"}
    if host in blocked:
        return False
    return not (host.startswith("10.") or host.startswith("192.168.")
                or host.startswith("169.254."))
