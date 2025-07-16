from __future__ import annotations

import asyncio
from apify import Actor

from .phone_number_formatter import PhoneFormatter, PhoneFormatterConfig


async def main() -> None:
    await Actor.init()
    Actor.log.info("Starting phone formatter actor")
    input_data = await Actor.get_input() or {}
    
    config = PhoneFormatterConfig(
        default_region=input_data.get('countries', 'US'),
        output_format=input_data.get('format_to', 'E164'),
        batch_size=input_data.get('batch_size', 100),
        max_concurrent_tasks=input_data.get('max_concurrent_tasks', 10),
        rate_limit_per_second=input_data.get('rate_limit', 100.0),
        aggressive_cleaning=input_data.get('aggressive_cleaning', True)
    )
    Actor.log.info(f"Configured with {config}")
    
    # Check for paid dataset limit
    paid_limit = Actor.config.max_paid_dataset_items
    if paid_limit:
        Actor.log.info(f"Paid dataset limit detected: {paid_limit} items maximum will be charged")
    
    formatter = PhoneFormatter(config)
    raw_numbers = input_data.get('phone_numbers', '')
    results, stats = await formatter.process_phone_numbers(raw_numbers)
    
    # Process results with paid limit checking
    default_dataset = await Actor.open_dataset()
    pushed_count = 0
    
    for result in results:
        # Check current dataset size before pushing each item
        if paid_limit:
            dataset_info = await default_dataset.get_info()
            current_items = dataset_info.item_count if dataset_info else 0
            
            if current_items >= paid_limit:
                Actor.log.info(f"Reached paid dataset limit of {paid_limit} items. Stopping data push.")
                break
        
        await Actor.push_data(result)
        pushed_count += 1
    
    # Update stats to reflect what was actually pushed
    if pushed_count < stats['total']:
        Actor.log.info(f"Limited by paid dataset quota: pushed {pushed_count} out of {stats['total']} processed results")
        stats['pushed_count'] = pushed_count
        stats['limited_by_quota'] = True
    else:
        stats['pushed_count'] = pushed_count
        stats['limited_by_quota'] = False
    
    await Actor.set_value('STATS', stats)
    Actor.log.info(f"Processed {stats['total']} numbers: {stats['success']} ok, {stats['error']} failed, {pushed_count} pushed to dataset")