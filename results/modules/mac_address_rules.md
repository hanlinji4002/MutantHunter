# MAC Address — Extracted Rules

Source document: wiki-MAC_address.pdf (Wikipedia: MAC address, retrieved from oldid=1362513041)

---

## Rules

**R1** — A MAC address in its standard (EUI-48) form consists of **six groups of two hexadecimal digits**.  
Source: wiki-MAC_address.pdf § "Notational conventions"  
> "The standard (IEEE 802) format for printing EUI-48 addresses in human-friendly form is six groups of two hexadecimal digits…"

**R2** — The six groups may be **separated by hyphens (`-`)**.  
Source: wiki-MAC_address.pdf § "Notational conventions"  
> "…separated by hyphens (-) in transmission order (e.g. 01-23-45-67-89-AB)."

**R3** — The six groups may be **separated by colons (`:`)**.  
Source: wiki-MAC_address.pdf § "Notational conventions"  
> "Other conventions include six groups of two hexadecimal digits separated by colons (:) (e.g. 01:23:45:67:89:AB)…"

**R4** — An alternative notation uses **three groups of four hexadecimal digits separated by dots (`.`)** (e.g. `0123.4567.89AB`).  
Source: wiki-MAC_address.pdf § "Notational conventions"  
> "…and three groups of four hexadecimal digits separated by dots (.) (e.g. 0123.4567.89AB)…"

**R5** — Hexadecimal digits are **case-insensitive** (both uppercase A–F and lowercase a–f are valid).  
Source: wiki-MAC_address.pdf § "Notational conventions" (examples show mixed case: `01-23-45-67-89-AB`)

**R6** — The address must contain **exactly 48 bits** (6 octets × 8 bits), no more, no fewer.  
Source: wiki-MAC_address.pdf § "Address details"  
> "This 48-bit address space contains potentially 2^48 possible MAC addresses."

**R7** — A **broadcast address** of all ones (`FF:FF:FF:FF:FF:FF` or `FF-FF-FF-FF-FF-FF`) is a valid MAC address.  
Source: wiki-MAC_address.pdf § "Unicast vs. multicast (I/G bit)"  
> "In hexadecimal the broadcast address would be FF:FF:FF:FF:FF:FF."

**R8** — A **multicast address** has the least-significant bit of the first octet set to 1 (i.e. first hex digit is odd); it is still a validly formatted MAC address.  
Source: wiki-MAC_address.pdf § "Unicast vs. multicast (I/G bit)"  
> "If the least significant bit of the first octet is set to 1 … the frame will still be sent only once…"

**R9** — A **locally administered address (LAA)** has the second-least-significant bit of the first octet set to 1. It is a valid MAC address (e.g. `06-00-00-00-00-00`).  
Source: wiki-MAC_address.pdf § "Universal vs. local (U/L bit)"  
> "Locally administered addresses are distinguished … by setting … the second-least-significant bit of the first octet… In the example address 06-00-00-00-00-00…"

**R10** — A string with **fewer than six groups** of two hex digits is **not** a valid MAC address.  
Source: wiki-MAC_address.pdf § "Notational conventions" (six groups are mandatory); § "Address details" (48-bit requirement, R6)

**R11** — A string with **more than six groups** of two hex digits is **not** a valid MAC address (48-bit size is fixed).  
Source: wiki-MAC_address.pdf § "Address details" (R6)

**R12** — Groups must each contain **exactly two hexadecimal digits** (no single-digit or three-digit groups).  
Source: wiki-MAC_address.pdf § "Notational conventions" ("six groups of **two** hexadecimal digits")

**R13** — Non-hexadecimal characters (e.g. `G`–`Z` outside `A`–`F`, or non-ASCII symbols) in any group render the address **invalid**.  
Source: wiki-MAC_address.pdf § "Notational conventions" (only hexadecimal digits, 0–9, A–F, are specified)

**R14** — An empty string is **not** a valid MAC address.  
Source: wiki-MAC_address.pdf § "Notational conventions" (a valid MAC address must have the structure described in R1–R3/R4)

**R15** — A MAC address written without any separator is **not** explicitly covered by the Wikipedia spec as a human-friendly notation (only hyphen, colon, and dot-grouped forms are specified).  
Source: wiki-MAC_address.pdf § "Notational conventions"  
Note: The article text says separators can be "without a separator" only in the first paragraph's introductory sentence; the Notational conventions section specifies three distinct notations (hyphens, colons, dots). This is treated as spec-ambiguous for the "no separator" case.

**R16** — **Mixing separators** (e.g. some groups separated by `:` and others by `-`) is **not** a valid notation; each address uses one consistent separator throughout.  
Source: wiki-MAC_address.pdf § "Notational conventions" (each notation uses one separator type exclusively)

**R17** — The all-zeros address `00:00:00:00:00:00` is a structurally valid MAC address (all octets are valid two-hex-digit groups).  
Source: wiki-MAC_address.pdf § "Address details" / § "Notational conventions" (no exclusion of all-zero values is stated)
