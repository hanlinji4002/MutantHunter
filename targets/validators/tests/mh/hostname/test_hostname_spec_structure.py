"""Spec-driven tests for hostname structural rules.

Sources: RFC 952 §ASSUMPTIONS §GRAMMATICAL HOST TABLE SPECIFICATION and
         RFC 1123 §2.1
"""

from validators import hostname


def test_empty_string_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R13

    An empty string is not a valid hostname.
    """
    assert not hostname("")


def test_single_label_hostname_valid():
    """Spec: rfc952.pdf GRAMMATICAL HOST TABLE SPECIFICATION — R6a

    A single name component that satisfies RFC 952 grammar is a valid hostname.
    """
    assert hostname("myhost")


def test_multi_label_hostname_valid():
    """Spec: rfc952.pdf GRAMMATICAL HOST TABLE SPECIFICATION — R6b

    A host name may be composed of multiple dot-separated labels
    (<hname> ::= <name>*["."<name>]).
    """
    assert hostname("www.example.com")


def test_two_label_hostname_valid():
    """Spec: rfc952.pdf GRAMMATICAL HOST TABLE SPECIFICATION — R6b

    A two-label hostname (e.g., example.com) is valid.
    """
    assert hostname("example.com")


def test_label_period_only_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R2

    A period is only allowed when delimiting domain-style name components.
    A standalone period is not a valid hostname.
    """
    assert not hostname(".")


def test_hostname_with_leading_period_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R2

    Periods are only allowed when they delimit name components. A leading
    period does not delimit two valid labels and is invalid.
    """
    assert not hostname(".example")


def test_hostname_with_trailing_period_simple_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R6

    The last character must not be a period (applied to simple/single-label
    names without rfc_1034 trailing-dot allowance).
    """
    assert not hostname("example.")


def test_hostname_multilabel_with_digit_start_label_valid():
    """Spec: rfc1123.pdf Section 2.1 — R7

    RFC 1123 allows labels to start with a digit. A multi-label hostname
    where one label begins with a digit must be accepted.
    """
    assert hostname("3com.example.com")


def test_hostname_multilabel_hyphen_in_interior_valid():
    """Spec: rfc952.pdf ASSUMPTIONS — R6a, R6b

    Interior hyphens are valid in any label of a multi-label hostname.
    """
    assert hostname("my-host.example.com")


def test_hostname_with_port_valid():
    """Spec: rfc1123.pdf Section 2.1 — R7

    A simple hostname with a port (as accepted by the validator's
    may_have_port=True default) should be valid when the host part
    is a valid label.
    """
    assert hostname("myhost:8080")


def test_hostname_with_invalid_port_invalid():
    """Spec: rfc1123.pdf Section 2.1 — R8

    Port numbers above 65535 are out of range; the hostname validator
    must reject such values when may_have_port is True.
    """
    assert not hostname("myhost:99999")


def test_hostname_consecutive_dots_invalid():
    """Spec: rfc952.pdf GRAMMATICAL HOST TABLE SPECIFICATION — R6b

    Consecutive periods produce empty labels which are not valid name
    components per the grammar.
    """
    assert not hostname("example..com")


def test_hostname_numeric_all_labels_valid():
    """Spec: rfc1123.pdf Section 2.1 — R19

    Under RFC 1123 §2.1, a label may begin with a digit, so an
    all-numeric single label is a valid simple hostname (not a domain name,
    but a simple-hostname match).
    """
    assert hostname("123")


def test_hostname_skip_ipv4_forces_non_ipv4():
    """Spec: rfc1123.pdf Section 2.1 — R7

    When skip_ipv4_addr=True, IP-address-like strings must be validated only
    as domain names or simple hostnames, not as IPv4. An all-numeric dotted
    quad is not a valid domain name and must be rejected.
    """
    assert not hostname("192.168.1.1", skip_ipv4_addr=True, maybe_simple=False)


def test_hostname_single_label_no_tld_not_forced():
    """Spec: rfc952.pdf ASSUMPTIONS — R6a

    A single-label hostname that satisfies the grammar (starts with
    alphanumeric, no trailing hyphen) is valid regardless of whether
    it is a recognised TLD, because maybe_simple=True (default).
    """
    assert hostname("localhost")
