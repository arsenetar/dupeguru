# de-dup Web UI Redesign Plan: "Duplicate Results Studio"

## 1. Problem Statement & Motivation
Currently, the **Scanned Results** table is rendered inside a small, constrained horizontal container at the bottom of the main scan view (`#results-container`). When scans produce thousands of duplicate files or groups, users experience:
* Restricted vertical viewable area (showing only 5-8 rows at a time).
* Truncated horizontal file paths without flexible column resizing or multi-dimensional scrolling.
* Difficulty navigating between large duplicate groups without context switching.
* Cluttered page layout with sidebar and database cards competing for screen space.

---

## 2. Key Design & UX Objectives

### 🎨 Modern Glassmorphic & Full-Viewport Workspace
* **Dedicated "Results Studio" View & Tab**: A dedicated full-viewport workspace tab (`#tab-results-studio`) and full-screen expansion mode (`⤢ Maximize Workspace`).
* **Sidebar Auto-Collapse**: Collapses the left setup sidebar automatically when viewing results, dedicating 100% of screen real estate to results exploration.

### 📜 Dual-Axis Scrollable Grid & Group Navigation Slider
* **Horizontal & Vertical Scroll Containers**: Fixed-header table grid with smooth dual-axis scrolling (`overflow-x: auto; overflow-y: auto; max-height: calc(100vh - 200px)`), sticky table headers (`position: sticky; top: 0; z-index: 10`), and sticky row group headers (`position: sticky; left: 0;`).
* **Duplicate Group Carousel / Slide Navigator**:
  * Visual slider / group quick-jump toolbar ("Group 14 of 1,250") with next/prev slide shortcuts (`[←]` / `[→]`).
  * Group filter cards displaying pivot file, duplicate count, and reclaimable disk space per group.

### 🔍 Interactive Inspection & Bulk Action Toolbar
* **Slide-out File Inspector Panel**: Clicking any duplicate file opens a right-side drawer showing file path details, directory breadcrumbs, exact byte size, modification timestamp, SHA256 digest, and file type preview icon.
* **Smart Filter & Density Controls**:
  * Instant search bar (filter by filename, folder path, or file extension `.mp4`, `.iso`, `.jpg`).
  * Row density toggle (**Compact View**: 28px row height vs **Detailed View**: 48px with path badges).
  * Filter by minimum size (e.g. `> 100 MB`).
* **Sticky Batch Action Floating Footer**:
  * Live status: **"1,420 files marked — 14.8 GB space to reclaim"**.
  * Quick mark actions: **Mark All Duplicates**, **Unmark All**, **Invert Selection**, **Mark All Except Oldest/Newest**.
  * Primary action: **🚀 Delete Marked Files** with safety confirmation modal.

---

## 3. Layout Architecture & Component Hierarchy

```
+-----------------------------------------------------------------------------------------+
| [Logo] de-dup Web   [Scan Console]  [📊 Results Studio]  [Cross-DB]  [Cache DB] [⤢ Full]  |
+-----------------------------------------------------------------------------------------+
| [ Quick Group Slider: ◀ Group 14 of 1,250 ▶ ] [🔍 Search Path...] [Filter: >100MB] [Density] |
+-----------------------------------------------------------------------------------------+
| GROUP #14: ISO_Images/ubuntu-22.04.iso (Size: 4.2 GB, 3 Duplicates, 8.4 GB Reclaimable) |
+---+-------+---------+------------------------------+--------------------+---------------+
| ☐ | Match | Type    | File Name                    | Path               | Size / Date   |
+---+-------+---------+------------------------------+--------------------+---------------+
| 🔘| [Pivot] | 💿 ISO  | ubuntu-22.04-desktop-amd.iso | /storage/backups/  | 4.2 GB / 2024 |
| ☑ | 100%  | 💿 ISO  | ubuntu-22.04-desktop-amd.iso | /downloads/ubuntu/ | 4.2 GB / 2024 |
| ☑ | 100%  | 💿 ISO  | ubuntu-22.04-desktop-amd.iso | /tmp/iso_copy/     | 4.2 GB / 2024 |
+---+-------+---------+------------------------------+--------------------+---------------+
| FOOTER ACTION BAR: Selected 2 files (8.4 GB)  [Mark All Except Pivot] [🗑️ Delete Marked] |
+-----------------------------------------------------------------------------------------+
```

---

## 4. Phased Implementation Roadmap

### Phase 1: Full-Viewport Layout & Tab Navigation
* Add `#tab-results-studio` to top navigation bar.
* Build full-height workspace container with responsive grid layout and sidebar auto-collapse toggle.

### Phase 2: Dual-Axis Table Grid & Sticky Headers
* Refactor `#results-table` with CSS custom scrollbars, sticky column headers, and expandable group cards.
* Implement pagination + virtual scrolling controls for 100,000+ row datasets.

### Phase 3: Group Slider Carousel & Quick Jump Navigation
* Add visual group slider bar, jump-to-group input, and group summary chips.

### Phase 4: Slide-out File Inspector & Smart Filtering
* Build slide-out detail drawer (`#file-inspector-drawer`).
* Implement real-time client-side search filtering by filename, folder path, extension, and minimum byte size.

### Phase 5: Verification & End-to-End Test Suite
* Add unit tests in `core/tests/web_ui_test.py` verifying HTML element IDs, CSS grid properties, tab switching, and REST API payload responses.
