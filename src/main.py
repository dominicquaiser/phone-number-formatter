from __future__ import annotations

import asyncio
from apify import Actor

from .phone_number_formatter.core import PhoneFormatter, PhoneFormatterConfig


async def main() -> None:
    await Actor.init()
    Actor.log.info("Starting phone formatter actor")
    input_data = await Actor.get_input() or {}

    config = PhoneFormatterConfig(
        default_region=input_data.get("countries", "US"),
        output_format=input_data.get("format_to", "E164"),
        batch_size=input_data.get("batch_size", 100),
        max_concurrent_tasks=input_data.get("max_concurrent_tasks", 10),
        rate_limit_per_second=input_data.get("rate_limit", 100.0),
        aggressive_cleaning=input_data.get("aggressive_cleaning", True),
    )
    Actor.log.info(f"Configured with {config}")

    formatter = PhoneFormatter(config)
    raw_numbers = input_data.get("phone_numbers", "")
    results, stats = await formatter.process_phone_numbers(raw_numbers)

    pushed_count = 0
    for result in results:
        await Actor.push_data(result)
        pushed_count += 1

    stats["pushed_count"] = pushed_count

    await Actor.set_value("STATS", stats)
    Actor.log.info(
        f"Processed {stats['total']} numbers: {stats['success']} ok, {stats['error']} failed, {pushed_count} pushed to dataset"
    )
