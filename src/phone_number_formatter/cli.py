"""
Enhanced CLI for Phone Number Formatter

Commands:
  format      Format phone numbers from direct input or JSON file
  csv         Format phone numbers from a CSV file

Example Usage:
  # Get help and version
  phone-formatter --help
  phone-formatter --version

  # Format direct input via JSON string
  phone-formatter format \
    --run_input '{"phone_numbers": "+49 30 1234567, 555-123-4567", "format_to": "E164", "countries": "DE"}' \
    --output out.json

  # Format from JSON file
  phone-formatter format --run_input config.json --output out.json

  # Format from CSV column
  phone-formatter csv \
    --csv numbers.csv --column phone_number \
    --format_to INTERNATIONAL --countries GB \
    --output results.json
"""
import argparse
import asyncio
import csv
import json
import sys
from typing import Optional

from .core import PhoneFormatter, PhoneFormatterConfig
from . import __version__


async def format_from_input(run_input: dict, output: Optional[str] = None):
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


async def format_from_csv(path: str, column: str, format_to: str, countries: str, output: Optional[str] = None):
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
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                val = row.get(column, '').strip()
                if val:
                    numbers.append(val)
    except FileNotFoundError:
        print(f"Error: CSV file '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not numbers:
        print(f"Warning: No phone numbers found in column '{column}' of '{path}'.")
        return
    
    run_input = {
        'phone_numbers': ','.join(numbers),
        'format_to': format_to,
        'countries': countries,
    }
    await format_from_input(run_input, output)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='phone-formatter',
        description='Format phone numbers in bulk across different regions and formats.',
        epilog='For more information, visit: https://github.com/dominicquaiser/phone-number-formatter'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'%(prog)s {__version__}'
    )
    
    subparsers = parser.add_subparsers(
        dest='command', 
        help='Available commands',
        required=True,
        metavar='COMMAND'
    )

    # format command
    fmt_parser = subparsers.add_parser(
        'format', 
        help='Format phone numbers from direct input or JSON file',
        description='Format phone numbers provided as JSON string or from a JSON configuration file.',
        epilog='Example: phone-formatter format --run_input \'{"phone_numbers": "+1-555-123-4567", "format_to": "E164", "countries": "US"}\''
    )
    fmt_parser.add_argument(
        '--run_input', 
        type=str, 
        required=True,
        help='JSON string or path to JSON file with keys: phone_numbers, format_to, countries'
    )
    fmt_parser.add_argument(
        '--output', 
        type=str, 
        default=None,
        help='Optional file path to write JSON output (default: stdout)'
    )

    # csv command
    csv_parser = subparsers.add_parser(
        'csv', 
        help='Format phone numbers from CSV file',
        description='Read phone numbers from a CSV file column and format them.',
        epilog='Example: phone-formatter csv --csv data.csv --column phone --format_to INTERNATIONAL --countries US'
    )
    csv_parser.add_argument(
        '--csv', 
        type=str, 
        required=True,
        help='Path to CSV file containing phone numbers'
    )
    csv_parser.add_argument(
        '--column', 
        type=str, 
        default='phone',
        help='CSV column name containing phone numbers (default: phone)'
    )
    csv_parser.add_argument(
        '--format_to', 
        type=str, 
        default='E164',
        choices=['E164', 'INTERNATIONAL', 'NATIONAL', 'RFC3966'],
        help='Desired output format (default: E164)'
    )
    csv_parser.add_argument(
        '--countries', 
        type=str, 
        default='US',
        help='Default ISO 3166-1 alpha-2 region code (default: US)'
    )
    csv_parser.add_argument(
        '--output', 
        type=str, 
        default=None,
        help='Optional file path to write JSON output (default: stdout)'
    )
    
    return parser


def main():
    """
    Entry point for the CLI.
    
    Supports subcommands 'format' and 'csv' with comprehensive help and error handling.
    """
    parser = create_parser()
    
    # Handle case where no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    try:
        args = parser.parse_args()
    except SystemExit:
        # argparse already handled help/error messages
        raise

    try:
        if args.command == 'format':
            # Try to parse as JSON file first, then as JSON string
            try:
                with open(args.run_input, 'r', encoding='utf-8') as f:
                    run_input = json.load(f)
                print(f"Loaded configuration from file: {args.run_input}")
            except (FileNotFoundError, json.JSONDecodeError, IsADirectoryError):
                try:
                    run_input = json.loads(args.run_input)
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON in --run_input: {e}", file=sys.stderr)
                    print("Expected format: '{\"phone_numbers\": \"...\", \"format_to\": \"...\", \"countries\": \"...\"}}'", file=sys.stderr)
                    sys.exit(1)
            
            asyncio.run(format_from_input(run_input, args.output))

        elif args.command == 'csv':
            asyncio.run(
                format_from_csv(
                    args.csv, args.column, args.format_to, args.countries, args.output
                )
            )

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()