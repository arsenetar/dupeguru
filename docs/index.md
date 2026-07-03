# dupeGuru System Documentation Index

Welcome to the comprehensive architecture, components, and data flow documentation for **dupeGuru**.

This documentation describes the internal design, software architecture, key subsystems, and data flows of dupeGuru, including its Standard, Music, and Picture editions.

## Documents

The documentation is split into the following sections:

1. **[Architecture & Design Patterns](file:///Users/tinle/src/tinle/opensource/dupeguru/docs/architecture.md)**
   Describes the Clean Architecture/MVP design, the double-decoupling mechanism using custom Broadcaster-Listener pub-sub and generic presenter-view interfaces, and the cross-platform GUI framework abstraction.

2. **[Component Catalog](file:///Users/tinle/src/tinle/opensource/dupeguru/docs/components.md)**
   A detailed walkthrough of the three primary source packages:
   - `core/`: The core business logic, matching engine, and GUI presentation layer.
   - `hscommon/`: Reusable common utilities, GUI base definitions, job progress reporting, and notification infrastructure.
   - `qt/`: The PyQt5-based frontend layout, adapter models, and platform-specific implementations.
   It also details the differences between the Standard Edition (SE), Music Edition (ME), and Picture Edition (PE).

3. **[Data Flow Analysis](file:///Users/tinle/src/tinle/opensource/dupeguru/docs/data_flow.md)**
   A deep dive into the runtime lifecycles and data pipelines:
   - Application Bootstrap & Qt event loop integration.
   - Folder Selection & Scannable File Collection.
   - Duplicate Detection & Scan Pipelines (including hashing & C-based pixel-block comparison).
   - Prioritization & Reference File Selection.
   - Deletion, Renaming, & Custom File Operations.

---
*Created on July 1, 2026.*
