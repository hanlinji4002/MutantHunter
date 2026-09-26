"""Additional pytest tests for validators.finance (batch 1)."""

import pytest
from validators import ValidationError, cusip, isin, sedol


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid(fn, value):
    result = fn(value)
    assert result, f"Expected valid for {value!r}, got {result!r}"


def _invalid(fn, value):
    result = fn(value)
    assert not result, f"Expected invalid for {value!r}, got {result!r}"


# ===========================================================================
# CUSIP
# ===========================================================================

class TestCusipDocstringExamples:
    """Docstring examples from the cusip() function."""

    def test_valid_037833dp2(self):
        """Docstring: cusip"""
        _valid(cusip, "037833DP2")

    def test_invalid_037833dp3(self):
        """Docstring: cusip"""
        _invalid(cusip, "037833DP3")


class TestCusipValidValues:
    """Docstring: cusip — well-known real-world CUSIPs."""

    @pytest.mark.parametrize("value", [
        "037833100",   # Apple Inc
        "38259P508",   # Google (Alphabet)
        "594918104",   # Microsoft
        "023135106",   # Amazon
        "000000000",   # all-zero check passes (sum=0, 0%10==0)
        "*00000001",   # asterisk (*) is a valid CUSIP character
        "0@0000009",   # at-sign (@) is a valid CUSIP character
        "00#000009",   # hash (#) is a valid CUSIP character
        "a00000009",   # lowercase letter is accepted by the checksum
    ])
    def test_valid_cusips(self, value):
        """Docstring: cusip"""
        _valid(cusip, value)


class TestCusipInvalidLength:
    """Docstring: cusip — wrong-length strings are rejected."""

    @pytest.mark.parametrize("value", [
        "",            # empty
        "03783310",    # 8 chars (too short)
        "037833100X",  # 10 chars (too long)
        "0",
        "037833DP2X",
    ])
    def test_invalid_cusip_length(self, value):
        """Docstring: cusip"""
        _invalid(cusip, value)


class TestCusipInvalidCheckDigit:
    """Docstring: cusip — 9-char strings with wrong check digit."""

    @pytest.mark.parametrize("value", [
        "037833DP3",   # docstring example
        "037833101",   # Apple CUSIP with wrong check digit
        "000000001",   # all zeros except last digit
    ])
    def test_invalid_cusip_check(self, value):
        """Docstring: cusip"""
        _invalid(cusip, value)


class TestCusipInvalidCharacters:
    """Docstring: cusip — characters outside the allowed set."""

    @pytest.mark.parametrize("value", [
        "!37833100",   # exclamation mark
        "03 833100",   # space
        "037833DP!",   # invalid last char
    ])
    def test_invalid_cusip_chars(self, value):
        """Docstring: cusip"""
        _invalid(cusip, value)


class TestCusipReturnType:
    """Docstring: cusip — return-type contract."""

    def test_valid_returns_truthy(self):
        """Docstring: cusip"""
        assert cusip("037833100")

    def test_invalid_returns_validation_error(self):
        """Docstring: cusip"""
        result = cusip("037833DP3")
        assert isinstance(result, ValidationError)


# ===========================================================================
# ISIN
# ===========================================================================

class TestIsinDocstringExamples:
    """Docstring examples from the isin() function."""

    def test_cusip_alone_is_invalid_isin(self):
        """Docstring: isin"""
        _invalid(isin, "037833DP2")

    def test_another_cusip_is_invalid_isin(self):
        """Docstring: isin"""
        _invalid(isin, "037833DP3")


class TestIsinValidValues:
    """Docstring: isin — well-known real-world ISINs."""

    @pytest.mark.parametrize("value", [
        "US0378331005",   # Apple Inc
        "US38259P5089",   # Google (Alphabet)
        "US5949181045",   # Microsoft
        "US0231351067",   # Amazon
        "GB0002634946",   # BAE Systems
        "GB0031348658",   # HSBC
        "XX0000000000",   # syntactically valid (any two uppercase letters + 10 digits)
        "ZZ9999999999",   # syntactically valid
        "AA1234567890",   # syntactically valid
    ])
    def test_valid_isins(self, value):
        """Docstring: isin"""
        _valid(isin, value)


class TestIsinInvalidLength:
    """Docstring: isin — wrong-length strings are rejected."""

    @pytest.mark.parametrize("value", [
        "",              # empty
        "US037833100",   # 11 chars (too short)
        "US03783310055", # 13 chars (too long)
        "US0378331",     # much too short
    ])
    def test_invalid_isin_length(self, value):
        """Docstring: isin"""
        _invalid(isin, value)


class TestIsinInvalidFirstTwoChars:
    """Docstring: isin — first two positions must be uppercase letters."""

    @pytest.mark.parametrize("value", [
        "1S0378331005",  # digit at position 0
        "U10378331005",  # digit at position 1
        "120000000000",  # both leading chars are digits
    ])
    def test_invalid_isin_country_code(self, value):
        """Docstring: isin"""
        _invalid(isin, value)


class TestIsinInvalidCharacters:
    """Docstring: isin — special characters outside the allowed set."""

    @pytest.mark.parametrize("value", [
        "US0378!31005",  # exclamation mark
        "US0378 31005",  # space
    ])
    def test_invalid_isin_special_chars(self, value):
        """Docstring: isin"""
        _invalid(isin, value)


class TestIsinReturnType:
    """Docstring: isin — return-type contract."""

    def test_valid_returns_truthy(self):
        """Docstring: isin"""
        assert isin("US0378331005")

    def test_invalid_returns_validation_error(self):
        """Docstring: isin"""
        result = isin("037833DP2")
        assert isinstance(result, ValidationError)


# ===========================================================================
# SEDOL
# ===========================================================================

class TestSedolDocstringExamples:
    """Docstring examples from the sedol() function."""

    def test_valid_2936921(self):
        """Docstring: sedol"""
        _valid(sedol, "2936921")

    def test_invalid_29a6922(self):
        """Docstring: sedol — vowel A in third position."""
        _invalid(sedol, "29A6922")


class TestSedolValidValues:
    """Docstring: sedol — additional well-known valid SEDOLs."""

    @pytest.mark.parametrize("value", [
        "2936921",   # docstring example
        "0263494",   # BAE Systems
        "3134865",   # HSBC
        "B000300",   # valid with leading letter
        "0540528",
        "0798059",
        "0000000",   # all-zero: check sum = 0, 0 % 10 == 0
        "1000009",   # digit at pos 0 (weight 1) + check digit 9 → sum=10 → 0
    ])
    def test_valid_sedols(self, value):
        """Docstring: sedol"""
        _valid(sedol, value)


class TestSedolInvalidLength:
    """Docstring: sedol — wrong-length strings are rejected."""

    @pytest.mark.parametrize("value", [
        "",          # empty
        "293692",    # 6 chars (too short)
        "29369211",  # 8 chars (too long)
        "2",
    ])
    def test_invalid_sedol_length(self, value):
        """Docstring: sedol"""
        _invalid(sedol, value)


class TestSedolVowelRejection:
    """Docstring: sedol — vowels are not allowed in any position."""

    @pytest.mark.parametrize("vowel", list("AEIOU"))
    def test_vowel_at_position_4_is_invalid(self, vowel):
        """Docstring: sedol"""
        # Use a slot that doesn't affect the surrounding digits' check sum validity
        value = "2936" + vowel + "21"
        _invalid(sedol, value)

    def test_lowercase_letter_is_invalid(self):
        """Docstring: sedol"""
        # Only 0-9 and A-Z (uppercase) are accepted; lowercase falls through to False
        _invalid(sedol, "293692a")


class TestSedolInvalidCheckDigit:
    """Docstring: sedol — 7-char strings with wrong check digit."""

    @pytest.mark.parametrize("value", [
        "2936922",   # docstring: wrong check digit on 2936921
        "B00030A",   # wrong check digit
        "1000000",   # digit sum = 1 * 1 = 1, check must be 9
    ])
    def test_invalid_sedol_check(self, value):
        """Docstring: sedol"""
        _invalid(sedol, value)


class TestSedolInvalidCharacters:
    """Docstring: sedol — only 0-9 and non-vowel A-Z are allowed."""

    @pytest.mark.parametrize("value", [
        "293692#",   # hash
        "293692!",   # exclamation mark
        "2936 21",   # space
        "293692*",   # asterisk (valid in CUSIP but not SEDOL)
    ])
    def test_invalid_sedol_chars(self, value):
        """Docstring: sedol"""
        _invalid(sedol, value)


class TestSedolReturnType:
    """Docstring: sedol — return-type contract."""

    def test_valid_returns_truthy(self):
        """Docstring: sedol"""
        assert sedol("2936921")

    def test_invalid_returns_validation_error(self):
        """Docstring: sedol"""
        result = sedol("29A6922")
        assert isinstance(result, ValidationError)
