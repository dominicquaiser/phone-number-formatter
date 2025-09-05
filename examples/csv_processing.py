"""CSV processing example."""

import asyncio
import csv
from phone_number_formatter import PhoneFormatter, PhoneFormatterConfig

async def process_csv(file_path: str, phone_column: str = 'phone'):
    """Process phone numbers from a CSV file."""
    
    # Read numbers from CSV
    numbers = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if phone_column in row and row[phone_column].strip():
                numbers.append(row[phone_column].strip())
    
    # Configure formatter for international format
    config = PhoneFormatterConfig(
        default_region='US',
        output_format='INTERNATIONAL',
        batch_size=50,
        max_concurrent_tasks=5
    )
    
    formatter = PhoneFormatter(config)
    results, stats = await formatter.process_phone_numbers(', '.join(numbers))
    
    # Save results
    with open('formatted_numbers.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['original', 'formatted', 'success', 'error']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'original': result['input'],
                'formatted': result['phone_number'],
                'success': result['success'],
                'error': result.get('error', '')
            })
    
    print(f"Processed {len(numbers)} numbers from {file_path}")
    print(f"Results saved to formatted_numbers.csv")

if __name__ == "__main__":
    # Usage: python csv_processing.py
    asyncio.run(process_csv('input.csv', 'phone_number'))