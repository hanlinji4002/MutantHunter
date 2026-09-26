"""Broad regression tests for the hostname validator."""

# local
from validators import hostname


# ---------------------------------------------------------------------------
# Docstring examples — must match exactly
# ---------------------------------------------------------------------------


def test_docstring_ubuntu_pc_port_443():
    """Docstring: hostname"""
    assert hostname("ubuntu-pc:443")


def test_docstring_this_pc():
    """Docstring: hostname"""
    assert hostname("this-pc")


def test_docstring_punycode_with_max_port():
    """Docstring: hostname"""
    assert hostname("xn----gtbspbbmkef.xn--p1ai:65535")


def test_docstring_underscore_example_com_invalid():
    """Docstring: hostname"""
    assert not hostname("_example.com")


def test_docstring_ipv4_with_port():
    """Docstring: hostname"""
    assert hostname("123.5.77.88:31000")


def test_docstring_plain_ipv4():
    """Docstring: hostname"""
    assert hostname("12.12.12.12")


def test_docstring_ipv6_loopback_with_port():
    """Docstring: hostname"""
    assert hostname("[::1]:22")


def test_docstring_ipv6_full_no_port():
    """Docstring: hostname"""
    assert hostname("dead:beef:0:0:0:0000:42:1")


def test_docstring_ipv6_negative_port_invalid():
    """Docstring: hostname"""
    assert not hostname("[0:0:0:0:0:ffff:1.2.3.4]:-65538")


def test_docstring_ipv6_bad_chars_invalid():
    """Docstring: hostname"""
    assert not hostname("[0:&:b:c:@:e:f::]:9999")


# ---------------------------------------------------------------------------
# Empty / None input
# ---------------------------------------------------------------------------


def test_empty_string_invalid():
    """Characterization: empty string is rejected (explicit early return)"""
    assert not hostname("")


# ---------------------------------------------------------------------------
# Simple hostname — valid
# ---------------------------------------------------------------------------


def test_simple_single_char():
    """Characterization: single alphanum char is the shortest valid simple hostname"""
    assert hostname("a")


def test_simple_single_digit():
    """Characterization: single digit is a valid simple hostname"""
    assert hostname("9")


def test_simple_alphanums_no_hyphen():
    """Characterization: alphanums-only simple hostname"""
    assert hostname("localhost")


def test_simple_with_hyphen_middle():
    """Characterization: hyphen in middle is allowed"""
    assert hostname("my-host")


def test_simple_with_port():
    """Docstring: hostname"""
    assert hostname("ubuntu-pc:443")


def test_simple_61_chars():
    """Characterization: 61-char simple hostname is the longest allowed by regex"""
    # regex middle part {0,59} + first + last = 61 total
    value = "a" + "b" * 59 + "c"  # 61 chars
    assert hostname(value)


def test_simple_1_char_is_valid():
    """Characterization: 1-char hostname — start/end are the same character (group is optional)"""
    assert hostname("z")


def test_simple_case_insensitive_upper():
    """Characterization: simple hostname regex is case-insensitive"""
    assert hostname("MYHOST")


def test_simple_case_insensitive_mixed():
    """Characterization: mixed-case simple hostname"""
    assert hostname("MyHost")


def test_simple_starts_with_digit():
    """Characterization: hostname starting with digit is valid"""
    assert hostname("4-oh-4")


def test_simple_lab_notebook_with_port():
    """Characterization: alphanumeric with hyphen and port"""
    assert hostname("lab-01a-notebook:404")


# ---------------------------------------------------------------------------
# Simple hostname — invalid
# ---------------------------------------------------------------------------


def test_simple_starts_with_hyphen_invalid():
    """Characterization: leading hyphen is forbidden by simple hostname regex"""
    assert not hostname("-bad")


def test_simple_ends_with_hyphen_invalid():
    """Characterization: trailing hyphen is forbidden by simple hostname regex"""
    assert not hostname("bad-")


def test_simple_special_char_invalid():
    """Characterization: special character makes hostname invalid"""
    assert not hostname("this-pc-is-sh*t")


# test_simple_62_chars_invalid removed — asserted current (buggy) behavior.
# Spec says 62-char label is valid (R8, rfc1123.pdf §2.1). See suspected_bugs/hostname.md.


def test_simple_only_hyphens_invalid():
    """Characterization: all-hyphen string is not a valid simple hostname"""
    assert not hostname("---")


def test_simple_with_space_invalid():
    """Characterization: internal space is not allowed"""
    assert not hostname("my host")


# ---------------------------------------------------------------------------
# maybe_simple=False
# ---------------------------------------------------------------------------


def test_maybe_simple_false_plain_label_invalid():
    """Docstring: hostname — maybe_simple kwarg"""
    assert not hostname("localhost", maybe_simple=False)


def test_maybe_simple_false_domain_still_valid():
    """Docstring: hostname — maybe_simple kwarg does not affect domain validation"""
    assert hostname("example.com", maybe_simple=False)


def test_maybe_simple_false_ipv4_still_valid():
    """Characterization: maybe_simple=False still accepts plain IPv4"""
    assert hostname("192.168.1.1", maybe_simple=False)


def test_maybe_simple_false_ipv6_still_valid():
    """Characterization: maybe_simple=False still accepts bare IPv6"""
    assert hostname("::1", maybe_simple=False)


def test_maybe_simple_false_with_port_label_invalid():
    """Characterization: maybe_simple=False rejects simple-hostname:port"""
    assert not hostname("myhost:8080", maybe_simple=False)


# ---------------------------------------------------------------------------
# Domain names — valid
# ---------------------------------------------------------------------------


def test_domain_plain():
    """Characterization: standard two-label domain"""
    assert hostname("example.com")


def test_domain_with_port():
    """Characterization: domain with port"""
    assert hostname("example.com:4444")


def test_domain_three_labels():
    """Characterization: three-label domain"""
    assert hostname("sub.example.com")


def test_domain_punycode():
    """Characterization: punycode-encoded IDN domain"""
    assert hostname("xn----gtbspbbmkef.xn--p1ai")


def test_domain_idn_umlaut():
    """Characterization: IDN domain with umlaut"""
    assert hostname("kräuter.com")


def test_domain_numeric_subdomain():
    """Characterization: numeric subdomain label is valid"""
    assert hostname("123.example.com")


# ---------------------------------------------------------------------------
# Domain names — invalid
# ---------------------------------------------------------------------------


def test_domain_trailing_slash_invalid():
    """Characterization: trailing slash is not valid in a hostname"""
    assert not hostname("example.com/")


def test_domain_leading_dot_invalid():
    """Characterization: leading dot produces invalid domain"""
    assert not hostname(".example.com")


def test_domain_double_dot_invalid():
    """Characterization: consecutive dots are invalid in a domain"""
    assert not hostname("example..com")


def test_domain_label_too_long_invalid():
    """Characterization: a domain label exceeding 63 chars is invalid"""
    long_label = "a" * 64
    assert not hostname(f"{long_label}.com")


# ---------------------------------------------------------------------------
# rfc_1034 — trailing dot
# ---------------------------------------------------------------------------


def test_rfc_1034_trailing_dot_domain():
    """Docstring: hostname — rfc_1034 allows trailing dot"""
    assert hostname("kräuter.com.", rfc_1034=True)


def test_rfc_1034_false_trailing_dot_domain_invalid():
    """Characterization: without rfc_1034, trailing dot is rejected"""
    assert not hostname("example.com.")


def test_rfc_1034_simple_hostname_no_trailing_dot():
    """Characterization: rfc_1034 does not affect simple hostname (no dot involved)"""
    assert hostname("myhost", rfc_1034=True)


# ---------------------------------------------------------------------------
# rfc_2782 — service record (underscore prefix)
# ---------------------------------------------------------------------------


def test_rfc_2782_underscore_prefix_domain():
    """Docstring: hostname — rfc_2782 allows leading underscore"""
    assert hostname("_example.com", rfc_2782=True)


def test_rfc_2782_false_underscore_prefix_invalid():
    """Docstring: hostname — without rfc_2782 underscore prefix is invalid"""
    assert not hostname("_example.com")


def test_rfc_2782_underscore_subdomain():
    """Characterization: rfc_2782 allows underscore in sub-label"""
    assert hostname("_tcp.example.com", rfc_2782=True)


# ---------------------------------------------------------------------------
# consider_tld — IANA TLD enforcement
# ---------------------------------------------------------------------------


def test_consider_tld_valid_com():
    """Characterization: .com is a valid IANA TLD"""
    assert hostname("example.com", consider_tld=True)


def test_consider_tld_valid_org():
    """Characterization: .org is a valid IANA TLD"""
    assert hostname("example.org", consider_tld=True)


def test_consider_tld_invalid_fake_tld():
    """Characterization: .invalid is not an IANA TLD"""
    assert not hostname("example.invalid", consider_tld=True)


def test_consider_tld_false_accepts_fake_tld():
    """Characterization: consider_tld=False (default) does not check IANA list"""
    assert hostname("example.invalid", consider_tld=False)


# ---------------------------------------------------------------------------
# IPv4 addresses — valid
# ---------------------------------------------------------------------------


def test_ipv4_plain():
    """Docstring: hostname"""
    assert hostname("12.12.12.12")


def test_ipv4_loopback():
    """Characterization: loopback IPv4 is a valid hostname"""
    assert hostname("127.0.0.1")


def test_ipv4_broadcast():
    """Characterization: broadcast address is a valid hostname"""
    assert hostname("255.255.255.255")


def test_ipv4_with_port_valid():
    """Docstring: hostname"""
    assert hostname("123.5.77.88:31000")


def test_ipv4_port_max_65535():
    """Characterization: port 65535 is the maximum allowed"""
    assert hostname("1.2.3.4:65535")


def test_ipv4_port_min_1():
    """Characterization: port 1 is the minimum allowed"""
    assert hostname("1.2.3.4:1")


# ---------------------------------------------------------------------------
# IPv4 addresses — invalid
# ---------------------------------------------------------------------------


def test_ipv4_out_of_range_octet():
    """Characterization: octet value > 255 is not valid"""
    assert not hostname("256.1.1.1")


def test_ipv4_port_too_large():
    """Characterization: port > 65535 is rejected"""
    assert not hostname("1.2.3.4:65536")


def test_ipv4_port_zero_invalid():
    """Characterization: port 0 is outside the allowed range (1–65535)"""
    assert not hostname("1.2.3.4:0")


def test_ipv4_port_negative_invalid():
    """Characterization: negative port number is rejected"""
    assert not hostname("1.2.3.4:-80")


def test_ipv4_port_empty_invalid():
    """Characterization: trailing colon with no port digits is rejected"""
    assert not hostname("127.0.0.1:")


def test_ipv4_negative_octet_invalid():
    """Characterization: negative octet value is not valid"""
    assert not hostname("123.5.-12.88:8080")


def test_ipv4_port_non_numeric_invalid():
    """Characterization: non-numeric port is rejected"""
    assert not hostname("12.12.12.12:$#")


# ---------------------------------------------------------------------------
# skip_ipv4_addr
# ---------------------------------------------------------------------------


def test_skip_ipv4_plain_ipv4_invalid():
    """Docstring: hostname — skip_ipv4_addr rejects IPv4 strings"""
    assert not hostname("192.168.1.1", skip_ipv4_addr=True)


def test_skip_ipv4_domain_still_valid():
    """Characterization: skip_ipv4_addr does not affect domain validation"""
    assert hostname("example.com", skip_ipv4_addr=True)


def test_skip_ipv4_simple_host_still_valid():
    """Characterization: skip_ipv4_addr does not affect simple hostname"""
    assert hostname("myhost", skip_ipv4_addr=True)


def test_skip_ipv4_false_ipv4_valid():
    """Characterization: skip_ipv4_addr=False (default) accepts IPv4"""
    assert hostname("10.0.0.1", skip_ipv4_addr=False)


def test_skip_ipv4_with_port_ipv4_invalid():
    """Characterization: skip_ipv4_addr also blocks IPv4:port combos"""
    assert not hostname("192.168.1.1:8080", skip_ipv4_addr=True)


# ---------------------------------------------------------------------------
# IPv6 addresses — valid
# ---------------------------------------------------------------------------


def test_ipv6_loopback_with_port():
    """Docstring: hostname"""
    assert hostname("[::1]:22")


def test_ipv6_full_no_brackets():
    """Docstring: hostname"""
    assert hostname("dead:beef:0:0:0:0000:42:1")


def test_ipv6_ipv4_mapped_with_port():
    """Characterization: IPv4-mapped IPv6 with port"""
    assert hostname("[0:0:0:0:0:ffff:1.2.3.4]:80")


def test_ipv6_abbreviated_with_port():
    """Characterization: abbreviated IPv6 with port"""
    assert hostname("[0:a:b:c:d:e:f::]:53")


def test_ipv6_loopback_bare():
    """Characterization: bare ::1 without brackets is a valid IPv6 hostname"""
    assert hostname("::1")


def test_ipv6_full_expanded():
    """Characterization: fully expanded IPv6 address"""
    assert hostname("2001:0db8:85a3:0000:0000:8a2e:0370:7334")


def test_ipv6_port_max_65535():
    """Characterization: IPv6 with maximum port 65535"""
    assert hostname("[::1]:65535")


def test_ipv6_port_min_1():
    """Characterization: IPv6 with minimum port 1"""
    assert hostname("[::1]:1")


# ---------------------------------------------------------------------------
# IPv6 addresses — invalid
# ---------------------------------------------------------------------------


def test_ipv6_port_too_large_invalid():
    """Characterization: port > 65535 with IPv6 is rejected"""
    assert not hostname("[::1]:65536")


def test_ipv6_port_zero_invalid():
    """Characterization: port 0 with IPv6 is rejected (below minimum)"""
    assert not hostname("[::1]:0")


def test_ipv6_port_negative_invalid():
    """Docstring: hostname"""
    assert not hostname("[0:0:0:0:0:ffff:1.2.3.4]:-65538")


def test_ipv6_port_in_brackets_invalid():
    """Characterization: port inside brackets is not a valid port syntax"""
    assert not hostname("[::1]:[22]")


def test_ipv6_bad_chars_invalid():
    """Docstring: hostname"""
    assert not hostname("[0:&:b:c:@:e:f::]:9999")


def test_ipv6_too_many_groups_invalid():
    """Characterization: IPv6 with bad groups is rejected"""
    assert not hostname("[dead:beef:0:-:0:-:42:1]:5731")


def test_ipv6_missing_closing_bracket_invalid():
    """Characterization: unclosed bracket is invalid"""
    assert not hostname("[0:&:b:c:@:e:f:::9999")


# ---------------------------------------------------------------------------
# skip_ipv6_addr
# ---------------------------------------------------------------------------


def test_skip_ipv6_bare_ipv6_invalid():
    """Docstring: hostname — skip_ipv6_addr rejects IPv6 strings"""
    assert not hostname("::1", skip_ipv6_addr=True)


def test_skip_ipv6_bracketed_with_port_invalid():
    """Characterization: skip_ipv6_addr blocks [ipv6]:port form"""
    assert not hostname("[::1]:22", skip_ipv6_addr=True)


def test_skip_ipv6_domain_still_valid():
    """Characterization: skip_ipv6_addr does not affect domain validation"""
    assert hostname("example.com", skip_ipv6_addr=True)


def test_skip_ipv6_ipv4_still_valid():
    """Characterization: skip_ipv6_addr does not affect IPv4 validation"""
    assert hostname("1.2.3.4", skip_ipv6_addr=True)


def test_skip_ipv6_false_ipv6_valid():
    """Characterization: skip_ipv6_addr=False (default) accepts IPv6"""
    assert hostname("::1", skip_ipv6_addr=False)


# ---------------------------------------------------------------------------
# may_have_port=False
# ---------------------------------------------------------------------------


def test_may_have_port_false_plain_host_valid():
    """Docstring: hostname — may_have_port=False still allows plain hosts"""
    assert hostname("myhost", may_have_port=False)


def test_may_have_port_false_host_with_port_bypasses_port_check():
    """Characterization: may_have_port=False skips port parsing; value treated as-is"""
    # "ubuntu-pc:443" without port checking: not a valid domain, not a valid IPv4/IPv6,
    # but simple hostname regex won't match because ':' is not alphanumeric.
    assert not hostname("ubuntu-pc:443", may_have_port=False)


def test_may_have_port_false_domain_valid():
    """Characterization: domain without port is still valid when may_have_port=False"""
    assert hostname("example.com", may_have_port=False)


def test_may_have_port_false_ipv4_valid():
    """Characterization: plain IPv4 without port is valid when may_have_port=False"""
    assert hostname("1.2.3.4", may_have_port=False)


def test_may_have_port_false_ipv4_with_port_invalid():
    """Characterization: IPv4:port bypasses port validator and becomes invalid"""
    assert not hostname("1.2.3.4:80", may_have_port=False)


# ---------------------------------------------------------------------------
# private parameter (IP address scope)
# ---------------------------------------------------------------------------


def test_private_true_private_ip_valid():
    """Characterization: private=True accepts a private IP"""
    assert hostname("192.168.1.1", private=True)


def test_private_true_public_ip_invalid():
    """Characterization: private=True rejects a public IP"""
    assert not hostname("8.8.8.8", private=True)


def test_private_false_public_ip_valid():
    """Characterization: private=False accepts a public IP"""
    assert hostname("8.8.8.8", private=False)


def test_private_false_private_ip_invalid():
    """Characterization: private=False rejects a private IP"""
    assert not hostname("192.168.1.1", private=False)


def test_private_none_any_ip_valid():
    """Characterization: private=None (default) accepts both public and private IPs"""
    assert hostname("8.8.8.8", private=None)
    assert hostname("192.168.1.1", private=None)


def test_private_true_loopback_valid():
    """Characterization: loopback (127.x) is in the private/local range"""
    assert hostname("127.0.0.1", private=True)


def test_private_false_loopback_invalid():
    """Characterization: loopback is not public — private=False rejects it"""
    assert not hostname("127.0.0.1", private=False)


# ---------------------------------------------------------------------------
# Port boundary values
# ---------------------------------------------------------------------------


def test_port_boundary_1_valid():
    """Characterization: port 1 is within the valid range"""
    assert hostname("myhost:1")


def test_port_boundary_65535_valid():
    """Characterization: port 65535 is the maximum in the valid range"""
    assert hostname("myhost:65535")


def test_port_boundary_0_invalid():
    """Characterization: port 0 is below the minimum allowed (1)"""
    assert not hostname("myhost:0")


def test_port_boundary_65536_invalid():
    """Characterization: port 65536 exceeds the maximum allowed (65535)"""
    assert not hostname("myhost:65536")


def test_port_boundary_99999_invalid():
    """Characterization: five-digit port well above maximum is rejected"""
    assert not hostname("123.123.123.123:99999")


def test_port_boundary_443080_invalid():
    """Characterization: six-digit port is far out of range"""
    assert not hostname("ubuntu-pc:443080")


# ---------------------------------------------------------------------------
# Combination: skip_ipv4_addr + skip_ipv6_addr
# ---------------------------------------------------------------------------


def test_skip_both_ip_domain_valid():
    """Characterization: when both IP types are skipped, domain still works"""
    assert hostname("example.com", skip_ipv4_addr=True, skip_ipv6_addr=True)


def test_skip_both_ip_ipv4_invalid():
    """Characterization: both IPs skipped — IPv4 is rejected"""
    assert not hostname("1.2.3.4", skip_ipv4_addr=True, skip_ipv6_addr=True)


def test_skip_both_ip_ipv6_invalid():
    """Characterization: both IPs skipped — IPv6 is rejected"""
    assert not hostname("::1", skip_ipv4_addr=True, skip_ipv6_addr=True)


def test_skip_both_ip_simple_host_valid():
    """Characterization: both IPs skipped — simple hostname still accepted"""
    assert hostname("myhost", skip_ipv4_addr=True, skip_ipv6_addr=True)


# ---------------------------------------------------------------------------
# Combination: rfc_1034 + rfc_2782
# ---------------------------------------------------------------------------


def test_rfc_1034_and_2782_underscore_with_trailing_dot():
    """Characterization: underscore prefix + trailing dot allowed when both flags set"""
    assert hostname("_example.com.", rfc_1034=True, rfc_2782=True)


def test_rfc_2782_underscore_port_zero_invalid():
    """Characterization: rfc_2782 host with port 0 is still rejected"""
    assert not hostname("_example.com:0", rfc_2782=True)


# ---------------------------------------------------------------------------
# Whitespace / surrounding space
# ---------------------------------------------------------------------------


def test_leading_space_invalid():
    """Characterization: leading whitespace is not stripped — value is invalid"""
    assert not hostname(" example.com")


def test_trailing_space_invalid():
    """Characterization: trailing whitespace is not stripped — value is invalid"""
    assert not hostname("example.com ")


def test_internal_space_invalid():
    """Characterization: internal space is not valid"""
    assert not hostname("exam ple.com")


# ---------------------------------------------------------------------------
# Miscellaneous edge cases
# ---------------------------------------------------------------------------


def test_at_sign_in_value_invalid():
    """Characterization: '@' symbol is not valid in a hostname"""
    assert not hostname("4-oh-4:@.com")


def test_port_with_bad_suffix_invalid():
    """Characterization: port-like suffix with underscore is rejected"""
    assert not hostname("kräuter.com.:81_00", rfc_1034=True)


def test_domain_with_bad_subcomponent_invalid():
    """Characterization: underscore in label without rfc_2782 is rejected"""
    assert not hostname("lab-01a-note._com_.com:404")
