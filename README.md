# Phone Number Formatter

**Easily parse, validate, and format phone numbers in bulk. Available as both an Apify actor and a standalone Python package.**

This versatile phone number formatting utility supports various international formats (E.164, International, National, RFC3966) and is built for efficiency with configurable batch processing, concurrency, and rate limiting. 

Use it as an [Apify actor](https://apify.com/dominic-quaiser/phone-number-formatter) for automated workflows, install it as a Python package for programmatic use, or run it as a CLI tool for local processing.

## 🚀 Features

* **Multiple Distribution Methods:** Use as Apify actor, Python package, or CLI tool
* **Bulk Processing:** Efficiently handles large lists of phone numbers with configurable batching
* **Multiple Output Formats:** Support for standard formats:
    * `E164` (e.g., +16502530000)
    * `INTERNATIONAL` (e.g., +1 650-253-0000)
    * `NATIONAL` (e.g., (650) 253-0000)
    * `RFC3966` (e.g., tel:+1-650-253-0000)
* **Flexible Input:** Accepts phone numbers in various common formats
* **Regional Support:** Set default country/region (ISO 3166-1 alpha-2) for numbers without country codes
* **Performance Optimized:** Concurrent processing with rate limiting and retry mechanisms
* **Open Source:** MIT licensed with full source code available

## 🎯 Use Cases

This tool is ideal for:

- **Data Standardization:** Normalize phone numbers in CRMs, databases, and datasets
- **Application Validation:** Clean and validate user-provided phone numbers
- **Marketing Campaigns:** Prepare phone lists for SMS or calling campaigns  
- **Data Migration:** Ensure consistent formatting across system migrations
- **Cost-Effective Automation:** Integrate with workflow platforms (Zapier, Make) as a cheaper alternative to built-in formatting tools
- **Bulk Processing:** Handle thousands of numbers efficiently via API or batch processing

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

For example, you might also check out the Gelbe Seiten **[German Yellow Pages Scraper](https://apify.com/dominic-quaiser/gelbe-seiten-german-yellow-pages-scraper)** Scraper:

This actor is designed to extract business listings from gelbeseiten.de, which often include phone numbers. After using the Gelbe Seiten Scraper to gather business contact details, you can then use this Phone Number Formatter to automatically clean, validate, and standardize those extracted phone numbers into your desired format (e.g., E.164 for CRMs or international format for outreach lists). This creates a powerful workflow for lead generation and data enrichment where raw contact data is collected and then uniformly formatted for consistent use.

### 💲 Pricing

**1000 results = $0.08**

## Using the Code from GitHub (Local or Package)

The core logic of this phone number formatter can be used directly in your Python projects or run locally via the provided CLI script.

### 📋 Requirements

- Python 3.8+
- `phonenumbers` library
- Optional: `apify` SDK for actor functionality

### 📦 Installation & Usage

#### As a Python Package

```bash
git clone https://github.com/dominicquaiser/phone-number-formatter.git
cd phone-number-formatter
pip install -e .
```

**Basic Usage:**
```python
import asyncio
from phone_number_formatter import PhoneFormatter, PhoneFormatterConfig

async def format_numbers():
    # Simple usage with defaults
    formatter = PhoneFormatter()
    results, stats = await formatter.process_phone_numbers(
        "+49 30 1234567, 555-123-4567, 0123456789"
    )
    
    # Custom configuration
    config = PhoneFormatterConfig(
        default_region="GB",
        output_format="INTERNATIONAL",
        batch_size=50,
        max_concurrent_tasks=5
    )
    formatter = PhoneFormatter(config)
    results, stats = await formatter.process_phone_numbers(numbers)

asyncio.run(format_numbers())
```

#### As a CLI Tool

```bash
# Format from direct input
phone-formatter format \
  --run_input '{"phone_numbers": "+1-555-123-4567", "format_to": "E164", "countries": "US"}' \
  --output results.json

# Format from CSV file
phone-formatter csv \
  --csv numbers.csv --column phone_number \
  --format_to INTERNATIONAL --countries GB \
  --output formatted.json
```

#### As an Apify Actor

Deploy to the Apify platform or run via API:

```bash
# Via Apify CLI
apify run

# Via API
curl -X POST https://api.apify.com/v2/acts/azquaier~phone-number-formatter/runs \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone_numbers": "+1-555-123-4567", "format_to": "E164", "countries": "US"}'
```

## 📄 License

MIT License - see [LICENSE](https://github.com/dominicquaiser/Phone-Number-Formatter?tab=MIT-1-ov-file) file for details.

## 🛠️ Maintainer

- **Author**: Dominic M. Quaiser
- **Contact**: [mail@dominic-quaiser.io](mailto:mail@dominic-quaiser.io)
- **Website**: [dominic-quaiser.io](https://dominic-quaiser.io/)