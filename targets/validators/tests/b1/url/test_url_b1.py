"""Additional pytest tests for validators.url (batch 1)."""

# external
import pytest

# local
from validators import ValidationError, url


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _valid(value, **kwargs):
    """Assert that url() returns True for value."""
    result = url(value, **kwargs)
    assert result is True, f"Expected True for {value!r}, got {result!r}"


def _invalid(value, **kwargs):
    """Assert that url() returns a ValidationError for value."""
    result = url(value, **kwargs)
    assert isinstance(result, ValidationError), (
        f"Expected ValidationError for {value!r}, got {result!r}"
    )


# ---------------------------------------------------------------------------
# Scheme validation
# ---------------------------------------------------------------------------

class TestSchemes:
    """Tests focused on URL scheme handling."""

    @pytest.mark.parametrize("value", [
        "ftp://files.example.com/resource",
        "ftps://files.example.com/resource",
        "git://github.com/user/repo",
        "irc://irc.freenode.net/channel",
        "rtmp://live.example.com/stream",
        "rtmps://live.example.com/stream",
        "rtsp://media.example.com/video",
        "sftp://storage.example.com/data",
        "ssh://user@host.example.com",
        "telnet://host.example.com",
    ])
    def test_all_supported_schemes_are_valid(self, value):
        _valid(value)

    @pytest.mark.parametrize("value", [
        "mailto:user@example.com",
        "javascript:alert(1)",
        "data:text/html,<h1>hello</h1>",
        "file:///etc/passwd",
        "ws://example.com/socket",
        "wss://example.com/socket",
        "urn:isbn:0451450523",
    ])
    def test_unsupported_schemes_are_invalid(self, value):
        _invalid(value)

    def test_empty_string_is_invalid(self):
        _invalid("")

    def test_none_like_missing_scheme_is_invalid(self):
        _invalid("example.com")

    def test_custom_validate_scheme_callable(self):
        """A custom validate_scheme that allows only 'myapp'."""
        result = url("myapp://service.example.com", validate_scheme=lambda s: s == "myapp")
        assert result is True

    def test_custom_validate_scheme_rejects_http(self):
        result = url("http://example.com", validate_scheme=lambda s: s == "myapp")
        assert isinstance(result, ValidationError)


# ---------------------------------------------------------------------------
# Whitespace rejection
# ---------------------------------------------------------------------------

class TestWhitespace:
    """URLs must not contain unencoded whitespace."""

    @pytest.mark.parametrize("value", [
        "http://example.com/path with spaces",
        "http://example.com/path\twith\ttabs",
        "http://example.com/path\nwith\nnewlines",
        " http://example.com",
        "http://example.com ",
    ])
    def test_whitespace_in_url_is_invalid(self, value):
        _invalid(value)

    def test_percent_encoded_space_is_valid(self):
        _valid("http://example.com/path%20with%20spaces")


# ---------------------------------------------------------------------------
# simple_host flag
# ---------------------------------------------------------------------------

class TestSimpleHost:
    """Tests for the simple_host parameter."""

    @pytest.mark.parametrize("value", [
        "http://localhost",
        "http://localhost:8000",
        "http://pc:8081/",
        "http://myhost/path",
    ])
    def test_simple_host_urls_valid_when_flag_set(self, value):
        _valid(value, simple_host=True)

    @pytest.mark.parametrize("value", [
        "http://localhost",
        "http://myhost/path",
    ])
    def test_simple_host_urls_invalid_without_flag(self, value):
        _invalid(value)


# ---------------------------------------------------------------------------
# strict_query flag
# ---------------------------------------------------------------------------

class TestStrictQuery:
    """Tests for the strict_query parameter."""

    @pytest.mark.parametrize("value", [
        "https://www.example.com/foo/?bar=baz&inga=42&quux",
        "https://foo.bar.net/baz.php?-/inga/test-lenient-query/",
        "https://foo.com/img/bar/baz.jpg?-62169987208",
    ])
    def test_lenient_query_valid_when_strict_false(self, value):
        _valid(value, strict_query=False)

    @pytest.mark.parametrize("value", [
        "https://www.example.com/foo/?bar=baz&inga=42&quux",
        "https://foo.bar.net/baz.php?-/inga/test-lenient-query/",
        "https://foo.com/img/bar/baz.jpg?-62169987208",
    ])
    def test_lenient_query_invalid_with_strict_true(self, value):
        _invalid(value, strict_query=True)


# ---------------------------------------------------------------------------
# skip_ipv4_addr flag
# ---------------------------------------------------------------------------

class TestSkipIPv4:
    """Tests for the skip_ipv4_addr parameter."""

    @pytest.mark.parametrize("value", [
        "http://192.168.1.1/path",
        "http://10.0.0.1",
        "http://8.8.8.8",
    ])
    def test_ipv4_url_valid_by_default(self, value):
        _valid(value)

    @pytest.mark.parametrize("value", [
        "http://192.168.1.1/path",
        "http://10.0.0.1",
        "http://8.8.8.8",
    ])
    def test_ipv4_url_invalid_when_skipped(self, value):
        _invalid(value, skip_ipv4_addr=True)


# ---------------------------------------------------------------------------
# skip_ipv6_addr flag
# ---------------------------------------------------------------------------

class TestSkipIPv6:
    """Tests for the skip_ipv6_addr parameter."""

    @pytest.mark.parametrize("value", [
        "http://[FEDC:BA98:7654:3210:FEDC:BA98:7654:3210]:80/index.html",
        "http://[::1]/path",
    ])
    def test_ipv6_url_valid_by_default(self, value):
        _valid(value)

    @pytest.mark.parametrize("value", [
        "http://[FEDC:BA98:7654:3210:FEDC:BA98:7654:3210]:80/index.html",
        "http://[::1]/path",
    ])
    def test_ipv6_url_invalid_when_skipped(self, value):
        _invalid(value, skip_ipv6_addr=True)


# ---------------------------------------------------------------------------
# may_have_port flag
# ---------------------------------------------------------------------------

class TestMayHavePort:
    """Tests for the may_have_port parameter."""

    @pytest.mark.parametrize("value", [
        "http://example.com:8080/path",
        "https://api.example.com:443/v1",
        "http://10.0.0.1:3000",
    ])
    def test_port_valid_when_allowed(self, value):
        _valid(value, may_have_port=True)

    @pytest.mark.parametrize("value", [
        "http://example.com:8080/path",
        "https://api.example.com:443/v1",
        "http://10.0.0.1:3000",
    ])
    def test_port_invalid_when_disallowed(self, value):
        _invalid(value, may_have_port=False)


# ---------------------------------------------------------------------------
# private IP flag
# ---------------------------------------------------------------------------

class TestPrivateIP:
    """Tests for the private parameter."""

    @pytest.mark.parametrize("value", [
        "http://192.168.0.1",
        "http://10.10.10.10",
        "http://172.16.0.1",
    ])
    def test_private_ip_valid_with_private_true(self, value):
        _valid(value, private=True)

    @pytest.mark.parametrize("value", [
        "http://192.168.0.1",
        "http://10.10.10.10",
        "http://172.16.0.1",
    ])
    def test_private_ip_invalid_with_private_false(self, value):
        _invalid(value, private=False)

    @pytest.mark.parametrize("value", [
        "http://8.8.8.8",
        "http://1.1.1.1",
    ])
    def test_public_ip_valid_with_private_false(self, value):
        _valid(value, private=False)

    @pytest.mark.parametrize("value", [
        "http://8.8.8.8",
        "http://1.1.1.1",
    ])
    def test_public_ip_invalid_with_private_true(self, value):
        _invalid(value, private=True)


# ---------------------------------------------------------------------------
# rfc_1034 — trailing dot in hostname
# ---------------------------------------------------------------------------

class TestRFC1034:
    """Tests for rfc_1034 (trailing dot) flag."""

    def test_trailing_dot_invalid_by_default(self):
        _invalid("http://www.foo.bar./")

    def test_trailing_dot_valid_when_rfc_1034(self):
        _valid("http://www.example.com./path", rfc_1034=True)


# ---------------------------------------------------------------------------
# Fragment validation
# ---------------------------------------------------------------------------

class TestFragments:
    """Tests for fragment section of URLs."""

    @pytest.mark.parametrize("value", [
        "http://example.com/page#section-1",
        "http://example.com/#top",
        "https://example.com/path#anchor_name",
        "https://exchange.jetswap.finance/#/swap",
        "https://example.org/path#2022%201040%20(Cornelius%20Morgan%20G).pdf",
    ])
    def test_valid_fragments(self, value):
        _valid(value)


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------

class TestPaths:
    """Tests for URL path component."""

    @pytest.mark.parametrize("value", [
        "http://example.com/simple/path",
        "http://example.com/path/with-dashes",
        "http://example.com/path_with_underscores",
        "http://example.com/path.with.dots",
        "http://example.com/path%20encoded",
        "http://foo.com/📍",
    ])
    def test_valid_paths(self, value):
        _valid(value)
