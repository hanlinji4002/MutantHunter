"""Broad regression tests for the url() validator."""

# standard
import pytest

# local
from validators import url


# ---------------------------------------------------------------------------
# Section 1: _validate_auth_segment – empty auth
# ---------------------------------------------------------------------------


def test_auth_empty_string_is_valid():
    """Docstring: url

    URL with @ but no auth component (empty before @) should be valid.
    The source: _validate_auth_segment returns True when value is empty.
    """
    assert url("http://@example.com")


# ---------------------------------------------------------------------------
# Section 1: _validate_auth_segment – colon_count == 0 (username only)
# ---------------------------------------------------------------------------


def test_auth_username_only_valid():
    """Docstring: url

    URL with only a username (no password) before the host should be valid.
    """
    assert url("http://userid@example.com")


def test_auth_username_only_no_at_valid():
    """Docstring: url

    URL with only a valid username embedded directly is valid.
    """
    assert url("http://alice@example.com/path")


def test_auth_username_alphanumeric_valid():
    """Docstring: url

    Alphanumeric-only username is a valid auth segment.
    """
    assert url("http://user123@example.com")


# ---------------------------------------------------------------------------
# Section 1: _validate_auth_segment – colon_count == 1 (username:password)
# ---------------------------------------------------------------------------


def test_auth_username_password_valid():
    """Docstring: url

    URL with username:password auth segment should be valid.
    """
    assert url("http://userid:password@example.com")


def test_auth_username_password_with_port_valid():
    """Docstring: url

    URL with username:password and explicit port is valid.
    """
    assert url("http://userid:password@example.com:8080")


def test_auth_password_contains_slash_invalid():
    """Docstring: url

    Password containing '/' is invalid per _validate_auth_segment.
    The chars /, ?, #, @ are explicitly forbidden in the password field.
    """
    assert not url("http://user:pass/word@example.com")


def test_auth_password_contains_question_mark_invalid():
    """Docstring: url

    Password containing '?' is invalid per _validate_auth_segment.
    """
    assert not url("http://user:pass?word@example.com")


def test_auth_password_contains_hash_invalid():
    """Docstring: url

    Password containing '#' is invalid per _validate_auth_segment.
    """
    assert not url("http://user:pass#word@example.com")


def test_auth_password_contains_at_invalid():
    """Docstring: url

    Password containing '@' would create a second '@' in netloc, which
    _validate_netloc rejects (count('@') > 1 → False).
    """
    assert not url("http://user:pass@word@example.com")


# ---------------------------------------------------------------------------
# Section 1: _validate_auth_segment – colon_count > 1 (multiple colons)
# ---------------------------------------------------------------------------


def test_auth_multiple_colons_treated_as_username_only():
    """Docstring: url

    When colon_count > 1 the entire pre-@ segment is treated as a username.
    The existing human test 'http://:::::::::::::@exmp.com' shows this is valid.
    """
    assert url("http://:::::::::::::@exmp.com")


def test_auth_multiple_colons_long_valid():
    """Docstring: url

    Multiple colons in auth (e.g. a:b:c) — colon_count > 1 path — valid
    when the whole segment matches the username regex.
    """
    assert url("http://-.~_!$&'()*+,;=:%40:80%2f::::::@example.com")


# ---------------------------------------------------------------------------
# Section 2: _validate_netloc – empty netloc
# ---------------------------------------------------------------------------


def test_netloc_empty_invalid():
    """Docstring: url

    A URL whose netloc is empty (http://) is invalid.
    _validate_netloc returns False for empty netloc.
    """
    assert not url("http://")


def test_netloc_empty_with_path_invalid():
    """Docstring: url

    A URL with empty netloc even when a path follows is invalid.
    """
    assert not url("http:///a")


# ---------------------------------------------------------------------------
# Section 2: _validate_netloc – more than one '@'
# ---------------------------------------------------------------------------


def test_netloc_two_at_signs_invalid():
    """Docstring: url

    More than one '@' in the netloc is explicitly rejected by _validate_netloc.
    """
    assert not url("http://a@b@example.com")


def test_netloc_three_at_signs_invalid():
    """Docstring: url

    Three '@' signs in netloc — still rejected.
    """
    assert not url("http://a@b@c@example.com")


# ---------------------------------------------------------------------------
# Section 2: _validate_netloc – exactly one '@'
# ---------------------------------------------------------------------------


def test_netloc_one_at_valid():
    """Docstring: url

    Exactly one '@' separates auth from host: valid.
    """
    assert url("http://user@host.com")


# ---------------------------------------------------------------------------
# Section 2: _validate_netloc – IPv6 with port (]:: pattern)
# ---------------------------------------------------------------------------


def test_netloc_ipv6_with_port_valid():
    """Docstring: url

    IPv6 address with port in brackets followed by colon:port is valid.
    """
    assert url("http://[FEDC:BA98:7654:3210:FEDC:BA98:7654:3210]:80/index.html")


def test_netloc_ipv6_no_port_valid():
    """Docstring: url

    IPv6 address without port is valid.
    """
    assert url("http://[3ffe:2a00:100:7031::1]")


def test_netloc_ipv6_missing_bracket_invalid():
    """Docstring: url

    IPv6 address missing closing bracket is invalid.
    """
    assert not url("http://[2010:836B:4179::836B:4179")


def test_netloc_ipv6_not_bracketed_invalid():
    """Docstring: url

    Bare IPv6 address without brackets is invalid.
    """
    assert not url("http://2010:836B:4179::836B:4179")


# ---------------------------------------------------------------------------
# Section 3: _validate_optionals – empty path / query / fragment
# ---------------------------------------------------------------------------


def test_optionals_empty_path_valid():
    """Docstring: url

    URL with no path component (just host) is valid.
    """
    assert url("http://example.com")


def test_optionals_empty_query_valid():
    """Docstring: url

    URL with path but no query string is valid.
    """
    assert url("http://example.com/path")


def test_optionals_empty_fragment_valid():
    """Docstring: url

    URL with path and query but no fragment is valid.
    """
    assert url("http://example.com/path?key=val")


# ---------------------------------------------------------------------------
# Section 3: _validate_optionals – valid / invalid path chars
# ---------------------------------------------------------------------------


def test_optionals_path_with_allowed_chars_valid():
    """Docstring: url

    Path containing allowed characters per _path_regex is valid.
    """
    assert url("http://example.com/foo/bar-baz_qux.html")


def test_optionals_path_with_tilde_valid():
    """Docstring: url

    Tilde is listed in _path_regex allowed set; path with tilde is valid.
    """
    assert url("http://example.com/~user/profile")


def test_optionals_path_with_space_invalid():
    """Docstring: url

    A literal space in the URL fails at the whitespace check before splitting.
    """
    assert not url("http://example.com/path with space")


def test_optionals_path_with_encoded_space_valid():
    """Docstring: url

    A percent-encoded space (%20) in the path is valid.
    """
    assert url("http://foo.bar/?q=Test%20URL-encoded%20stuff")


def test_optionals_path_emoji_valid():
    """Docstring: url

    Emoji / pictograph character in path is allowed per _path_regex.
    """
    assert url("http://foo.bar/📍")


# ---------------------------------------------------------------------------
# Section 3: _validate_optionals – strict_query=True vs False
# ---------------------------------------------------------------------------


def test_optionals_strict_query_valid_kv_pair():
    """Docstring: url

    strict_query=True (default) accepts a well-formed key=value query.
    """
    assert url("https://www.example.com/foo/?key=value")


def test_optionals_strict_query_rejects_valueless_key():
    """Docstring: url

    strict_query=True (default) rejects a query key without a value.
    Confirmed by existing human tests: 'baz&inga=42&quux' is invalid.
    """
    assert not url("https://www.example.com/foo/?bar=baz&inga=42&quux")


def test_optionals_lenient_query_accepts_valueless_key():
    """Docstring: url

    strict_query=False should accept a query key without a '=value' part.
    """
    assert url("https://www.example.com/foo/?bar=baz&inga=42&quux", strict_query=False)


def test_optionals_strict_query_rejects_path_like_query():
    """Docstring: url

    strict_query=True rejects a query that looks like a path segment.
    """
    assert not url("https://foo.bar.net/baz.php?-/inga/test-lenient-query/")


def test_optionals_lenient_query_accepts_path_like():
    """Docstring: url

    strict_query=False accepts a query that looks like a path segment.
    """
    assert url("https://foo.bar.net/baz.php?-/inga/test-lenient-query/", strict_query=False)


def test_optionals_strict_query_rejects_numeric_query():
    """Docstring: url

    strict_query=True rejects a bare numeric query string.
    """
    assert not url("https://foo.com/img/bar/baz.jpg?-62169987208")


def test_optionals_lenient_query_accepts_numeric_query():
    """Docstring: url

    strict_query=False accepts a bare numeric query string.
    """
    assert url("https://foo.com/img/bar/baz.jpg?-62169987208", strict_query=False)


# ---------------------------------------------------------------------------
# Section 3: _validate_optionals – fragment allowed chars (RFC 3986 §3.5)
# ---------------------------------------------------------------------------


def test_optionals_fragment_alphanumeric_valid():
    """Docstring: url

    Alphanumeric fragment is valid per RFC 3986 §3.5.
    """
    assert url("http://example.com/page#section1")


def test_optionals_fragment_with_slash_and_query_chars_valid():
    """Docstring: url

    Fragment may contain '/', '?', and '=' per RFC 3986 §3.5.
    """
    assert url("http://code.google.com/events/#&product=browser")


def test_optionals_fragment_with_hash_valid():
    """Docstring: url

    Fragment may contain '#' per the explicit comment in the source code.
    """
    assert url("https://exchange.jetswap.finance/#/swap")


def test_optionals_fragment_encoded_space_valid():
    """Docstring: url

    Fragment with percent-encoded characters is valid.
    """
    assert url("https://example.org/path#2022%201040%20(Cornelius%20Morgan%20G).pdf")


def test_optionals_fragment_control_char_invalid():
    """Docstring: url

    A fragment containing a literal control character (space) is invalid
    because the url() function rejects any URL with whitespace first.
    """
    assert not url("http://example.com/page#sec tion")


# ---------------------------------------------------------------------------
# Section 4: main url() – all valid schemes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "scheme",
    ["ftp", "ftps", "git", "http", "https", "irc", "rtmp", "rtmps", "rtsp", "sftp", "ssh", "telnet"],
)
def test_valid_schemes(scheme):
    """Docstring: url

    All schemes listed in _validate_scheme should be accepted.
    """
    assert url(f"{scheme}://example.com")


# ---------------------------------------------------------------------------
# Section 4: main url() – invalid scheme
# ---------------------------------------------------------------------------


def test_invalid_scheme_htp():
    """Docstring: url

    'htp' is not a valid scheme and must be rejected.
    """
    assert not url("htp://foobar.com")


def test_invalid_scheme_rdar():
    """Docstring: url

    'rdar' is not a listed scheme and must be rejected.
    """
    assert not url("rdar://1234")


def test_invalid_scheme_no_scheme():
    """Docstring: url

    URL without a scheme is invalid.
    """
    assert not url("foobar.dk")


def test_invalid_scheme_custom_rejected_by_default():
    """Docstring: url

    A custom scheme not in the default set is rejected.
    """
    assert not url("myscheme://example.com")


def test_invalid_scheme_empty():
    """Docstring: url

    A URL that starts with '//' has no scheme and must be invalid.
    """
    assert not url("//example.com")


# ---------------------------------------------------------------------------
# Section 4: main url() – whitespace in URL
# ---------------------------------------------------------------------------


def test_whitespace_space_invalid():
    """Docstring: url

    URL with a literal space is rejected immediately (re.search r'\\s').
    """
    assert not url("http://foo.bar/foo(bar)baz quux")


def test_whitespace_space_in_host_invalid():
    """Docstring: url

    URL with a space before the host is rejected.
    """
    assert not url("http:// shouldfail.com")


def test_whitespace_tab_invalid():
    """Docstring: url

    URL with a tab character is rejected by the whitespace check.
    """
    assert not url("http://example.com/path\ttab")


def test_whitespace_newline_invalid():
    """Docstring: url

    URL with a newline character is rejected by the whitespace check.
    """
    assert not url("http://example.com/path\nnewline")


# ---------------------------------------------------------------------------
# Section 4: main url() – empty string
# ---------------------------------------------------------------------------


def test_empty_string_invalid():
    """Docstring: url

    Empty string must be rejected (first check in url()).
    """
    assert not url("")


# ---------------------------------------------------------------------------
# Section 4: main url() – docstring examples
# ---------------------------------------------------------------------------


def test_docstring_example_http_duck():
    """Docstring: url

    Docstring example: url('http://duck.com') returns True.
    """
    assert url("http://duck.com")


def test_docstring_example_ftp_foobar():
    """Docstring: url

    Docstring example: url('ftp://foobar.dk') returns True.
    """
    assert url("ftp://foobar.dk")


def test_docstring_example_private_ip():
    """Docstring: url

    Docstring example: url('http://10.0.0.1') returns True.
    """
    assert url("http://10.0.0.1")


def test_docstring_example_xss_invalid():
    """Docstring: url

    Docstring example: url with injected user@example.com is invalid.
    """
    assert not url('http://example.com/">user@example.com')


# ---------------------------------------------------------------------------
# Section 4: main url() – URL with all optional parameters at once
# ---------------------------------------------------------------------------


def test_url_with_all_parts():
    """Docstring: url

    Full URL with scheme, auth, host, port, path, query, fragment all present.
    Corresponds to the diagram in the docstring.
    """
    assert url("http://admin:hunter1@example.com:8042/over/there?name=ferret#nose")


# ---------------------------------------------------------------------------
# Section 5: option – simple_host=True
# ---------------------------------------------------------------------------


def test_simple_host_localhost_valid():
    """Docstring: url

    simple_host=True allows single-label hosts like 'localhost'.
    """
    assert url("http://localhost", simple_host=True)


def test_simple_host_with_port_valid():
    """Docstring: url

    simple_host=True allows single-label host with port.
    """
    assert url("http://localhost:8000", simple_host=True)


def test_simple_host_single_label_valid():
    """Docstring: url

    simple_host=True allows arbitrary single-label hostnames.
    """
    assert url("http://myserver", simple_host=True)


def test_simple_host_false_rejects_localhost():
    """Docstring: url

    Without simple_host=True (default), single-label 'localhost' is rejected.
    """
    assert not url("http://localhost")


# ---------------------------------------------------------------------------
# Section 5: option – consider_tld=True
# ---------------------------------------------------------------------------


def test_consider_tld_valid_known_tld():
    """Docstring: url

    consider_tld=True accepts a domain with a known IANA TLD.
    """
    assert url("http://example.com", consider_tld=True)


def test_consider_tld_invalid_unknown_tld():
    """Docstring: url

    consider_tld=True rejects a domain whose TLD is not in the IANA list.
    """
    assert not url("http://example.invalidtld", consider_tld=True)


def test_consider_tld_false_accepts_unknown_tld():
    """Docstring: url

    consider_tld=False (default) does not enforce TLD validity.
    """
    assert url("http://example.localdomain")


# ---------------------------------------------------------------------------
# Section 5: option – rfc_1034=True (trailing dot allowed)
# ---------------------------------------------------------------------------


def test_rfc_1034_trailing_dot_valid():
    """Docstring: url

    rfc_1034=True allows a trailing dot in the domain name.
    """
    assert url("http://example.com.", rfc_1034=True)


def test_rfc_1034_false_trailing_dot_invalid():
    """Docstring: url

    Without rfc_1034=True (default), a trailing dot in domain is rejected.
    """
    assert not url("http://www.foo.bar./")


# ---------------------------------------------------------------------------
# Section 5: option – rfc_2782=True (service record / SRV)
# ---------------------------------------------------------------------------


def test_rfc_2782_srv_name_valid():
    """Docstring: url

    rfc_2782=True allows hostnames in SRV format (leading underscore label).
    """
    assert url("http://_http._tcp.example.com", rfc_2782=True)


# ---------------------------------------------------------------------------
# Section 5: option – skip_ipv6_addr=True
# ---------------------------------------------------------------------------


def test_skip_ipv6_false_ipv6_valid():
    """Docstring: url

    skip_ipv6_addr=False (default) allows IPv6 addresses in URLs.
    """
    assert url("http://[::FFFF:129.144.52.38]:80/index.html")


def test_skip_ipv6_true_rejects_ipv6():
    """Docstring: url

    skip_ipv6_addr=True causes IPv6 addresses to be rejected/skipped.
    The bracketed IPv6 address will not be validated as IPv6.
    """
    assert not url("http://[::FFFF:129.144.52.38]:80/index.html", skip_ipv6_addr=True)


# ---------------------------------------------------------------------------
# Section 5: option – skip_ipv4_addr=True
# ---------------------------------------------------------------------------


def test_skip_ipv4_false_ipv4_valid():
    """Docstring: url

    skip_ipv4_addr=False (default) allows IPv4 addresses in URLs.
    """
    assert url("http://142.42.1.1/")


def test_skip_ipv4_true_rejects_ipv4():
    """Docstring: url

    skip_ipv4_addr=True causes IPv4 addresses to be rejected.
    """
    assert not url("http://142.42.1.1/", skip_ipv4_addr=True)


# ---------------------------------------------------------------------------
# Section 5: option – private=True / private=False
# ---------------------------------------------------------------------------


def test_private_true_accepts_private_ip():
    """Docstring: url

    private=True accepts URLs with private/local IP addresses.
    """
    assert url("http://username:password@10.0.10.1/", private=True)


def test_private_true_accepts_loopback():
    """Docstring: url

    private=True accepts loopback address 127.0.0.1.
    """
    assert url("http://127.0.0.1", private=True)


def test_private_false_rejects_private_ip():
    """Docstring: url

    private=False rejects URLs with private/local IP addresses.
    """
    assert not url("http://username:password@192.168.10.10:4010", private=False)


def test_private_false_rejects_loopback():
    """Docstring: url

    private=False rejects loopback address.
    """
    assert not url("http://username:password@127.0.0.1:8080", private=False)


def test_private_none_accepts_any_ip():
    """Docstring: url

    private=None (default) does not restrict by IP visibility.
    """
    assert url("http://192.168.1.1")


# ---------------------------------------------------------------------------
# Section 5: option – may_have_port
# ---------------------------------------------------------------------------


def test_may_have_port_true_accepts_port():
    """Docstring: url

    may_have_port=True (default) allows a port number in the URL.
    """
    assert url("http://example.com:8080/path")


def test_may_have_port_false_rejects_port():
    """Docstring: url

    may_have_port=False should reject URLs that include a port number.
    """
    assert not url("http://example.com:8080/path", may_have_port=False)


# ---------------------------------------------------------------------------
# Section 5: option – validate_scheme (custom callable)
# ---------------------------------------------------------------------------


def test_custom_validate_scheme_accepts_custom():
    """Docstring: url

    A custom validate_scheme function allows non-default schemes.
    """
    assert url("myscheme://example.com", validate_scheme=lambda s: s == "myscheme")


def test_custom_validate_scheme_rejects_http():
    """Docstring: url

    A custom validate_scheme that rejects 'http' should fail for http URLs.
    """
    assert not url("http://example.com", validate_scheme=lambda s: s == "myscheme")


# ---------------------------------------------------------------------------
# Additional edge cases
# ---------------------------------------------------------------------------


def test_url_with_unicode_domain_valid():
    """Docstring: url

    Unicode domain names are valid.
    """
    assert url("http://مثال.إختبار")


def test_url_with_unicode_path_valid():
    """Docstring: url

    Unicode path characters are valid.
    """
    assert url("https://travel-usa.com/wisconsin/旅行/")


def test_url_xss_injection_invalid():
    """Docstring: url

    SQL/JS injection attempt in query string is invalid (';' triggers
    strict_query failure or host parsing failure).
    """
    assert not url("https://example.org?q=search');alert(document.domain);")


def test_url_ip_octet_too_large_invalid():
    """Docstring: url

    IPv4 octet value >255 is an invalid IP address.
    """
    assert not url("http://127.12.0.260")


def test_url_ip_three_octets_invalid():
    """Docstring: url

    IPv4 with only three octets (123.123.123) is not a valid IP address.
    """
    assert not url("http://123.123.123")


def test_url_double_dot_in_host_invalid():
    """Docstring: url

    Double dot in hostname (foobar..com) is invalid.
    """
    assert not url("http://foobar..com")


def test_url_leading_dot_in_host_invalid():
    """Docstring: url

    Leading dot in hostname (.www.foo.bar) is invalid.
    """
    assert not url("http://.www.foo.bar/")


def test_url_hostname_starts_with_hyphen_invalid():
    """Docstring: url

    Hostname starting with a hyphen (-a.b.co) is invalid.
    """
    assert not url("http://-a.b.co")


def test_url_hostname_ends_with_hyphen_invalid():
    """Docstring: url

    Hostname ending with a hyphen (a.b-.co) is invalid.
    """
    assert not url("http://a.b-.co")


def test_url_fragment_with_hash_in_path_valid():
    """Docstring: url

    URL with fragment containing path-like and query-like chars is valid.
    """
    assert url("https://www.foo.com/bar#/baz/test")


def test_url_complex_fragment_valid():
    """Docstring: url

    Complex matrix.to-style URL with fragment containing special chars is valid.
    """
    assert url(
        "https://matrix.to/#/!BSqRHgvCtIsGittkBG:talk.puri.sm/$1551464398"
        "853539kMJNP:matrix.org?via=talk.puri.sm&via=matrix.org&via=disroot.org"
    )


def test_url_null_string_invalid():
    """Docstring: url

    None-like empty string is invalid.
    """
    assert not url("")


def test_url_just_scheme_invalid():
    """Docstring: url

    URL with scheme but empty netloc (http://) is invalid.
    """
    assert not url("http://")


def test_url_short_tld_valid():
    """Docstring: url

    Two-letter TLD is valid (j.mp used in existing human tests).
    """
    assert url("http://j.mp")


def test_url_numeric_hostname_valid():
    """Docstring: url

    All-numeric hostname like 1337.net is valid.
    """
    assert url("http://1337.net")


def test_url_private_none_default_accepts_public_ip():
    """Docstring: url

    Default private=None accepts public IP addresses without restriction.
    """
    assert url("http://5.196.190.0/")
