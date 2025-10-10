# Story 2.4: Add Pattern Skip and Defer Functionality

**As a** user,
**I want** to skip uncertain patterns and defer them for later review,
**so that** I can focus on high-confidence batch operations first.

## Acceptance Criteria

1. From PatternGroupScreen, pressing 's' on selected pattern marks it as "Skipped" and moves to next pattern
2. Skipped patterns remain visible in table with distinct visual styling (grayed out or strikethrough)
3. User can un-skip patterns by selecting and pressing 'u' (undo skip)
4. Action modal includes "Skip Pattern" option alongside Create/Alias options
5. Status bar tracks skipped count separately from completed count
6. When all pending patterns processed, screen shows summary: "X completed, Y skipped. Press 'r' to review skipped patterns or 'q' to return."
