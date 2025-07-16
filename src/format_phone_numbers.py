#!/usr/bin/env python3
"""
phone_number_formatter.py

A simple local CLI for PhoneFormatter (without Apify).

Commands:
  format      Format phone numbers from direct input or JSON file
  csv         Format phone numbers from a CSV file

Example Usage:
  # Format direct input via JSON string
  python phone_number_formatter.py format \
    --run_input '{"phone_numbers": "+49 30 1234567, 555-123-4567", "format_to": "E164", "countries": "DE"}' \
    --output out.json

  # Format from JSON file
  python phone_number_formatter.py format --run_input config.json --output out.json

  # Format from CSV column
  python phone_number_formatter.py csv \
    --csv numbers.csv --column phone_number \
    --format_to INTERNATIONAL --countries GB \
    --output results.json
"""
import argparse
import asyncio
import csv
import json

from phone_number_formatter import PhoneFormatter, PhoneFormatterConfig


async def format_from_input(run_input: dict, output: str | None = None):
    """
    Format phone numbers based on run_input dict and handle output.

    Args:
        run_input: Dict with keys:
            phone_numbers (str): comma-separated phone numbers
            format_to (str): output format key
            countries (str): default region code
        output: Optional path to write JSON results; if None, print to stdout
    """
    config = PhoneFormatterConfig(
        default_region=run_input.get('countries', 'US'),
        output_format=run_input.get('format_to', 'E164'),
    )
    formatter = PhoneFormatter(config)
    results, stats = await formatter.process_phone_numbers(
        run_input.get('phone_numbers', '')
    )
    data = {'results': results, 'stats': stats}
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Output written to {output}")
    else:
        print(json.dumps(data, indent=2))


async def format_from_csv(path: str, column: str, format_to: str, countries: str, output: str | None = None):
    """
    Read phone numbers from a CSV file, format them, and handle output.

    Args:
        path: Path to the CSV file
        column: Column name containing phone numbers
        format_to: Desired output format
        countries: Default region code
        output: Optional path to write JSON results; if None, print to stdout
    """
    numbers = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = row.get(column, '').strip()
            if val:
                numbers.append(val)
    run_input = {
        'phone_numbers': ','.join(numbers),
        'format_to': format_to,
        'countries': countries,
    }
    await format_from_input(run_input, output)


def main():
    """
    Entry point for the CLI.

    Use subcommands 'format' or 'csv'.
    """
    parser = argparse.ArgumentParser(
        description='Local phone formatter CLI'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # format command
    fmt_parser = subparsers.add_parser('format', help='Format from direct or JSON input')
    fmt_parser.add_argument(
        '--run_input', type=str, required=True,
        help="JSON string or path to JSON file with keys: phone_numbers, format_to, countries"
    )
    fmt_parser.add_argument(
        '--output', type=str, default=None,
        help='Optional file path to write JSON output'
    )

    # csv command
    csv_parser = subparsers.add_parser('csv', help='Format from CSV file')
    csv_parser.add_argument(
        '--csv', type=str, required=True,
        help='Path to CSV file containing phone numbers'
    )
    csv_parser.add_argument(
        '--column', type=str, default='phone',
        help='CSV column name for phone numbers'
    )
    csv_parser.add_argument(
        '--format_to', type=str, default='E164',
        help='Desired output format'
    )
    csv_parser.add_argument(
        '--countries', type=str, default='US',
        help='Default region code'
    )
    csv_parser.add_argument(
        '--output', type=str, default=None,
        help='Optional file path to write JSON output'
    )

    args = parser.parse_args()

    if args.command == 'format':
        try:
            with open(args.run_input) as rf:
                run_input = json.load(rf)
        except (FileNotFoundError, json.JSONDecodeError):
            run_input = json.loads(args.run_input)
        asyncio.run(format_from_input(run_input, args.output))

    elif args.command == 'csv':
        asyncio.run(
            format_from_csv(
                args.csv, args.column, args.format_to, args.countries, args.output
            )
        )


if __name__ == '__main__':
    main()