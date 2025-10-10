# Component Library / Design System

**Design System Approach:** Leverage Textual framework's built-in widgets with customized styling via CSS. Maintain consistency with existing application components (CreateUnitModal, CreateFoodModal, SelectFoodModal) while extending for batch operations.

## Core Components

### DataTable (Pattern Display)

**Purpose:** Display grouped patterns with sortable columns and status indicators

**Variants:**
- Pattern table (PatternGroupScreen): Columns for Pattern Text, Type, Count, Status
- Ingredient preview table (BatchPreviewScreen): Columns for Recipe Name, Ingredient Text, Status
- Operations history table (Progress Dashboard): Columns for Time, Operation, Count, Status

**States:**
- Row focused: Highlighted border, visual focus indicator (▶ symbol)
- Row completed: Grayed out text, checkmark in status column
- Row skipped: Strikethrough text, dimmed color, skip symbol (⊘)
- Row pending: Normal styling, pending indicator (●)

**Usage Guidelines:** Tables must support keyboard navigation (arrow keys), visual focus indicators for accessibility, and scrolling for large datasets. Sort functionality optional for pattern tables (by count descending), not needed for preview tables.

---

### StatusBadge (Pattern/Operation Status)

**Purpose:** Visual indicator for item status (pending, completed, skipped, partial success)

**Variants:**
- Pending: ● symbol, neutral color (white/gray)
- Completed: ✓ symbol, success color (green)
- Skipped: ⊘ symbol, muted color (dark gray)
- Partial Success: ⚠ symbol, warning color (yellow/orange)
- Error: ✗ symbol, error color (red)

**States:** Static display only, no interactive states

**Usage Guidelines:** Always pair symbol with text label (e.g., "● Pending" not just "●") for screen reader accessibility. Use consistent symbols across all screens.

---

### Modal (Action Selection & Confirmation)

**Purpose:** Overlay dialogs for user input, confirmations, and error messages

**Variants:**
- Action Modal (small): Pattern action selection (Create/Alias/Skip)
- Preview Modal (large): BatchPreviewScreen with ingredient table
- Dashboard Modal (medium): Progress statistics display
- Summary Modal (small/medium): Post-operation success/failure reporting
- Error Modal (small): Validation errors, API failures

**States:**
- Active: Border highlighted, accepts keyboard input
- Dismissible: Esc key closes (except for required confirmations)

**Usage Guidelines:** Modals must have clear titles, visual hierarchy (header/body/footer), and explicit action buttons with keyboard shortcuts shown. Large modals (preview, dashboard) need scroll support. All modals require explicit dismissal action (no auto-close).

---

### ProgressBar (Completion Indicators)

**Purpose:** Visual representation of progress percentage for ingredients, patterns, operations

**Variants:**
- Horizontal bar: `████████░░░░` style with percentage text
- Compact inline: Used in dashboard statistics
- Multi-segment: For showing completed vs. skipped vs. pending in same bar

**States:**
- In progress: Partially filled
- Complete: Fully filled (100%)
- Error/warning: Different color fill for failed operations

**Usage Guidelines:** Always include percentage text alongside visual bar (e.g., "342/487 (70%)"). Use ASCII block characters (█ ░) for terminal compatibility. Ensure sufficient contrast between filled/unfilled sections.

---

### StatisticDisplay (Metrics & Counts)

**Purpose:** Formatted display of numerical statistics with labels

**Variants:**
- Count with label: "Total Ingredients: 487"
- Breakdown list: Indented tree structure (├─ └─) showing subcounts
- Efficiency metrics: Duration, averages, estimates

**States:** Static display, no interactive states

**Usage Guidelines:** Use tree structure symbols (├─ └─ │) for nested relationships. Right-align numbers for easy scanning. Include units for time values (m, s, hours).

---

### HelpFooter (Keyboard Shortcuts)

**Purpose:** Context-sensitive display of available keyboard shortcuts

**Variants:**
- Pattern screen footer: "Enter: Process | s: Skip | u: Un-skip | d: Dashboard | i: Individual | q: Back"
- Preview screen footer: "Enter/c: Confirm | Esc/x: Cancel"
- Modal footer: "Any key to close" or specific shortcuts

**States:**
- Context changes based on current screen/mode
- Updates dynamically as selections change

**Usage Guidelines:** Separate shortcuts with | character. Show key first, then action description. Keep descriptions concise (1-2 words). Update footer when user context changes (e.g., skipped pattern selected → show 'u: Un-skip').

---
