# Goals and Background Context

## Goals

- Enable batch processing of unparsed ingredients across multiple recipes through pattern recognition and intelligent grouping
- Reduce ingredient parsing time from 4+ hours to ~15 minutes for typical bulk import scenarios (500 ingredients)
- Preserve human decision-making quality while eliminating 90% of repetitive modal interactions
- Prevent Mealie database pollution by ensuring consistent unit/food creation decisions across similar ingredients
- Provide visibility into parsing patterns (e.g., "this unit appears in 47 ingredients") to inform better decisions
- Maintain compatibility with existing Mealie API and data structures without requiring Mealie core modifications

## Background Context

Mealie's current ingredient parsing workflow operates sequentially—one ingredient at a time through multiple modal dialogs. This approach works adequately for users adding 5-10 recipes weekly but breaks down catastrophically for bulk scenarios: migrations from other platforms, large scraping campaigns, or accumulated backlogs. Users face 4+ hours of repetitive clicking to process 500 unparsed ingredients, with the same units (e.g., "tsp", "cup") and foods (e.g., "chicken breast") requiring separate decisions across dozens of recipes. This friction creates database pollution through inconsistent duplicate entries, decision fatigue, and often leads users to accept partially-parsed databases rather than complete the cleanup.

The existing Mealie Ingredient Parser TUI already provides a foundation for sequential processing. This PRD focuses on enhancing it with intelligent batch operations that recognize patterns across ingredients—allowing users to create a unit or food once and automatically apply it to all matching instances. This transformation preserves human oversight for ambiguous cases while eliminating the mechanical repetition that makes large-scale parsing unsustainable.

See [brief.md](brief.md) for detailed user research and problem analysis.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-07 | 1.0 | Initial PRD creation | John (PM Agent) |
| 2025-10-07 | 1.1 | Added scope boundaries, security NFR, deployment notes, checklist validation, next steps prompts | John (PM Agent) |

---
