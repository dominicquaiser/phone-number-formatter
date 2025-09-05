"""Basic usage example for phone-number-formatter package."""

import asyncio
from phone_number_formatter import PhoneFormatter, PhoneFormatterConfig

async def main():
    # Basic usage with default configuration
    formatter = PhoneFormatter()
    
    numbers = "+49 30 1234567, 555-123-4567, 0123456789"
    results, stats = await formatter.process_phone_numbers(numbers)
    
    print(f"Processed {stats['total']} numbers:")
    print(f"✓ Success: {stats['success']}")
    print(f"✗ Errors: {stats['error']}")
    
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['input']} → {result['phone_number']}")

if __name__ == "__main__":
    asyncio.run(main())