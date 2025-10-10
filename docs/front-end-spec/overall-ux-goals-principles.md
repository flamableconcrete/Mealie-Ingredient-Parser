# Overall UX Goals & Principles

## Target User Personas

**1. Bulk Migration User**
System administrators or power users performing one-time large-scale migrations from other recipe platforms (e.g., importing 200+ recipes from Paprika, Recipe Keeper). They need to process 500+ unparsed ingredients efficiently and expect the tool to "learn" from their decisions. Technical comfort level: High. Primary pain point: Time investment (current 4+ hour sessions).

**2. Regular Home Cook with Accumulated Backlog**
Casual Mealie users who have accumulated 50-100 unparsed ingredients over months of recipe scraping. They want to clean up their database periodically but find the sequential workflow tedious. Technical comfort level: Medium. Primary pain point: Repetitive decision-making for obvious patterns (e.g., "tsp" appearing 30 times).

**3. Recipe Collection Manager**
Organized users who maintain large recipe databases (500+ recipes) and want to keep data quality high. They prefer batch operations for consistency and appreciate detailed statistics to track progress. Technical comfort level: High. Primary pain point: Database pollution from inconsistent unit/food creation.

## Usability Goals

- **Efficiency of batch operations:** Users can process 500 ingredients in ~15 minutes (vs. 4+ hours in sequential mode)
- **Clarity of action scope:** Users clearly understand whether an action affects one ingredient or many before confirming
- **Error prevention:** Batch operations include preview-before-commit pattern to prevent accidental mass changes
- **Workflow flexibility:** Users can seamlessly switch between batch mode (for patterns) and sequential mode (for edge cases) without losing progress
- **Progress visibility:** Users always know: how many ingredients remain, what's been processed, what's been skipped, and can resume interrupted sessions

## Design Principles

1. **Teach Once, Apply Everywhere** - When users make a decision (e.g., create "tsp" unit), the system should intelligently apply it to all matching cases. Eliminate mechanical repetition.

2. **Preview Before Commit** - Every batch operation shows affected ingredients in a confirmation screen. Users should never be surprised by the scope of their actions.

3. **Keyboard-First, Always** - All workflows accessible via single-key shortcuts. Power users should never need to reach for a mouse. Sequential navigation with clear visual focus indicators.

4. **Progressive Disclosure** - Start with pattern groups (high-level view), drill down to individual ingredients only when needed. Don't overwhelm with detail until requested.

5. **Fail Gracefully, Continue Forward** - Transient API errors shouldn't halt entire batch operations. Collect failures, report clearly, allow retry of failed subset.

## Change Log

| Date       | Version | Description                                      | Author              |
|------------|---------|--------------------------------------------------|---------------------|
| 2025-10-07 | 1.0     | Initial UI/UX specification for batch processing | Sally (UX Expert)   |

---
