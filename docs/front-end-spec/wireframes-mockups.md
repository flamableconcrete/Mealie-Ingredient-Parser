# Wireframes & Mockups

**Primary Design Files:** Terminal-based UI (TUI) using Textual framework - no traditional design tool mockups needed. ASCII-based wireframes below represent actual terminal rendering.

## Key Screen Layouts

### PatternGroupScreen (Batch Mode)

**Purpose:** Display grouped ingredient patterns with counts, allowing users to select patterns for batch operations

**Key Elements:**
- Table with sortable columns: Pattern Text, Type (Unit/Food), Count, Status
- Visual distinction between unit patterns and food patterns (grouped sections or color coding)
- Status indicators: Pending (default), Completed (green/checkmark), Skipped (gray/strikethrough)
- Real-time statistics in header: Total Patterns, Completed, Skipped, Pending
- Context-sensitive footer showing available keyboard shortcuts
- Focus indicator on selected row (highlighted/bordered)

**Interaction Notes:**
- Arrow keys for navigation, Enter to open action modal, 's' to skip, 'u' to un-skip, 'd' for progress dashboard
- Table auto-scrolls as patterns are completed to keep pending items visible
- Completed patterns remain in table but grayed out to show progress
- Pressing 'q' returns to RecipeListScreen with all progress preserved

**ASCII Wireframe:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Mealie Ingredient Parser - Batch Mode                                      │
│ Total: 42 patterns | Completed: 15 | Skipped: 3 | Pending: 24             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ UNIT PATTERNS                                                               │
│ ┌───────────────────┬──────┬───────┬────────────────────────────────────┐  │
│ │ Pattern Text      │ Type │ Count │ Status                            │  │
│ ├───────────────────┼──────┼───────┼────────────────────────────────────┤  │
│ │ ✓ tsp             │ Unit │  47   │ ✓ Completed                       │  │
│ │ ✓ cup             │ Unit │  35   │ ✓ Completed                       │  │
│ │ ▶ tbsp            │ Unit │  28   │ ● Pending                         │  │
│ │   oz              │ Unit │  22   │ ● Pending                         │  │
│ │   pinch           │ Unit │  12   │ ● Pending                         │  │
│ │   dash            │ Unit │   8   │ ⊘ Skipped                         │  │
│ └───────────────────┴──────┴───────┴────────────────────────────────────┘  │
│                                                                             │
│ FOOD PATTERNS                                                               │
│ ┌───────────────────┬──────┬───────┬────────────────────────────────────┐  │
│ │ Pattern Text      │ Type │ Count │ Status                            │  │
│ ├───────────────────┼──────┼───────┼────────────────────────────────────┤  │
│ │ ✓ olive oil       │ Food │  42   │ ✓ Completed                       │  │
│ │   chicken breast  │ Food │  31   │ ● Pending                         │  │
│ │   garlic clove    │ Food │  29   │ ● Pending                         │  │
│ │   salt            │ Food │  18   │ ⊘ Skipped                         │  │
│ └───────────────────┴──────┴───────┴────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Enter: Process | s: Skip | u: Un-skip | d: Dashboard | i: Individual | q: Back │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### BatchPreviewScreen (Confirmation Dialog)

**Purpose:** Show all ingredients affected by proposed batch operation, require explicit confirmation before execution

**Key Elements:**
- Header clearly stating the operation type and target (e.g., "Creating unit 'tbsp'" or "Adding alias 'chicken breast' → 'Chicken Breast, Boneless'")
- Table of affected ingredients: Recipe Name, Ingredient Text, Current Status (unparsed)
- Ingredient count prominently displayed ("28 ingredients will be updated")
- Warning if count is very high (50+): "Large batch operation - please review carefully"
- Confirmation buttons: Confirm (Enter/c), Cancel (Esc/x)
- Scrollable table for large ingredient lists

**Interaction Notes:**
- Read-only table - user cannot edit, only review
- Arrow keys scroll through ingredient list if it exceeds screen height
- Clear visual distinction from action modals (different border style, colors)
- Operation is NOT executed until user presses Enter/c
- Esc/x returns to PatternGroupScreen with no changes

**ASCII Wireframe:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BATCH OPERATION PREVIEW                              │
│                                                                             │
│ Creating unit: 'tbsp' (Tablespoon)                                         │
│ 28 ingredients will be updated across 18 recipes                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Recipe Name              │ Ingredient Text                 │ Status    │ │
│ ├──────────────────────────┼─────────────────────────────────┼───────────┤ │
│ │ Chocolate Chip Cookies   │ 2 tbsp butter, softened         │ Unparsed  │ │
│ │ Caesar Salad Dressing    │ 3 tbsp lemon juice              │ Unparsed  │ │
│ │ Garlic Bread             │ 4 tbsp olive oil                │ Unparsed  │ │
│ │ Pasta Carbonara          │ 2 tbsp reserved pasta water     │ Unparsed  │ │
│ │ Marinara Sauce           │ 3 tbsp tomato paste             │ Unparsed  │ │
│ │ Herb Butter              │ 1 tbsp chopped parsley          │ Unparsed  │ │
│ │ Vinaigrette              │ 2 tbsp red wine vinegar         │ Unparsed  │ │
│ │ Pesto                    │ 3 tbsp pine nuts                │ Unparsed  │ │
│ │ ▼ (scroll for 20 more)                                                 │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│                                                                             │
│                 [Confirm - Enter/c]    [Cancel - Esc/x]                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Review the affected ingredients above before confirming                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Progress Dashboard Modal

**Purpose:** Provide detailed statistics on batch processing progress and efficiency metrics

**Key Elements:**
- Overall progress: Total ingredients (parsed/unparsed), patterns (completed/skipped/pending)
- Breakdown by operation type: Units Created, Foods Created, Aliases Added
- Session statistics: Time elapsed, average time per pattern, estimated time remaining
- Recent operations list: Last 5 batch actions with timestamps and counts
- Visual progress bars for completion percentages

**Interaction Notes:**
- Invoked with 'd' key from PatternGroupScreen
- Modal overlay (doesn't replace main screen)
- Read-only information display
- Press any key or Esc to dismiss and return to PatternGroupScreen
- Statistics update in real-time as operations complete

**ASCII Wireframe:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROGRESS DASHBOARD                                  │
│                                                                             │
│ SESSION OVERVIEW                                                            │
│ ├─ Total Ingredients: 487                                                  │
│ │  ├─ Parsed: 342 (70%) ████████████████░░░░░░░░                           │
│ │  └─ Remaining: 145 (30%)                                                 │
│ │                                                                           │
│ ├─ Patterns: 42                                                            │
│ │  ├─ Completed: 15 (36%) ████████░░░░░░░░░░░░░░                           │
│ │  ├─ Skipped: 3 (7%)                                                      │
│ │  └─ Pending: 24 (57%)                                                    │
│                                                                             │
│ OPERATIONS COMPLETED                                                        │
│ ├─ Units Created: 8                                                        │
│ ├─ Foods Created: 4                                                        │
│ └─ Aliases Added: 3                                                        │
│                                                                             │
│ EFFICIENCY METRICS                                                          │
│ ├─ Session Duration: 12m 34s                                               │
│ ├─ Avg Time per Pattern: 50s                                               │
│ └─ Estimated Remaining: ~20 minutes                                        │
│                                                                             │
│ RECENT BATCH OPERATIONS                                                     │
│ ┌───────────┬──────────────────────────────┬───────┬───────────────────┐   │
│ │ Time      │ Operation                    │ Count │ Status            │   │
│ ├───────────┼──────────────────────────────┼───────┼───────────────────┤   │
│ │ 10:45 AM  │ Created unit 'cup'           │  35   │ ✓ Success         │   │
│ │ 10:43 AM  │ Added alias 'olive oil'      │  42   │ ✓ Success         │   │
│ │ 10:41 AM  │ Created food 'Garlic'        │  29   │ ✓ Success         │   │
│ │ 10:38 AM  │ Created unit 'tsp'           │  47   │ ✓ Success         │   │
│ │ 10:35 AM  │ Created unit 'oz'            │  22   │ ⚠ Partial (20/22) │   │
│ └───────────┴──────────────────────────────┴───────┴───────────────────┘   │
│                                                                             │
│                          Press any key to close                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Batch Operation Summary Modal (Post-Execution)

**Purpose:** Confirm successful batch operation and report any failures

**Key Elements:**
- Success/partial success indicator with color coding
- Count of successfully updated ingredients vs. total
- List of failed ingredients (if any) with recipe names and error messages
- "Retry Failed" button if partial failures occurred
- "Continue" button to return to PatternGroupScreen

**Interaction Notes:**
- Appears immediately after batch update completes
- Requires explicit user action to dismiss (no auto-dismiss)
- If all successful: Shows success count, user presses any key to continue
- If partial failures: Remains open, requires user action (Retry or Continue)
- Failed ingredients can be scrolled through if list is long

**ASCII Wireframe (Success):**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                              ✓ SUCCESS                                      │
│                                                                             │
│                    28 ingredients updated successfully                      │
│                                                                             │
│                  Unit 'tbsp' applied to all matching ingredients            │
│                                                                             │
│                                                                             │
│                      Press any key to continue...                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**ASCII Wireframe (Partial Failure):**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ⚠ PARTIAL SUCCESS                                  │
│                                                                             │
│                 20 of 22 ingredients updated successfully                   │
│                           2 failures occurred                               │
│                                                                             │
│ FAILED INGREDIENTS:                                                         │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Recipe Name          │ Ingredient           │ Error                    │ │
│ ├──────────────────────┼──────────────────────┼──────────────────────────┤ │
│ │ Marinara Sauce       │ 3 tbsp tomato paste  │ API timeout (retry #3)   │ │
│ │ Caesar Dressing      │ 2 tbsp lemon juice   │ Ingredient not found     │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│                                                                             │
│                [Retry Failed - r]    [Continue - Enter/c]                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---
