
import pytest

from app.codes import (
    ALPHABET,
    LinkError,
    decode,
    encode,
    is_safe,
    normalise_url,
    validate_custom,
)


@pytest.mark.parametrize("number", [0, 1, 2, 10, 100, 999, 123456, 9999999])
def test_encode_decode_round_trip(number):
    assert decode(encode(number)) == number


def test_encode_zero():
    assert encode(0) == ALPHABET[0]


def test_encode_negative_number():
    with pytest.raises(LinkError):
        encode(-1)


def test_custom_code_valid():
    assert validate_custom("abc") == "abc"


@pytest.mark.parametrize("code", ["ab", "hello!", "abc0", "abc1", ""])
def test_custom_code_invalid(code):
    with pytest.raises(LinkError):
        validate_custom(code)


@pytest.mark.parametrize("code", ["api", "health", "docs", "admin"])
def test_reserved_code(code):
    with pytest.raises(LinkError):
        validate_custom(code)


def test_normalise_url_adds_scheme():
    assert normalise_url("example.com") == "https://example.com/"


def test_normalise_url_lowercases_host():
    assert normalise_url("https://EXAMPLE.COM/path") == (
        "https://example.com/path"
    )


def test_normalise_url_removes_default_port():
    assert normalise_url("https://example.com:443/") == (
        "https://example.com/"
    )


@pytest.mark.parametrize(
    "url",
    [None, "", "   ", "ftp://example.com", "https:///missing-host"],
)
def test_invalid_url(url):
    with pytest.raises(LinkError):
        normalise_url(url)


def test_is_safe_rejects_localhost():
    assert is_safe("http://localhost/") is False


def test_is_safe_rejects_private_ip():
    assert is_safe("http://192.168.1.1/") is False


def test_is_safe_accepts_public_url():
    assert is_safe("https://example.com/") is True

def test_decode_invalid_character():
    with pytest.raises(LinkError):
        decode("abc0")


def test_decode_invalid_uppercase_character():
    with pytest.raises(LinkError):
        decode("abc!")


def test_reserved_code_case_insensitive():
    with pytest.raises(LinkError):
        validate_custom("API")


def test_normalise_url_removes_trailing_host_dot():
    assert normalise_url("https://example.com./path") == (
        "https://example.com/path"
    )


def test_normalise_url_preserves_non_default_port():
    assert normalise_url("https://example.com:8443/path") == (
        "https://example.com:8443/path"
    )
