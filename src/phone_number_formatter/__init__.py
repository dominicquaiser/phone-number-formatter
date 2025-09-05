"""
Phone Number Formatter

A versatile phone number formatting utility that works both as an Apify actor 
and as a standalone Python package.
"""

from .core import (
    PhoneFormatter,
    PhoneFormatterConfig,
    PhoneNumberParser,
    PhoneNumberFormatter,
    PhoneNumberBatchProcessor,
    RateLimiter,
    PHONE_NUMBER_FORMATS,
)

__version__ = "1.2.0"
__author__ = "Dominic M. Quaiser"
__email__ = "mail@quaiser.dev"

__all__ = [
    "PhoneFormatter",
    "PhoneFormatterConfig", 
    "PhoneNumberParser",
    "PhoneNumberFormatter",
    "PhoneNumberBatchProcessor",
    "RateLimiter",
    "PHONE_NUMBER_FORMATS",
]