# Phone Number Formatter

**Easily parse, validate, and format phone numbers in bulk. Supports various international formats (E.164, International, National, RFC3966)**

This [Apify actor](https://apify.com/azquaier/phone-number-formatter) takes a list of raw phone numbers, cleans them, and formats them according to your specified regional settings and desired output format. It's built for efficiency with configurable batch processing, concurrency, and rate limiting. The core logic is also available as a Python class for easy integration into your own projects.

### 🚀 Features

* **Bulk Processing:** Efficiently handles large lists of phone numbers provided as a single string (separated by commas, semicolons, or new lines).
* **Multiple Output Formats:** Format numbers to standard outputs:
    * `E164` (e.g., +16502530000)
    * `INTERNATIONAL` (e.g., +1 650-253-0000)
    * `NATIONAL` (e.g., (650) 253-0000)
    * `RFC3966` (e.g., tel:+1-650-253-0000)
* **Flexible Input:** Accepts phone numbers in various common formats.
* **Default Region Specification:** Set a default country/region (ISO 3166-1 alpha-2 code) for parsing numbers lacking an explicit country code.
* **Open Source & Integrable:** Core logic is available for direct use in your Python applications.

### 🎯 Use Cases

This tool is ideal for:

- Standardizing phone number datasets for CRMs or databases.
- Validating and cleaning user-provided phone numbers in applications.
- Preparing phone number lists for SMS or calling campaigns.
- Data migration projects requiring consistent phone number formatting.
- **Cost-Effective Automation:** Use the Apify API endpoint in automation workflows (e.g., Zapier, Make/Integromat) to format numbers. This can be significantly cheaper than using built-in formatting steps in some platforms, especially for thousands of numbers and for Zapier's Python module provides better formatting since it doesn't allow external library imports like `phonenumbers`.
- Any workflow where phone numbers from various sources need to be normalized.

## For Apify Users

### 📥 Input Parameters

The actor accepts the following input fields. You can provide these as a JSON object when running on the Apify platform or modifying the input configuration.

| Field                  | Type    | Description                                                                                                            | Default Value                                | Required |
| :--------------------- | :------ | :--------------------------------------------------------------------------------------------------------------------- | :------------------------------------------- | :------- |
| `phone_numbers`        | string  | A single string containing phone numbers to format, separated by commas (,), semicolons (;), or new lines (\n).        | `"+49 30 1234567, 555-123-4567, 0123456789"` | Yes      |
| `format_to`            | string  | The desired output format. Options: `E164`, `INTERNATIONAL`, `NATIONAL`, `RFC3966`.                                    | `"E164"`                                     | Yes      |
| `countries`            | string  | The default ISO 3166-1 alpha-2 country code to assume for numbers without an explicit country code (e.g., "US", "GB"). | `"US"`                                       | Yes      |

*For a full list of supported country codes for the `countries` field, please refer to the `input_schema.json` file or common ISO 3166-1 alpha-2 code lists.*

#### **Example Input JSON:**
```json
{
  "phone_numbers": "+44 20 7946 0958; 01632 960984; 415-555-2671\n+1-202-555-0125, (02) 9999 8888",
  "format_to": "INTERNATIONAL",
  "countries": "GB",
  "aggressive_cleaning": true
}
```

### 📤 Output Data Structure

#### **Example Output Item:**
```json
{
  "index": 0,
  "input": "+44 20 7946 0958",
  "phone_number": "+44 20 7946 0958",
  "success": true,
  "error": null
}
```

### 🤖 Other Actors

🔗 Combine with Other Actors for Powerful Workflows.

You can enhance your data processing pipelines by combining this Phone Number Formatter with other Apify actors.

For example, you might also check out the Gelbe Seiten **[German Yellow Pages Scraper](https://apify.com/azquaier/gelbe-seiten-german-yellow-pages-scraper)** Scraper:

This actor is designed to extract business listings from gelbeseiten.de, which often include phone numbers. After using the Gelbe Seiten Scraper to gather business contact details, you can then use this Phone Number Formatter to automatically clean, validate, and standardize those extracted phone numbers into your desired format (e.g., E.164 for CRMs or international format for outreach lists). This creates a powerful workflow for lead generation and data enrichment where raw contact data is collected and then uniformly formatted for consistent use.

### 💲 Pricing

**1000 results = $0.5**

## Using the Code from GitHub (Local or Integration)

The core logic of this phone number formatter can be used directly in your Python projects or run locally via the provided CLI script.

### 📋 Requirements

- Python 3.x (e.g., 3.8+)
- `phonenumbers` library
- (Optional, for Apify integration) `apify-sdk`

### 🐍 Integrating into Your Python Code

The primary classes for integration are `PhoneFormatterConfig` and `PhoneFormatter` located in `phone_number_formatter.py`.

**Basic Usage Example:**
```python
import asyncio
from phone_number_formatter import PhoneFormatter, PhoneFormatterConfig

async def format_my_numbers(raw_numbers_string):
	config = PhoneFormatterConfig(
	    default_region="US",
	    output_format="E164",
	    batch_size=100,
	    max_concurrent_tasks=10,
	    rate_limit_per_second=50.0,
	    backoff_factor=1.5,
	    max_retries=3,
	    aggressive_cleaning=False
	)
    formatter = PhoneFormatter(config)

    results, stats = await formatter.process_phone_numbers(raw_numbers_string)

    for result in results:
        if result['success']:
            print(f"Input: {result['input']}, Formatted: {result['phone_number']}")
        else:
            print(f"Input: {result['input']}, Error: {result.get('error', 'Unknown error')}")

    print(f"\nStats: {stats}")

if __name__ == '__main__':
    asyncio.run(format_my_numbers(raw_numbers_string))
```

### 🖥️ Running Locally

A command-line interface (`format_phone_numbers.py`) is provided for local testing and use.

**Commands:**

- `format`: Format phone numbers from a direct JSON string input or a JSON file.
- `csv`: Format phone numbers from a specific column in a CSV file.

**Example CLI Usage:**

1. **Format from JSON string:**
```bash
python format_phone_numbers.py format \
--run_input '{"phone_numbers": "+49 30 1234567, 555-123-4567", "format_to": "E164", "countries": "DE"}' \
--output output.json
```

2. **Format from JSON file (`input.json`):**
```bash
python format_phone_numbers.py format --run_input input.json --output output.json
```
    
3. **Format from CSV file (`numbers.csv`, column `phone_col`):**
```bash
python format_phone_numbers.py csv \
--csv numbers.csv --column phone_col \
--format_to INTERNATIONAL --countries GB \
--output output.csv
```

For detailed CLI options, run:
``` bash
python format_phone_numbers.py --help
python format_phone_numbers.py format --help
python format_phone_numbers.py csv --help
```

### 🛠️ Maintainer

- **Author**: Dominic M. Quaiser
- **Contact**: [mail@dominic-quaiser.io](mailto:mail@dominic-quaiser.io)
- **Website**: [dominic-quaiser.io](https://dominic-quaiser.io/)