# EpochCN Map Data Gaps

设计标签：B站：天涯路漫

Last checked: 2026-04-23

Compared against Bennylavaa/pfQuest-epoch `a28c6145a805830520caf0a486d0aa9e3f182919`.

## Remaining Epoch Quest Marker Gaps

- `8949` The Instigator's Enchantment `<NYI>`: pfQuest-epoch references unit `45473`, but no coordinates are present. EpochHead confirms the quest is in Tol Barad / Baradin Hold, which is not currently covered by EpochCN's vanilla world map conversion table.
- `8950` The Instigator's Enchantment: pfQuest-epoch references unit `45473` and item `22224`. EpochHead confirms item `22224` drops from Astilos the Hollow in Baradin Hold, but the embedded spawn data is an instance-local point and does not map to the vanilla world map.
- `26330` Dreams of Another Life: EpochHead confirms pickup in Silithus / The Veiled Sea from Tauren Hermit `45315`, but neither pfQuest-epoch nor EpochHead currently exposes precise world-map coordinates for unit `45315` or object `250160`.

## Manual Fixes Added

- `27705` Lorrin Foxfire: added Stonard coordinates from Maczuga/pfQuest-Epoch `db/units-tbc.lua`.
- `28711` Commission for Tyraeth Morningshade: added turn-in markers using existing pfQuest-wotlk coordinates for unit `45976`.
