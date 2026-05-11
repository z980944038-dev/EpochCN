# EpochHead Item Snapshot

This directory stores the raw Project Epoch item data captured from EpochHead.
Keep it under version control: it is source material for item names, auction-house
translation, tooltip green-line translation, categories, item levels, and future
localization work.

- `list.json`: complete `/items` index, 335 pages / 16706 items.
- `items.json`: resumed detail snapshot. Each row may include `description`,
  `tooltip`, and `green`. `tooltip` is the full visible tooltip line list with
  raw text and color classification; `green` is kept as a compatibility shortcut.
- `manifest.json`: counts, source URLs, schema, and file hashes.

Use `Tools/scrape_epochhead_items.js` to resume details. Rows captured before the
full-tooltip schema may only have `green`; the scraper treats those as incomplete
and refetches them until `tooltip` is present. The scraper writes both the ignored
working cache under `Tools/cache/epochhead_items/` and this committed snapshot
directory, so completed rows do not need to be scraped again.
