"""Additional pytest tests for validators.hostname (batch 1)."""

# external
import pytest

# local
from validators import ValidationError, hostname


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid(value, **kwargs):
    """Assert that hostname() returns truthy for value."""
    result = hostname(value, **kwargs)
    assert result, f"Expected valid for {value!r}, got {result!r}"


def _invalid(value, **kwargs):
    """Assert that hostname() returns a ValidationError for value."""
    result = hostname(value, **kwargs)
    assert isinstance(result, ValidationError), (
        f"Expected ValidationError for {value!r}, got {result!r}"
    )


# ---------------------------------------------------------------------------
# Docstring examples
# ---------------------------------------------------------------------------

class TestDocstringExamples:
    """Docstring: hostname — verbatim examples from the docstring."""

    def test_simple_hostname_with_port(self):
        """Docstring: hostname"""
        _valid("ubuntu-pc:443")

    def test_simple_hostname_no_port(self):
        """Docstring: hostname"""
        _valid("this-pc")

    def test_idn_hostname_with_port(self):
        """Docstring: hostname"""
        _valid("xn----gtbspbbmkef.xn--p1ai:65535")

    def test_underscore_prefix_is_invalid(self):
        """Docstring: hostname"""
        _invalid("_example.com")

    def test_ipv4_with_port(self):
        """Docstring: hostname"""
        _valid("123.5.77.88:31000")

    def test_ipv4_bare(self):
        """Docstring: hostname"""
        _valid("12.12.12.12")

    def test_ipv6_bracketed_with_port(self):
        """Docstring: hostname"""
        _valid("[::1]:22")

    def test_ipv6_bare(self):
        """Docstring: hostname"""
        _valid("dead:beef:0:0:0:0000:42:1")

    def test_negative_port_is_invalid(self):
        """Docstring: hostname"""
        _invalid("[0:0:0:0:0:ffff:1.2.3.4]:-65538")

    def test_invalid_ipv6_chars_with_port(self):
        """Docstring: hostname"""
        _invalid("[0:&:b:c:@:e:f::]:9999")


# ---------------------------------------------------------------------------
# Empty / None guard
# ---------------------------------------------------------------------------

class TestEmptyInput:
    """Docstring: hostname"""

    def test_empty_string_is_invalid(self):
        """Docstring: hostname"""
        _invalid("")


# ---------------------------------------------------------------------------
# Simple hostname (maybe_simple=True, the default)
# ---------------------------------------------------------------------------

class TestSimpleHostname:
    """Tests for the simple hostname (no dot) path."""

    @pytest.mark.parametrize("value", [
        "localhost",
        "myserver",
        "web01",
        "a",                    # single char
        "a1",                   # two chars
        "server-01",
        "ubuntu-pc",
        "UPPERCASE",
        "MixedCase",
        "a" * 61,               # exactly 61 chars (max for simple label)
    ])
    def test_valid_simple_hostnames(self, value):
        """Docstring: hostname"""
        _valid(value)

    @pytest.mark.parametrize("value", [
        "-startswithhyphen",
        "endswithhyphen-",
        "has space",
        "a" * 64,               # too long for a single label (>63)
    ])
    def test_invalid_simple_hostnames(self, value):
        """Docstring: hostname"""
        _invalid(value)

    def test_simple_hostname_disabled(self):
        """Docstring: hostname"""
        # "localhost" is only a valid simple hostname; with maybe_simple=False
        # it is not a valid domain or IP address.
        _invalid("localhost", maybe_simple=False)

    def test_simple_hostname_enabled_by_default(self):
        """Docstring: hostname"""
        _valid("myhost")


# ---------------------------------------------------------------------------
# Domain-based hostnames
# ---------------------------------------------------------------------------

class TestDomainHostname:
    """Tests for hostnames that are valid domain names."""

    @pytest.mark.parametrize("value", [
        "example.com",
        "sub.example.com",
        "deep.sub.example.org",
        "xn----gtbspbbmkef.xn--p1ai",
        "my-host.example.net",
    ])
    def test_valid_domain_hostnames(self, value):
        """Docstring: hostname"""
        _valid(value)

    @pytest.mark.parametrize("value", [
        "example..com",         # consecutive dots
        "-example.com",
        "example-.com",
        "example.com/path",     # path not allowed in hostname
        "example_domain.com",   # underscore not allowed without rfc_2782
    ])
    def test_invalid_domain_hostnames(self, value):
        """Docstring: hostname"""
        _invalid(value)


# ---------------------------------------------------------------------------
# IPv4 address handling
# ---------------------------------------------------------------------------

class TestIPv4:
    """Tests for IPv4 address hostnames."""

    @pytest.mark.parametrize("value", [
        "192.168.1.1",
        "10.0.0.1",
        "8.8.8.8",
        "255.255.255.255",
        "0.0.0.0",
    ])
    def test_valid_ipv4(self, value):
        """Docstring: hostname"""
        _valid(value)

    @pytest.mark.parametrize("value", [
        "192.168.1.1",
        "10.0.0.1",
        "8.8.8.8",
    ])
    def test_ipv4_rejected_when_skipped(self, value):
        """Docstring: hostname"""
        _invalid(value, skip_ipv4_addr=True)

    def test_ipv4_cidr_is_invalid(self):
        """Docstring: hostname"""
        # CIDR notation is not a hostname
        _invalid("192.168.1.0/24")

    @pytest.mark.parametrize("value", [
        "192.168.1.1",
        "10.0.0.1",
        "172.16.0.1",
    ])
    def test_private_ipv4_accepted_with_private_true(self, value):
        """Docstring: hostname"""
        _valid(value, private=True)

    @pytest.mark.parametrize("value", [
        "192.168.1.1",
        "10.0.0.1",
        "172.16.0.1",
    ])
    def test_private_ipv4_rejected_with_private_false(self, value):
        """Docstring: hostname"""
        _invalid(value, private=False)

    @pytest.mark.parametrize("value", [
        "8.8.8.8",
        "1.1.1.1",
    ])
    def test_public_ipv4_accepted_with_private_false(self, value):
        """Docstring: hostname"""
        _valid(value, private=False)

    @pytest.mark.parametrize("value", [
        "8.8.8.8",
        "1.1.1.1",
    ])
    def test_public_ipv4_rejected_with_private_true(self, value):
        """Docstring: hostname"""
        _invalid(value, private=True)


# ---------------------------------------------------------------------------
# IPv6 address handling
# ---------------------------------------------------------------------------

class TestIPv6:
    """Tests for IPv6 address hostnames."""

    @pytest.mark.parametrize("value", [
        "::1",
        "dead:beef:0:0:0:0000:42:1",
        "2001:db8::1",
        "fe80::1",
    ])
    def test_valid_ipv6(self, value):
        """Docstring: hostname"""
        _valid(value)

    @pytest.mark.parametrize("value", [
        "[::1]",                # brackets without port are not valid bare hostnames
        "[2001:db8::1]",
    ])
    def test_bracketed_ipv6_without_port_is_invalid(self, value):
        """Docstring: hostname"""
        _invalid(value)

    @pytest.mark.parametrize("value", [
        "::1",
        "dead:beef:0:0:0:0000:42:1",
        "2001:db8::1",
    ])
    def test_ipv6_rejected_when_skipped(self, value):
        """Docstring: hostname"""
        _invalid(value, skip_ipv6_addr=True)

    def test_invalid_ipv6_bad_chars(self):
        """Docstring: hostname"""
        _invalid("[0:&:b:c:@:e:f::]")

    def test_ipv6_cidr_is_invalid(self):
        """Docstring: hostname"""
        _invalid("::1/128")


# ---------------------------------------------------------------------------
# Port handling (may_have_port / _port_validator)
# ---------------------------------------------------------------------------

class TestPortHandling:
    """Tests for port parsing in hostnames."""

    @pytest.mark.parametrize("value", [
        "localhost:1",
        "localhost:80",
        "localhost:8080",
        "localhost:65535",
        "example.com:443",
        "example.com:8080",
        "192.168.1.1:3000",
        "[::1]:22",
        "[2001:db8::1]:8080",
        "xn----gtbspbbmkef.xn--p1ai:65535",
    ])
    def test_valid_hostnames_with_port(self, value):
        """Docstring: hostname"""
        _valid(value)

    @pytest.mark.parametrize("value", [
        "localhost:0",          # port 0 is not valid per regex
        "localhost:65536",      # out of range
        "localhost:99999",
        "localhost:-1",
        "localhost:port",
        "[::1]:-1",
        "[::1]:65536",
    ])
    def test_invalid_ports(self, value):
        """Docstring: hostname"""
        _invalid(value)

    @pytest.mark.parametrize("value", [
        "localhost:8080",
        "example.com:443",
        "192.168.1.1:3000",
        "[::1]:22",
    ])
    def test_port_rejected_when_may_have_port_false(self, value):
        """Docstring: hostname"""
        _invalid(value, may_have_port=False)

    def test_bare_hostname_valid_when_may_have_port_false(self):
        """Docstring: hostname"""
        # A pure hostname without a port should still be valid even
        # when may_have_port=False.
        _valid("localhost", may_have_port=False)

    def test_port_boundary_65535(self):
        """Docstring: hostname"""
        _valid("example.com:65535")

    def test_port_boundary_1(self):
        """Docstring: hostname"""
        _valid("example.com:1")


# ---------------------------------------------------------------------------
# rfc_1034 — trailing dot
# ---------------------------------------------------------------------------

class TestRFC1034:
    """Tests for rfc_1034 (trailing dot) flag."""

    def test_trailing_dot_invalid_by_default(self):
        """Docstring: hostname"""
        _invalid("example.com.")

    def test_trailing_dot_valid_with_rfc_1034(self):
        """Docstring: hostname"""
        _valid("example.com.", rfc_1034=True)

    def test_trailing_dot_with_port_valid_when_rfc_1034(self):
        """Docstring: hostname"""
        _valid("example.com.:8080", rfc_1034=True)

    def test_no_trailing_dot_still_valid_with_rfc_1034(self):
        """Docstring: hostname"""
        _valid("example.com", rfc_1034=True)


# ---------------------------------------------------------------------------
# rfc_2782 — service record (SRV) underscore labels
# ---------------------------------------------------------------------------

class TestRFC2782:
    """Tests for rfc_2782 (service record underscores) flag."""

    def test_srv_record_invalid_without_flag(self):
        """Docstring: hostname"""
        _invalid("_http._tcp.example.com")

    def test_srv_record_valid_with_flag(self):
        """Docstring: hostname"""
        _valid("_http._tcp.example.com", rfc_2782=True)

    def test_double_underscore_still_invalid_with_rfc_2782(self):
        """Docstring: hostname"""
        # Double underscores are explicitly banned even with rfc_2782=True.
        _invalid("__double.example.com", rfc_2782=True)


# ---------------------------------------------------------------------------
# consider_tld
# ---------------------------------------------------------------------------

class TestConsiderTLD:
    """Tests for the consider_tld flag."""

    def test_valid_tld_com(self):
        """Docstring: hostname"""
        _valid("example.com", consider_tld=True)

    def test_valid_tld_org(self):
        """Docstring: hostname"""
        _valid("example.org", consider_tld=True)

    def test_invalid_tld_fakeext(self):
        """Docstring: hostname"""
        _invalid("example.invalidtldxyz", consider_tld=True)

    def test_unknown_tld_valid_without_flag(self):
        """Docstring: hostname"""
        # Without consider_tld any syntactically valid TLD-like suffix passes.
        _valid("example.invalidtldxyz", consider_tld=False)


# ---------------------------------------------------------------------------
# Combined skip flags
# ---------------------------------------------------------------------------

class TestSkipFlags:
    """Tests for combining skip_ipv4_addr and skip_ipv6_addr."""

    def test_domain_still_valid_when_both_ip_types_skipped(self):
        """Docstring: hostname"""
        _valid("example.com", skip_ipv4_addr=True, skip_ipv6_addr=True)

    def test_simple_host_still_valid_when_both_ip_types_skipped(self):
        """Docstring: hostname"""
        _valid("myhost", skip_ipv4_addr=True, skip_ipv6_addr=True)

    def test_ipv4_invalid_when_skip_ipv4(self):
        """Docstring: hostname"""
        _invalid("8.8.8.8", skip_ipv4_addr=True)

    def test_ipv6_invalid_when_skip_ipv6(self):
        """Docstring: hostname"""
        _invalid("::1", skip_ipv6_addr=True)
