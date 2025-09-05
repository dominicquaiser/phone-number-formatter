"""
Phone number formatting utility for Apify actors.

Provides tools for parsing, validating, and formatting phone numbers across different regions 
and formats using the phonenumbers library. This utility handles bulk processing with 
configurable rate limiting and concurrency controls.
"""
from __future__ import annotations

import os
import re
import asyncio
import time
import logging
from dataclasses import dataclass, fields
from typing import List, Dict, Any, Tuple, Optional, Union, cast
import phonenumbers

# Configure logging without duplicate timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('phone_formatter')

# --- Configuration Classes ---

@dataclass
class PhoneFormatterConfig:
    """Configuration for phone number formatting operations.
    
    Attributes:
        default_region: ISO 3166-1 alpha-2 country code for parsing (e.g., 'US', 'GB')
        output_format: Format for phone numbers ('E164', 'INTERNATIONAL', 'NATIONAL', 'RFC3966')
        batch_size: Number of phone numbers to process in a single batch
        max_concurrent_tasks: Maximum number of concurrent formatting tasks
        rate_limit_per_second: Maximum operations per second (throttling)
        backoff_factor: Multiplier for exponential backoff on retries
        max_retries: Maximum retry attempts before failing
        aggressive_cleaning: Whether to aggressively strip non-digit characters
    """
    default_region: str = "US"
    output_format: str = "E164"
    batch_size: int = 100
    max_concurrent_tasks: int = 10
    rate_limit_per_second: float = 100.0
    backoff_factor: float = 1.5
    max_retries: int = 3
    aggressive_cleaning: bool = False

    def __post_init__(self):
        """Validate configuration after initialization."""
        logger.debug(f"Validating config: {self}")
        self.validate()

    def validate(self):
        """Validate configuration parameters and set defaults if needed."""
        if self.default_region not in phonenumbers.SUPPORTED_REGIONS:
            logger.warning(
                f"Region '{self.default_region}' not supported by phonenumbers library. Defaulting to 'US'"
            )
            self.default_region = "US"

        if self.output_format not in PHONE_NUMBER_FORMATS:
            logger.warning(
                f"Format '{self.output_format}' not supported. Defaulting to 'E164'"
            )
            self.output_format = "E164"

        if self.batch_size < 1:
            logger.warning("Batch size must be positive. Defaulting to 100")
            self.batch_size = 100
        
        if self.max_concurrent_tasks < 1:
            logger.warning("Max concurrent tasks must be positive. Defaulting to 10")
            self.max_concurrent_tasks = 10
            
        if self.rate_limit_per_second <= 0:
            logger.warning("Rate limit must be positive. Defaulting to 100.0")
            self.rate_limit_per_second = 100.0

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> PhoneFormatterConfig:
        """Create configuration from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration parameters
            
        Returns:
            Initialized PhoneFormatterConfig object
        """
        valid_keys = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in config_dict.items() if k in valid_keys}
        logger.debug(f"Loading config from dict keys={list(filtered.keys())}")
        return cls(**filtered)

    @classmethod
    def from_env(cls) -> PhoneFormatterConfig:
        """Create configuration from environment variables.
        
        Environment variables:
            PHONE_FORMATTER_REGION: Default region code (default: 'US')
            PHONE_FORMATTER_FORMAT: Output format (default: 'E164')
            PHONE_FORMATTER_BATCH_SIZE: Batch size for processing (default: 100)
            PHONE_FORMATTER_MAX_TASKS: Max concurrent tasks (default: 10)
            PHONE_FORMATTER_RATE_LIMIT: Operations per second (default: 100.0)
            PHONE_FORMATTER_BACKOFF: Backoff factor for retries (default: 1.5)
            PHONE_FORMATTER_MAX_RETRIES: Maximum retry attempts (default: 3)
            PHONE_FORMATTER_AGGRESSIVE_CLEAN: Aggressive cleaning (default: False)
            
        Returns:
            Initialized PhoneFormatterConfig object
        """
        cfg = {
            "default_region": os.getenv("PHONE_FORMATTER_REGION", "US"),
            "output_format": os.getenv("PHONE_FORMATTER_FORMAT", "E164"),
            "batch_size": int(os.getenv("PHONE_FORMATTER_BATCH_SIZE", "100")),
            "max_concurrent_tasks": int(os.getenv("PHONE_FORMATTER_MAX_TASKS", "10")),
            "rate_limit_per_second": float(os.getenv("PHONE_FORMATTER_RATE_LIMIT", "100.0")),
            "backoff_factor": float(os.getenv("PHONE_FORMATTER_BACKOFF", "1.5")),
            "max_retries": int(os.getenv("PHONE_FORMATTER_MAX_RETRIES", "3")),
            "aggressive_cleaning": os.getenv("PHONE_FORMATTER_AGGRESSIVE_CLEAN", "False").lower() == "true"
        }
        logger.info("Loaded configuration from environment")
        return cls.from_dict(cfg)


# Dictionary mapping format names to phonenumbers library constants
PHONE_NUMBER_FORMATS = {
    'E164': phonenumbers.PhoneNumberFormat.E164,                    # +14155552671
    'INTERNATIONAL': phonenumbers.PhoneNumberFormat.INTERNATIONAL,  # +1 415 555 2671
    'NATIONAL': phonenumbers.PhoneNumberFormat.NATIONAL,            # (415) 555-2671
    'RFC3966': phonenumbers.PhoneNumberFormat.RFC3966,              # tel:+1-415-555-2671
}


class PhoneNumberParser:
    """Parser for cleaning and extracting phone numbers from input text."""
    
    def __init__(self, config: PhoneFormatterConfig):
        """Initialize the parser with configuration.
        
        Args:
            config: Configuration parameters for phone number parsing
        """
        self.config = config
        logger.debug("PhoneNumberParser initialized")

    def parse_phone_number_input(self, numbers: str) -> List[str]:
        """Parse a string input into a list of individual phone numbers.
        
        Args:
            numbers: String containing one or more phone numbers separated by commas, 
                    newlines, or semicolons
                    
        Returns:
            List of individual phone number strings
        """
        logger.debug(f"Parsing input text of length={len(numbers)}")
        nums = numbers.replace('\n', ',').replace(';', ',')
        while ',,' in nums:
            nums = nums.replace(',,', ',')
        parsed = [p.strip() for p in nums.split(',') if p.strip()]
        logger.info(f"Parsed {len(parsed)} phone numbers from input")
        return parsed

    def clean_phone_number(self, number: str) -> str:
        """Clean a phone number by removing unwanted characters.
        
        Args:
            number: Raw phone number string
            
        Returns:
            Cleaned phone number string
        """
        original = number
        if self.config.aggressive_cleaning:
            # Keep only digits and '+' character
            cleaned = re.sub(r'[^\d+]', '', number)
            logger.debug(f"Aggressively cleaned '{original}' to '{cleaned}'")
            return cleaned
        
        # Standard cleaning - keep spaces but remove common separators
        cleaned = re.sub(r'\s+', ' ', number)
        cleaned = re.sub(r'[.()-]', '', cleaned)
        cleaned = cleaned.strip()
        logger.debug(f"Cleaned '{original}' to '{cleaned}'")
        return cleaned


class PhoneNumberFormatter:
    """Formatter for standardizing phone numbers to various formats."""
    
    def __init__(self, config: PhoneFormatterConfig):
        """Initialize the formatter with configuration.
        
        Args:
            config: Configuration parameters for phone number formatting
        """
        self.config = config
        self._country_code_cache: Dict[str, Optional[int]] = {}
        logger.debug("PhoneNumberFormatter initialized")

    def get_country_code(self, region: str) -> Optional[int]:
        """Get the numeric country calling code for a region.
        
        Args:
            region: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')
            
        Returns:
            Numeric country code or None if region is invalid
        """
        if region not in self._country_code_cache:
            code = phonenumbers.country_code_for_region(region)
            self._country_code_cache[region] = code if code != 0 else None
            logger.debug(f"Cached country code for {region}: {self._country_code_cache[region]}")
        return self._country_code_cache[region]

    def format_single_phone_number(self, raw: str, default_region: str, fmt: str) -> Tuple[str, bool, Optional[str]]:
        """Format a single phone number to the specified format.
        
        Args:
            raw: Raw phone number string
            default_region: ISO 3166-1 alpha-2 country code for parsing
            fmt: Output format name ('E164', 'INTERNATIONAL', 'NATIONAL', 'RFC3966')
            
        Returns:
            Tuple containing:
                - Formatted phone number (or original if formatting failed)
                - Success flag (True if formatting succeeded)
                - Error message (None if formatting succeeded)
        """
        fmt_const = PHONE_NUMBER_FORMATS.get(fmt.upper(), phonenumbers.PhoneNumberFormat.E164)
        logger.debug(f"Formatting '{raw}' using region={default_region}, format={fmt}")

        # First attempt: try parsing as-is
        success, formatted, error = self._attempt_phone_number_parse(raw, default_region, fmt_const)
        if success:
            logger.debug(f"Successfully formatted '{raw}' -> '{formatted}'")
            return formatted, True, None

        # Second attempt: try adding country code if not already present
        if not raw.startswith('+'):
            cc = self.get_country_code(default_region)
            if cc:
                attempt = f"+{cc}{raw}"
                success, formatted, error = self._attempt_phone_number_parse(attempt, default_region, fmt_const)
                if success:
                    logger.debug(f"Successfully formatted with country code '{attempt}' -> '{formatted}'")
                    return formatted, True, None

        # Final attempt: try with aggressively cleaned input
        cleaned = re.sub(r'[^\d+]', '', raw)
        logger.debug(f"Fallback cleaned '{raw}' to '{cleaned}' for parsing")
        success, formatted, error = self._attempt_phone_number_parse(cleaned, default_region, fmt_const)
        if success:
            logger.debug(f"Successfully formatted fallback '{cleaned}' -> '{formatted}'")
            return formatted, True, None

        logger.error(f"Failed to format '{raw}': {error}")
        return raw, False, error

    def _attempt_phone_number_parse(self, raw: str, default_region: str, fmt_const: int) -> Tuple[bool, str, Optional[str]]:
        """Attempt to parse and format a phone number.
        
        Args:
            raw: Raw phone number string
            default_region: ISO 3166-1 alpha-2 country code for parsing
            fmt_const: Output format constant from phonenumbers library
            
        Returns:
            Tuple containing:
                - Success flag (True if parsing succeeded)
                - Formatted phone number (or original if parsing failed)
                - Error message (None if parsing succeeded)
        """
        try:
            num = phonenumbers.parse(raw, default_region)
            if not phonenumbers.is_possible_number(num):
                logger.warning(f"Impossible number detected: {raw}")
                return False, raw, f"Impossible number: {raw}"
            formatted = phonenumbers.format_number(num, fmt_const)
            return True, formatted, None
        except phonenumbers.NumberParseException as e:
            logger.warning(f"Parse exception for '{raw}': {e}")
            return False, raw, f"Parse error for {raw}: {e}"


class RateLimiter:
    """Asynchronous rate limiter to control operation frequency."""
    
    def __init__(self, rate_limit: float):
        """Initialize the rate limiter.
        
        Args:
            rate_limit: Maximum operations per second
        """
        self.min_interval = 1.0 / rate_limit if rate_limit > 0 else 0
        self.last_operation_time = 0.0
        self._lock = asyncio.Lock()
        logger.debug(f"RateLimiter set with min_interval={self.min_interval}")

    async def acquire(self):
        """Acquire permission to proceed, waiting if needed to respect rate limit.
        
        This method will block until the rate limit allows the operation to proceed.
        """
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_operation_time
            wait_time = max(0, self.min_interval - elapsed)
            if wait_time > 0:
                logger.debug(f"RateLimiter sleeping for {wait_time:.3f}s")
                await asyncio.sleep(wait_time)
            self.last_operation_time = time.time()


class PhoneNumberBatchProcessor:
    """Processor for handling batches of phone numbers with concurrency control."""
    
    def __init__(self, config: PhoneFormatterConfig, parser: PhoneNumberParser, formatter: PhoneNumberFormatter):
        """Initialize the batch processor.
        
        Args:
            config: Configuration parameters
            parser: Phone number parser
            formatter: Phone number formatter
        """
        self.config = config
        self.parser = parser
        self.formatter = formatter
        self.rate_limiter = RateLimiter(config.rate_limit_per_second)
        self._semaphore = asyncio.Semaphore(config.max_concurrent_tasks)
        logger.debug("PhoneNumberBatchProcessor initialized")

    async def process_single_number(self, raw: str, index: int) -> Dict[str, Any]:
        """Process a single phone number with rate limiting.
        
        Args:
            raw: Raw phone number string
            index: Position index of this number in the original input
            
        Returns:
            Dictionary containing processing results
        """
        await self.rate_limiter.acquire()
        cleaned = self.parser.clean_phone_number(raw)
        formatted, success, error = self.formatter.format_single_phone_number(
            cleaned, self.config.default_region, self.config.output_format
        )
        result = {'index': index, 'input': raw, 'phone_number': formatted, 'success': success}
        if error:
            result['error'] = error
        logger.debug(f"Result for index {index}: {result}")
        return result

    async def process_phone_number_batch(self, numbers: List[str], start_index: int = 0) -> List[Dict[str, Any]]:
        """Process a batch of phone numbers concurrently.
        
        Args:
            numbers: List of raw phone number strings
            start_index: Starting index for this batch in the overall list
            
        Returns:
            List of processing results in the same order as the input
        """
        logger.info(f"Processing batch of {len(numbers)} numbers starting at index {start_index}")
        
        async def _wrap(raw: str, idx: int) -> Dict[str, Any]:
            """Wrapper function to handle semaphore for concurrency control."""
            async with self._semaphore:
                return await self.process_single_number(raw, start_index + idx)
                
        tasks = [_wrap(n, i) for i, n in enumerate(numbers)]
        results = await asyncio.gather(*tasks)
        sorted_results = sorted(results, key=lambda r: r['index'])
        logger.info(f"Completed batch starting at index {start_index}")
        return sorted_results


class PhoneFormatter:
    """Main class providing phone number formatting functionality."""
    
    def __init__(self, config: Optional[PhoneFormatterConfig] = None):
        """Initialize the phone formatter.
        
        Args:
            config: Configuration parameters (uses defaults if None)
        """
        self.config = config or PhoneFormatterConfig()
        logger.info(f"PhoneFormatter instantiated with config: {self.config}")
        self.parser = PhoneNumberParser(self.config)
        self.formatter = PhoneNumberFormatter(self.config)
        self.batch_processor = PhoneNumberBatchProcessor(self.config, self.parser, self.formatter)

    async def process_phone_numbers(self, raw_input: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Process multiple phone numbers from a raw text input.
        
        Args:
            raw_input: String containing one or more phone numbers
            
        Returns:
            Tuple containing:
                - List of results for each phone number
                - Statistics dictionary with processing metrics
        """
        logger.info(f"Starting processing: input_length={len(raw_input)}, format={self.config.output_format}, region={self.config.default_region}")
        start = time.time()
        
        # Parse input into individual phone numbers
        nums = self.parser.parse_phone_number_input(raw_input)
        total = len(nums)
        logger.info(f"Total numbers to process: {total}")
        
        # Process numbers in batches
        all_results: List[Dict[str, Any]] = []
        success = error = 0
        
        for i in range(0, total, self.config.batch_size):
            batch = nums[i:i+self.config.batch_size]
            batch_res = await self.batch_processor.process_phone_number_batch(batch, i)
            all_results.extend(batch_res)
            
            # Update counters
            success += sum(1 for r in batch_res if r['success'])
            error += sum(1 for r in batch_res if not r['success'])
            
            # Log progress
            pct = int((i+len(batch))/total*100)
            logger.info(f"Progress {pct}% ({i+len(batch)}/{total})")
        
        # Calculate statistics
        elapsed = time.time() - start
        stats = {
            'total': total, 
            'success': success, 
            'error': error, 
            'elapsed_seconds': elapsed, 
            'numbers_per_second': total/elapsed if elapsed > 0 else 0
        }
        
        logger.info(f"Processing complete: {success} succeeded, {error} failed in {elapsed:.2f}s")
        return all_results, stats