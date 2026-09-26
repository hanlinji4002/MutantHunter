# Email Validation Rules

Extracted from RFC 5321 (SMTP) and RFC 5322 (Internet Message Format).

---

## R1 — Address structure: exactly one `@`
**Source:** RFC 5322 §3.4.1  
`addr-spec = local-part "@" domain`  
A valid email address MUST contain exactly one `@` character separating the local-part from the domain.

## R2 — Local-part maximum length: 64 octets
**Source:** RFC 5321 §4.5.3.1.1  
The maximum total length of a user name or other local-part is **64 octets**.

## R3 — Domain maximum length: 255 octets
**Source:** RFC 5321 §4.5.3.1.2  
The maximum total length of a domain name or number is **255 octets**.

## R4 — Local-part dot-atom form: allowed characters
**Source:** RFC 5322 §3.2.3, §3.4.1  
`atext = ALPHA / DIGIT / "!" / "#" / "$" / "%" / "&" / "'" / "*" / "+" / "-" / "/" / "=" / "?" / "^" / "_" / "`" / "{" / "|" / "}" / "~"`  
`dot-atom-text = 1*atext *("." 1*atext)`  
In dot-atom form the local-part consists of `atext` characters optionally separated by dots. The characters `(`, `)`, `<`, `>`, `[`, `]`, `:`, `;`, `@`, `\`, `,`, and `"` (specials) are NOT allowed in the dot-atom form.

## R5 — Local-part dot rules: no leading, trailing, or consecutive dots
**Source:** RFC 5322 §3.2.3, §3.4.1  
`dot-atom-text = 1*atext *("." 1*atext)`  
In dot-atom form, the local-part must NOT begin with a dot, end with a dot, or contain consecutive dots (`..`).

## R6 — Local-part quoted-string form
**Source:** RFC 5322 §3.2.4, §3.4.1 / RFC 5321 §4.1.2  
The local-part MAY be a quoted-string enclosed in double-quote characters (`"`). Inside the quoted string, any printable ASCII character (except `"` and `\`) is allowed without escaping; `"` and `\` must be escaped as `\"` and `\\`.  
RFC 5321 qtextSMTP: `%d32-33 / %d35-91 / %d93-126` (space and printable US-ASCII except `"` and `\`).

## R7 — Domain dot-atom form: sub-domain labels
**Source:** RFC 5321 §4.1.2  
`Domain = sub-domain *("." sub-domain)`  
`sub-domain = Let-dig [Ldh-str]`  
`Let-dig = ALPHA / DIGIT`  
`Ldh-str = *( ALPHA / DIGIT / "-" ) Let-dig`  
Each label must start with a letter or digit, end with a letter or digit, and contain only letters, digits, and hyphens. Underscores and other special characters are NOT permitted in domain labels.

## R8 — Domain label: no leading or trailing hyphen
**Source:** RFC 5321 §4.1.2  
`sub-domain = Let-dig [Ldh-str]` and `Ldh-str = *( ALPHA / DIGIT / "-" ) Let-dig`  
Domain labels MUST NOT begin or end with a hyphen.

## R9 — Domain: at least one dot for FQDN (internet mail)
**Source:** RFC 5321 §2.3.5  
Only resolvable, fully-qualified domain names (FQDNs) are permitted in SMTP; a single-label domain (no dot) is not a valid FQDN on the public Internet (exception: the `simple_host` option relaxes this for local contexts).

## R10 — Domain literal: IPv4 address in brackets
**Source:** RFC 5321 §4.1.3 / RFC 5322 §3.4.1  
`address-literal = "[" ( IPv4-address-literal / IPv6-address-literal / General-address-literal ) "]"`  
When the domain part is an IP address literal it MUST be enclosed in square brackets `[...]`. For IPv4: `[d.d.d.d]` where each octet is 0–255.

## R11 — Domain literal: IPv6 address in brackets with `IPv6:` tag
**Source:** RFC 5321 §4.1.3  
`IPv6-address-literal = "IPv6:" IPv6-addr`  
IPv6 literals MUST use the `IPv6:` prefix inside brackets, e.g., `[IPv6:::1]`.

## R12 — Local-part case sensitivity
**Source:** RFC 5321 §2.4  
The local-part of a mailbox MUST BE treated as case-sensitive by SMTP servers. (The validators library accepts both cases as syntactically valid.)

## R13 — Domain case insensitivity
**Source:** RFC 5321 §2.4  
Mailbox domains follow normal DNS rules and are hence NOT case-sensitive.

## R14 — No bare `@` — both parts required
**Source:** RFC 5322 §3.4.1 / RFC 5321 §4.1.2  
Both the local-part and the domain part MUST be non-empty.

## R15 — Local-part specials not allowed outside quoted-string
**Source:** RFC 5322 §3.2.3  
`specials = "(" / ")" / "<" / ">" / "[" / "]" / ":" / ";" / "@" / "\" / "," / "." / DQUOTE`  
These characters appear in `specials` (not in `atext`) and MUST NOT appear in an unquoted local-part.

## R16 — Space not allowed in unquoted local-part
**Source:** RFC 5322 §3.2.3  
Whitespace (SP, HTAB) is not in `atext` and therefore MUST NOT appear in an unquoted local-part or outside CFWS context.

## R17 — Domain must not be empty
**Source:** RFC 5322 §3.4.1  
`addr-spec = local-part "@" domain` requires a non-empty domain portion.

## R18 — Local-part must not be empty
**Source:** RFC 5322 §3.4.1  
`local-part = dot-atom / quoted-string / obs-local-part` requires at least one character.

## R19 — atext characters are case-insensitive for matching
**Source:** RFC 5322 §3.2.3  
Both upper-case and lower-case letters are `ALPHA` and therefore valid atext. The local-part alphabet includes A–Z and a–z.

## R20 — Non-ASCII (high-bit) characters NOT permitted in standard SMTP
**Source:** RFC 5321 §2.4  
Systems MUST NOT define mailboxes that require non-ASCII characters (octets with the high-order bit set) in SMTP. The unextended SMTP service is 7-bit only.  
*(The validators library uses the `@validator` decorator and does accept certain extended Latin characters as an implementation extension; tests for that rely on the implementation docstring.)*
