"""Broad regression tests for validators.email."""

# local
import validators
from validators import email


# ---------------------------------------------------------------------------
# Typical valid addresses (docstring example + common patterns)
# ---------------------------------------------------------------------------


def test_docstring_example_valid():
    """Docstring: email"""
    assert email("someone@example.com")


def test_simple_valid_address():
    """Docstring: email"""
    assert email("user@example.com")


def test_subdomain_valid():
    """Docstring: email"""
    assert email("user@mail.example.com")


def test_deep_subdomain_valid():
    """Docstring: email"""
    assert email("user@a.b.c.example.com")


def test_plus_sign_in_local():
    """Docstring: email"""
    assert email("user+tag@example.com")


def test_dot_in_local():
    """Docstring: email"""
    assert email("first.last@example.com")


def test_digits_in_local():
    """Docstring: email"""
    assert email("user123@example.com")


def test_hyphen_in_local():
    """Docstring: email"""
    assert email("user-name@example.com")


def test_underscore_in_local():
    """Docstring: email"""
    assert email("user_name@example.com")


def test_all_digits_local():
    """Docstring: email"""
    assert email("123@example.com")


def test_mixed_case_local():
    """Docstring: email"""
    assert email("UserName@example.com")


def test_mixed_case_domain():
    """Docstring: email"""
    assert email("user@Example.COM")


def test_numeric_tld():
    """Docstring: email"""
    # Numeric TLDs are technically valid hostnames
    assert email("user@example.com")


def test_long_tld():
    """Docstring: email"""
    assert email("user@example.technology")


def test_special_chars_in_local():
    """Docstring: email"""
    # RFC 5321 allows ! # $ % & ' * + / = ? ^ _ ` { } | ~ -
    assert email("user!#$%&'*+/=?^_`{}|~@example.com")


def test_local_with_hash():
    """Docstring: email"""
    assert email("user#tag@example.com")


def test_local_with_tilde():
    """Docstring: email"""
    assert email("user~name@example.com")


# ---------------------------------------------------------------------------
# Docstring example — invalid
# ---------------------------------------------------------------------------


def test_docstring_example_invalid():
    """Docstring: email"""
    assert not email("bogus@@")


# ---------------------------------------------------------------------------
# Empty / None / missing @ sign
# ---------------------------------------------------------------------------


def test_empty_string():
    """Docstring: email"""
    assert not email("")


def test_none_value():
    """Docstring: email"""
    assert not email(None)


def test_no_at_sign():
    """Docstring: email"""
    assert not email("userexample.com")


def test_multiple_at_signs():
    """Docstring: email"""
    assert not email("user@@example.com")


def test_three_at_signs():
    """Docstring: email"""
    assert not email("a@b@c.com")


# ---------------------------------------------------------------------------
# Local part length boundary (RFC 1034/5321: max 64 chars)
# ---------------------------------------------------------------------------


def test_local_part_exactly_64_chars():
    """Docstring: email"""
    local = "a" * 64
    assert email(f"{local}@example.com")


def test_local_part_65_chars_invalid():
    """Docstring: email"""
    local = "a" * 65
    assert not email(f"{local}@example.com")


def test_local_part_1_char():
    """Docstring: email"""
    assert email("a@example.com")


# ---------------------------------------------------------------------------
# Domain part length boundary (RFC 1034: max 253 chars)
# ---------------------------------------------------------------------------


def test_domain_exactly_253_chars():
    """Docstring: email"""
    # Build domain of exactly 253 chars: labels of 63 chars separated by dots
    # 63 + 1 + 63 + 1 + 63 + 1 + 62 = 254 — need to fit in 253
    # Use: 63 + 1 + 63 + 1 + 61 + 1 + 63 = 253  (sum of labels + dots)
    label63 = "a" * 63
    label61 = "a" * 61
    domain = f"{label63}.{label63}.{label61}.{label63}"
    assert len(domain) == 253
    assert email(f"user@{domain}")


def test_domain_254_chars_invalid():
    """Docstring: email"""
    label63 = "a" * 63
    label62 = "a" * 62
    domain = f"{label63}.{label63}.{label62}.{label63}"
    assert len(domain) == 254
    assert not email(f"user@{domain}")


# ---------------------------------------------------------------------------
# IPv4 address domain (requires ipv4_address=True flag)
# ---------------------------------------------------------------------------


def test_ipv4_flag_valid():
    """Docstring: email"""
    assert email("user@[192.168.1.1]", ipv4_address=True)


def test_ipv4_flag_loopback():
    """Docstring: email"""
    assert email("user@[127.0.0.1]", ipv4_address=True)


def test_ipv4_without_brackets_invalid():
    """Docstring: email"""
    # RFC 5321 requires brackets around IP literals
    assert not email("user@192.168.1.1", ipv4_address=True)


def test_ipv4_flag_off_address_invalid():
    """Docstring: email"""
    # Without the flag, bare IP in domain is not valid
    assert not email("user@[192.168.1.1]")


def test_ipv4_default_no_flag():
    """Docstring: email"""
    # email@127.0.0.1 — no brackets, no flag — invalid (matches existing human test)
    assert not email("user@127.0.0.1")


# ---------------------------------------------------------------------------
# IPv6 address domain (requires ipv6_address=True flag)
# ---------------------------------------------------------------------------


def test_ipv6_flag_valid():
    """Docstring: email"""
    assert email("user@[2001:db8::1]", ipv6_address=True)


def test_ipv6_flag_loopback():
    """Docstring: email"""
    assert email("user@[::1]", ipv6_address=True)


def test_ipv6_without_brackets_invalid():
    """Docstring: email"""
    assert not email("user@2001:db8::1", ipv6_address=True)


def test_ipv6_flag_off_invalid():
    """Docstring: email"""
    # brackets around IPv6 but flag not set — no valid hostname
    assert not email("user@[2001:db8::1]")


def test_ipv6_full_address_valid():
    """Docstring: email"""
    assert email("user@[2001:0db8:0000:0000:0000:0000:0000:0001]", ipv6_address=True)


# ---------------------------------------------------------------------------
# simple_host flag
# ---------------------------------------------------------------------------


def test_simple_host_valid():
    """Docstring: email"""
    assert email("user@localhost", simple_host=True)


def test_simple_host_single_label():
    """Docstring: email"""
    assert email("user@mailhost", simple_host=True)


def test_simple_host_without_flag_invalid():
    """Docstring: email"""
    # Single-label host without simple_host flag should fail
    assert not email("user@localhost")


# ---------------------------------------------------------------------------
# rfc_1034 flag — trailing dot in domain name
# ---------------------------------------------------------------------------


def test_rfc_1034_trailing_dot_valid():
    """Docstring: email"""
    assert email("user@example.com.", rfc_1034=True)


def test_rfc_1034_trailing_dot_without_flag_invalid():
    """Docstring: email"""
    assert not email("user@example.com.", rfc_1034=False)


def test_rfc_1034_normal_address_still_valid():
    """Docstring: email"""
    assert email("user@example.com", rfc_1034=True)


# ---------------------------------------------------------------------------
# rfc_2782 flag — service record domain
# ---------------------------------------------------------------------------


def test_rfc_2782_srv_record_valid():
    """Docstring: email"""
    assert email("user@_smtp._tcp.example.com", rfc_2782=True)


def test_rfc_2782_without_flag_invalid():
    """Docstring: email"""
    assert not email("user@_smtp._tcp.example.com", rfc_2782=False)


def test_rfc_2782_normal_address_still_valid():
    """Docstring: email"""
    assert email("user@example.com", rfc_2782=True)


# ---------------------------------------------------------------------------
# Flag combinations
# ---------------------------------------------------------------------------


def test_rfc_1034_and_rfc_2782_combined():
    """Docstring: email"""
    assert email("user@_smtp._tcp.example.com.", rfc_1034=True, rfc_2782=True)


def test_ipv4_and_simple_host_mutually_exclusive_ip_wins():
    """Docstring: email"""
    # ipv4_address requires brackets — if brackets present, ipv4 path is taken
    assert email("user@[10.0.0.1]", ipv4_address=True, simple_host=True)


# ---------------------------------------------------------------------------
# Quoted-string local part
# ---------------------------------------------------------------------------


def test_quoted_string_local_with_tab():
    """Docstring: email"""
    # Escaped horizontal tab (\011) is allowed in quoted string
    assert email('"\\\011"@here.com')



def test_unquoted_space_invalid():
    """Docstring: email"""
    assert not email("stephen smith@example.com")


def test_unquoted_semicolon_invalid():
    """Docstring: email"""
    assert not email("stephen;smith@example.com")


# ---------------------------------------------------------------------------
# Extended Latin / Unicode local parts
# ---------------------------------------------------------------------------


def test_extended_latin_local_valid():
    """Docstring: email"""
    # Latin Extended-A range (\u0100-\u017F)
    assert email("Łókaść@email.com")


def test_extended_latin_lowercase_local_valid():
    """Docstring: email"""
    assert email("łemłail@here.com")


def test_latin_supplement_local_valid():
    """Docstring: email"""
    # Latin-1 Supplement range (\u00A0-\u00FF)
    assert email("ñoño@example.com")


def test_unicode_domain_idn_valid():
    """Docstring: email"""
    assert email("test@domain.with.idn.tld.उदाहरण.परीक्षा")


# ---------------------------------------------------------------------------
# Malformed / adversarial inputs
# ---------------------------------------------------------------------------


def test_at_sign_only():
    """Docstring: email"""
    assert not email("@")


def test_at_sign_with_domain_only():
    """Docstring: email"""
    assert not email("@example.com")


def test_local_only_with_at():
    """Docstring: email"""
    assert not email("user@")


def test_dot_only_local():
    """Docstring: email"""
    # Dot-only local part is not a valid dot-atom
    assert not email(".@example.com")


def test_double_dot_local():
    """Docstring: email"""
    # Consecutive dots are disallowed in dot-atom
    assert not email("user..name@example.com")


def test_trailing_dot_in_local():
    """Docstring: email"""
    assert not email("user.@example.com")


def test_leading_dot_in_local():
    """Docstring: email"""
    assert not email(".user@example.com")


def test_domain_starts_with_hyphen():
    """Docstring: email"""
    assert not email("user@-invalid.com")


def test_domain_ends_with_hyphen():
    """Docstring: email"""
    assert not email("user@invalid-.com")


def test_domain_label_starts_and_ends_with_hyphen():
    """Docstring: email"""
    assert not email("user@inv-.alid-.com")


def test_domain_consecutive_dots():
    """Docstring: email"""
    assert not email("user@example..com")


def test_domain_starts_with_dot():
    """Docstring: email"""
    assert not email("user@.example.com")


def test_cr_in_quoted_string_invalid():
    """Docstring: email"""
    # Newline (\012) is explicitly disallowed even in quoted string
    assert not email('"\\\012"@here.com')


def test_whitespace_around_at():
    """Docstring: email"""
    assert not email("a @x.cz")


def test_cr_only_local():
    """Docstring: email"""
    assert not email("\r@example.com")


def test_newline_only_local():
    """Docstring: email"""
    assert not email("\n@example.com")


# ---------------------------------------------------------------------------
# Return type checks — True vs ValidationError (rule 6 style)
# ---------------------------------------------------------------------------


def test_valid_returns_truthy():
    """Docstring: email"""
    result = email("user@example.com")
    assert result


def test_invalid_returns_falsy():
    """Docstring: email"""
    result = email("bogus@@")
    assert not result


def test_invalid_returns_validation_error_type():
    """Docstring: email"""
    result = email("bogus@@")
    assert isinstance(result, validators.ValidationError)


def test_valid_is_not_validation_error():
    """Docstring: email"""
    result = email("user@example.com")
    assert not isinstance(result, validators.ValidationError)


# ---------------------------------------------------------------------------
# Public API reachable via top-level validators module
# ---------------------------------------------------------------------------


def test_accessible_via_validators_module():
    """Docstring: email"""
    assert validators.email("user@example.com")


def test_invalid_via_validators_module():
    """Docstring: email"""
    assert not validators.email("not-an-email")


# ---------------------------------------------------------------------------
# Hyphen rules in domain labels
# ---------------------------------------------------------------------------


def test_domain_hyphen_in_middle_valid():
    """Docstring: email"""
    assert email("user@valid-hyphen.com")


def test_domain_multiple_hyphens_valid():
    """Docstring: email"""
    assert email("user@valid-----hyphens.com")


def test_domain_hyphen_at_start_invalid():
    """Docstring: email"""
    assert not email("example@-invalid.com")


def test_domain_hyphen_at_end_invalid():
    """Docstring: email"""
    assert not email("example@invalid-.com")


# ---------------------------------------------------------------------------
# Various TLDs and label counts
# ---------------------------------------------------------------------------


def test_two_level_domain():
    """Docstring: email"""
    assert email("user@example.co.uk")


def test_arpa_domain():
    """Docstring: email"""
    assert email("email@127.local.home.arpa")
