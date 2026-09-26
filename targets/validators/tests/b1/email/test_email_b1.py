"""Additional pytest tests for validators.email (batch 1)."""

# external
import pytest

# local
from validators import ValidationError, email


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid(value, **kwargs):
    """Assert that email() returns True for value."""
    result = email(value, **kwargs)
    assert result, f"Expected valid for {value!r}, got {result!r}"


def _invalid(value, **kwargs):
    """Assert that email() returns a ValidationError for value."""
    result = email(value, **kwargs)
    assert isinstance(result, ValidationError), (
        f"Expected ValidationError for {value!r}, got {result!r}"
    )


# ---------------------------------------------------------------------------
# Basic valid addresses
# ---------------------------------------------------------------------------

class TestBasicValid:
    """Well-formed email addresses that must pass."""

    @pytest.mark.parametrize("value", [
        "someone@example.com",
        "user.name@example.com",
        "user+tag@example.org",
        "user_name@example.co.uk",
        "user123@sub.domain.example.com",
        "a@b.com",
        "test@xn--nxasmq6b.com",          # punycode domain
        "USER@EXAMPLE.COM",                # uppercase (case-insensitive per RFC)
        "User.Name@Example.COM",
        "user!name@example.com",
        "user#name@example.com",
        "user$name@example.com",
        "user%name@example.com",
        "user&name@example.com",
        "user'name@example.com",
        "user*name@example.com",
        "user/name@example.com",
        "user=name@example.com",
        "user?name@example.com",
        "user^name@example.com",
        "user`name@example.com",
        "user{name}@example.com",
        "user|name@example.com",
        "user~name@example.com",
        "user-name@example.com",
    ])
    def test_valid_standard_addresses(self, value):
        """Docstring: email"""
        _valid(value)


# ---------------------------------------------------------------------------
# Basic invalid addresses
# ---------------------------------------------------------------------------

class TestBasicInvalid:
    """Addresses that must be rejected."""

    @pytest.mark.parametrize("value", [
        "bogus@@",
        "missingdomain@",
        "@nodomain.com",
        "no-at-sign",
        "",
        "two@@at@example.com",
        "space in@example.com",
        "user@",
        "user@.com",
    ])
    def test_invalid_addresses(self, value):
        """Docstring: email"""
        _invalid(value)

    def test_none_value(self):
        """Docstring: email"""
        # The validator is called with a positional-only str; passing None triggers
        # the falsy guard at the top of the function.
        result = email(None)
        assert not result

    def test_multiple_at_signs(self):
        """Docstring: email"""
        _invalid("a@b@c.com")


# ---------------------------------------------------------------------------
# Username length boundary (RFC 5321: max 64 octets)
# ---------------------------------------------------------------------------

class TestUsernameLengthLimit:
    """Username part must not exceed 64 characters."""

    def test_username_exactly_64_chars_is_valid(self):
        """Docstring: email"""
        username = "a" * 64
        _valid(f"{username}@example.com")

    def test_username_65_chars_is_invalid(self):
        """Docstring: email"""
        username = "a" * 65
        _invalid(f"{username}@example.com")

    def test_username_1_char_is_valid(self):
        """Docstring: email"""
        _valid("z@example.com")


# ---------------------------------------------------------------------------
# Domain length boundary (RFC 1034: max 253 octets)
# ---------------------------------------------------------------------------

class TestDomainLengthLimit:
    """Domain part must not exceed 253 characters."""

    def test_domain_exactly_253_chars_is_valid(self):
        """Docstring: email"""
        # Build a domain of exactly 253 characters using labels ≤ 63 chars each.
        # Pattern: four labels of 62 chars separated by dots = 62*4 + 3 = 251,
        # then add a 2-char TLD-like suffix: 62+1+62+1+62+1+62+1+2 = 252...
        # Simpler: use labels of 63 chars: 63.63.63.61 = 63+1+63+1+63+1+61 = 253
        label63 = "a" * 63
        label61 = "b" * 61
        domain_part = f"{label63}.{label63}.{label63}.{label61}"
        assert len(domain_part) == 253
        _valid(f"user@{domain_part}")

    def test_domain_254_chars_is_invalid(self):
        """Docstring: email"""
        # 63+1+63+1+63+1+62 = 254; last label is still ≤ 63
        label63 = "a" * 63
        label62 = "b" * 62
        domain_part = f"{label63}.{label63}.{label63}.{label62}"
        assert len(domain_part) == 254
        _invalid(f"user@{domain_part}")


# ---------------------------------------------------------------------------
# Quoted-string usernames
# ---------------------------------------------------------------------------

class TestQuotedUsernames:
    """RFC 5321 allows quoted-string local parts."""

    @pytest.mark.parametrize("value", [
        '"user.name"@example.com',     # dot inside quotes
        '"user!name"@example.com',     # ! inside quotes (0x21, included in class)
        '"user#name"@example.com',     # # inside quotes (0x23, included)
    ])
    def test_valid_quoted_username(self, value):
        """Docstring: email"""
        _valid(value)

    @pytest.mark.parametrize("value", [
        '"user name"@example.com',     # space (0x20) not in quoted-string class
        '"user@name"@example.com',     # two @ signs — fails count check before split
    ])
    def test_invalid_quoted_username(self, value):
        """Docstring: email"""
        _invalid(value)


# ---------------------------------------------------------------------------
# IPv4 domain (ipv4_address flag)
# ---------------------------------------------------------------------------

class TestIPv4Domain:
    """Domain part can be an IPv4 literal when ipv4_address=True."""

    @pytest.mark.parametrize("value", [
        "user@[192.168.1.1]",
        "user@[10.0.0.1]",
        "user@[8.8.8.8]",
    ])
    def test_ipv4_domain_valid_with_flag(self, value):
        """Docstring: email"""
        _valid(value, ipv4_address=True)

    @pytest.mark.parametrize("value", [
        "user@[192.168.1.1]",
        "user@[10.0.0.1]",
    ])
    def test_ipv4_domain_invalid_without_flag(self, value):
        """Docstring: email"""
        _invalid(value)

    def test_ipv4_domain_missing_brackets_invalid(self):
        """Docstring: email"""
        # Without the surrounding brackets the validator rejects it even with flag
        _invalid("user@192.168.1.1", ipv4_address=True)


# ---------------------------------------------------------------------------
# IPv6 domain (ipv6_address flag)
# ---------------------------------------------------------------------------

class TestIPv6Domain:
    """Domain part can be an IPv6 literal when ipv6_address=True."""

    @pytest.mark.parametrize("value", [
        "user@[::1]",
        "user@[2001:db8::1]",
        "user@[FEDC:BA98:7654:3210:FEDC:BA98:7654:3210]",
    ])
    def test_ipv6_domain_valid_with_flag(self, value):
        """Docstring: email"""
        _valid(value, ipv6_address=True)

    @pytest.mark.parametrize("value", [
        "user@[::1]",
        "user@[2001:db8::1]",
    ])
    def test_ipv6_domain_invalid_without_flag(self, value):
        """Docstring: email"""
        _invalid(value)

    def test_ipv6_domain_missing_brackets_invalid(self):
        """Docstring: email"""
        _invalid("user@::1", ipv6_address=True)


# ---------------------------------------------------------------------------
# simple_host flag
# ---------------------------------------------------------------------------

class TestSimpleHost:
    """Domain can be a plain hostname (no TLD) when simple_host=True."""

    @pytest.mark.parametrize("value", [
        "user@localhost",
        "user@mailhost",
        "user@intranet",
    ])
    def test_simple_host_valid_with_flag(self, value):
        """Docstring: email"""
        _valid(value, simple_host=True)

    @pytest.mark.parametrize("value", [
        "user@localhost",
        "user@mailhost",
    ])
    def test_simple_host_invalid_without_flag(self, value):
        """Docstring: email"""
        _invalid(value)


# ---------------------------------------------------------------------------
# rfc_1034 flag — trailing dot in domain
# ---------------------------------------------------------------------------

class TestRFC1034TrailingDot:
    """Trailing dot in domain is allowed only when rfc_1034=True."""

    def test_trailing_dot_invalid_by_default(self):
        """Docstring: email"""
        _invalid("user@example.com.")

    def test_trailing_dot_valid_with_rfc_1034(self):
        """Docstring: email"""
        _valid("user@example.com.", rfc_1034=True)

    def test_no_trailing_dot_valid_without_flag(self):
        """Docstring: email"""
        _valid("user@example.com")


# ---------------------------------------------------------------------------
# rfc_2782 flag — service record domain
# ---------------------------------------------------------------------------

class TestRFC2782ServiceRecord:
    """Domain prefixed with underscore labels (SRV records) needs rfc_2782=True."""

    def test_srv_domain_valid_with_rfc_2782(self):
        """Docstring: email"""
        _valid("user@_smtp._tcp.example.com", rfc_2782=True)

    def test_srv_domain_invalid_without_rfc_2782(self):
        """Docstring: email"""
        _invalid("user@_smtp._tcp.example.com")


# ---------------------------------------------------------------------------
# Extended Latin / Unicode usernames
# ---------------------------------------------------------------------------

class TestExtendedLatinUsernames:
    """Extended Latin characters in the local part are permitted."""

    @pytest.mark.parametrize("value", [
        "üser@example.com",        # U+00FC in local part
        "ñame@example.com",        # U+00F1
        "użytkownik@example.com",  # U+017C
    ])
    def test_extended_latin_username_valid(self, value):
        """Docstring: email"""
        _valid(value)


# ---------------------------------------------------------------------------
# Dot handling in local part
# ---------------------------------------------------------------------------

class TestDotHandling:
    """Dots within the local part are fine; leading/trailing dots are not."""

    def test_dot_in_middle_is_valid(self):
        """Docstring: email"""
        _valid("first.last@example.com")

    def test_multiple_dots_in_local_valid(self):
        """Docstring: email"""
        _valid("a.b.c.d@example.com")

    def test_leading_dot_in_local_is_invalid(self):
        """Docstring: email"""
        _invalid(".user@example.com")

    def test_trailing_dot_in_local_is_invalid(self):
        """Docstring: email"""
        _invalid("user.@example.com")

    def test_consecutive_dots_in_local_invalid(self):
        """Docstring: email"""
        _invalid("user..name@example.com")
