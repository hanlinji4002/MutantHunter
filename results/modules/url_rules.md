# URL / URI Rules — Extracted from RFC 3986

**Source:** RFC 3986, "Uniform Resource Identifier (URI): Generic Syntax", January 2005  
**Validator under test:** `validators.url`

---

## R1 — URI overall structure
**§3 / Appendix A**  
A URI has the form: `scheme ":" hier-part [ "?" query ] [ "#" fragment ]`  
Both `scheme` and `path` (possibly empty) are required; `query` and `fragment` are optional.

## R2 — Scheme must start with ALPHA
**§3.1**  
`scheme = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )`  
The first character MUST be a letter (A–Z, a–z). A scheme beginning with a digit, `+`, `-`, `.`, or any other non-alpha character is invalid.

## R3 — Scheme subsequent characters
**§3.1**  
After the first alpha, a scheme may contain letters, digits, `+`, `-`, and `.` only.  
Example valid: `http`, `ftp`, `my+scheme`, `s3.4`, `a-b`.

## R4 — Scheme is case-insensitive
**§3.1 / §6.2.2.1**  
Scheme names are case-insensitive. An implementation SHOULD accept `HTTP` as equivalent to `http`.

## R5 — Authority is introduced by "//"
**§3.2**  
When an authority component is present it is preceded by `//` and terminated by the next `/`, `?`, `#`, or end of URI.

## R6 — Authority structure
**§3.2 / Appendix A**  
`authority = [ userinfo "@" ] host [ ":" port ]`  
All three sub-components are optional; a bare host is the minimum.

## R7 — Userinfo characters
**§3.2.1 / Appendix A**  
`userinfo = *( unreserved / pct-encoded / sub-delims / ":" )`  
Colons (`:`) are explicitly allowed inside userinfo (though the `user:password` form is deprecated).

## R8 — Userinfo delimiter
**§3.2.1**  
Userinfo, when present, is separated from the host by `@`. Only one `@` is permitted in the authority.

## R9 — Host forms
**§3.2.2 / Appendix A**  
`host = IP-literal / IPv4address / reg-name`  
An IP-literal is enclosed in `[ ]`; IPv4 is dotted-decimal; reg-name is a registered name (domain).

## R10 — IP-literal uses square brackets
**§3.2.2**  
`IP-literal = "[" ( IPv6address / IPvFuture ) "]"`  
Square brackets are only allowed in the host component for IP literals. An IPv6 address without enclosing brackets is not valid as a host.

## R11 — IPv4 address range
**§3.2.2 / Appendix A**  
Each decimal octet in an IPv4 address must be in the range 0–255.  
`dec-octet = DIGIT / %x31-39 DIGIT / "1" 2DIGIT / "2" %x30-34 DIGIT / "25" %x30-35`  
Values like `256`, `999`, or `.` in place of an octet are invalid.

## R12 — IPv4 requires exactly four octets
**§3.2.2**  
An IPv4 address consists of exactly four decimal octets separated by `.`.  
Three-octet or five-octet strings are not valid IPv4 literals.

## R13 — reg-name characters
**§3.2.2 / Appendix A**  
`reg-name = *( unreserved / pct-encoded / sub-delims )`  
Registered names may be empty (zero length).

## R14 — Port is zero or more digits
**§3.2.3 / Appendix A**  
`port = *DIGIT`  
An empty port (i.e., `host:` with nothing after the colon) is syntactically valid.

## R15 — Port digits only
**§3.2.3**  
The port sub-component contains ONLY decimal digits. Letters or symbols in the port field are invalid.

## R16 — Path-abempty when authority is present
**§3.3**  
When the URI contains an authority component, the path must either be empty or begin with `/`.  
A path starting with `//` when authority is present is also disallowed at the structural level.

## R17 — pchar definition
**§3.3 / Appendix A**  
`pchar = unreserved / pct-encoded / sub-delims / ":" / "@"`  
These are the characters allowed within a single path segment.

## R18 — Path segment characters
**§3.3**  
Each path segment is `*pchar`. Path characters include unreserved chars, percent-encoded octets, sub-delimiters (`! $ & ' ( ) * + , ; =`), `:`, and `@`.

## R19 — Query characters
**§3.4 / Appendix A**  
`query = *( pchar / "/" / "?" )`  
In addition to pchar, `/` and `?` are allowed in query strings.

## R20 — Query delimiter
**§3.4**  
The query component begins at the first `?` and ends at `#` or end of URI.

## R21 — Fragment characters
**§3.5 / Appendix A**  
`fragment = *( pchar / "/" / "?" )`  
Same character set as query. The `#` character itself introduces the fragment but is not part of it.

## R22 — Fragment delimiter
**§3.5**  
The fragment component begins at the first `#` character and extends to the end of the URI.

## R23 — Percent-encoding syntax
**§2.1 / Appendix A**  
`pct-encoded = "%" HEXDIG HEXDIG`  
A percent sign MUST be followed by exactly two hexadecimal digits (0–9, A–F, a–f).

## R24 — Unreserved characters
**§2.3 / Appendix A**  
`unreserved = ALPHA / DIGIT / "-" / "." / "_" / "~"`  
These characters have no reserved purpose and may appear anywhere they are syntactically allowed.

## R25 — Reserved characters — gen-delims
**§2.2 / Appendix A**  
`gen-delims = ":" / "/" / "?" / "#" / "[" / "]" / "@"`  
These characters delimit URI components and must be percent-encoded when used as data.

## R26 — Reserved characters — sub-delims
**§2.2 / Appendix A**  
`sub-delims = "!" / "$" / "&" / "'" / "(" / ")" / "*" / "+" / "," / ";" / "="`  
Sub-delimiters may appear literally in most components (they are "reserved for use as subcomponent delimiters").

## R27 — Whitespace is not allowed in a URI
**§2 / §1.2.1**  
A URI consists only of characters from the US-ASCII set (letters, digits, a few graphic symbols). Raw space characters (SP, TAB, CRLF) are not allowed; they must be percent-encoded.

## R28 — Scheme is required
**§3**  
The scheme component is not optional in a URI (only in a relative-reference). An input without a scheme (e.g., `//host/path` or `host/path`) is a relative reference, not a URI.

## R29 — IPv6 literal must be enclosed in brackets
**§3.2.2**  
A bare IPv6 address (e.g., `2001:db8::1`) used as a host must be enclosed in square brackets: `[2001:db8::1]`. Unbracketed IPv6 addresses are not valid URI hosts.

## R30 — Empty fragment is syntactically distinct from absent fragment
**§3.5 / §5.3**  
`http://example.com/#` (empty fragment) is a distinct URI from `http://example.com/` (no fragment).

## R31 — Multiple @ in authority is invalid
**§3.2 / §3.2.1**  
Only one `@` separates userinfo from host. A netloc string containing more than one `@` is invalid.
