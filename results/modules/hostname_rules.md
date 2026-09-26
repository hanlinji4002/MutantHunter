# Hostname Rules

Extracted from RFC 952 (October 1985) and RFC 1123 (October 1989).

---

## RFC 952 — DOD INTERNET HOST TABLE SPECIFICATION

### Section: ASSUMPTIONS, item 1

**R1** — A host name is a text string up to **24 characters** drawn from the
alphabet (A–Z), digits (0–9), the minus sign (`-`), and the period (`.`).
*(Note: RFC 1123 §2.1 later relaxes the first-character restriction and raises
the length limit — see R7/R8 below.)*

**R2** — Periods are only allowed when they serve to **delimit components** of
domain-style names (i.e., inside a multi-label hostname such as
`example.com`).

**R3** — No blank or space characters are permitted as part of a name.

**R4** — No distinction is made between **upper and lower case** in host names.

**R5** — The **first character must be an alphabetic character** (A–Z).
*(Relaxed by RFC 1123 §2.1 — see R7.)*

**R6** — The **last character must not be a minus sign or period**.

### Section: GRAMMATICAL HOST TABLE SPECIFICATION — Lexical grammar

**R6a** — A single name component follows the grammar:
```
<name> ::= <let>[*[<let-or-digit-or-hyphen>]<let-or-digit>]
```
i.e., starts with a letter, ends with a letter or digit, interior characters
may be letters, digits, or hyphens.  
A single-character name is a single letter.

**R6b** — A host name may be composed of multiple dot-separated labels:
```
<hname> ::= <name>*["."<name>]
```

---

## RFC 1123 — Requirements for Internet Hosts, Section 2.1

**R7** — The restriction on the **first character is relaxed**: the first
character of a hostname label may be either a **letter or a digit**.
*Host software MUST support this more liberal syntax.*

**R8** — Host software **MUST handle** host names of up to **63 characters**.

**R9** — Host software **SHOULD handle** host names of up to **255 characters**.

**R10** — A hostname (label) MUST NOT begin with a hyphen.

**R11** — A hostname (label) MUST NOT end with a hyphen.

**R12** — The interior of a label may contain hyphens, letters, and digits,
but no other characters (no underscore, no slash, no special characters).

---

## Derived / boundary rules (from the combined specs)

**R13** — An **empty string** is not a valid hostname.

**R14** — A hostname that is exactly **63 characters long** (all alphanumeric)
is valid; one that is 64 characters long exceeds the per-label limit.

**R15** — A hostname whose only content is hyphens (e.g. `---`) is invalid
because the first and last characters are hyphens (violates R10/R11).

**R16** — A single letter is a valid single-label hostname (RFC 952 grammar
allows `<name> ::= <let>`; RFC 1123 extends this to `<let-or-digit>`).

**R17** — A single digit is a valid single-label hostname under RFC 1123 §2.1.

**R18** — Labels may not contain characters outside `[A-Za-z0-9-]`; special
characters such as `*`, `@`, `!`, `$`, `#`, `%`, space, etc. are invalid.

**R19** — A label consisting solely of digits is syntactically valid under
RFC 1123 §2.1 (the TLD-is-alphabetic constraint applies only to full domain
names, not to single-label simple hostnames).
