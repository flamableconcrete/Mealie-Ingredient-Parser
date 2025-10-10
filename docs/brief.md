# Project Brief: Mealie Ingredient Parser TUI Enhancements

## Executive Summary

**Mealie Ingredient Parser TUI** addresses the workflow mismatch between bulk recipe imports and sequential ingredient resolution in Mealie instances. When users import recipes in bulk, unparsed ingredients create broken shopping lists, failed recipe scaling, and dysfunctional search—but resolving them one-by-one through hundreds of modals is prohibitively tedious. This enhanced TUI introduces intelligent batch operations that let users create recurring units/foods once and auto-apply them across all matching ingredients, transforming a multi-hour sequential task into a 15-minute batch workflow. Target users are Mealie self-hosters managing recipe databases post-migration or after bulk imports. The key value proposition is preserving human decision-making quality while eliminating 90% of repetitive clicks through pattern-based batch processing.

---

## Problem Statement

### Current State and Pain Points

Mealie's current ingredient parsing workflow operates on a sequential, one-ingredient-at-a-time model. This works well for small-scale recipe additions but creates significant friction for bulk scenarios (migrations, scraping campaigns, or even weekly recipe batches). Users encounter:

- **Volume overload:** Hundreds of unparsed ingredients requiring individual review
- **Extreme repetition:** The same unit (e.g., "tsp", "tablespoon", "cup") appears across dozens of recipes but must be addressed each time it's encountered through separate modal dialogs
- **Modal fatigue:** Each ingredient requires navigating through 3-5 modal interactions (unit action → create unit → food action → create/select food → confirmation)
- **Lost context:** No visibility into "how many more times will I see this unit/food?" when making decisions
- **No pattern recognition:** Tool treats "chicken breast", "chicken breasts", and "boneless chicken breast" as entirely separate decisions despite obvious relationships

### Impact of the Problem

**Time impact (quantified):**
- Current workflow: ~30 seconds per ingredient × 500 ingredients = 4+ hours of active clicking
- This often extends across multiple sessions as decision fatigue sets in
- Error correction (fixing accidental duplicates) adds uncounted overhead

**Quality impact:**
- Inconsistent decisions due to fatigue ("I created 'tsp' as an alias earlier, now I'm creating it as a new unit")
- Mealie database becomes polluted with duplicate units/foods created accidentally
- Users may accept partially unparsed databases to avoid cleanup friction (unvalidated but likely based on friction severity)

**Functional impact:**
- Shopping lists combine only parsed ingredients, forcing manual additions for unparsed items
- Recipe scaling only works for fully parsed recipes
- Nutrition tracking fails for unparsed ingredients
- Cross-recipe search (e.g., "find all chicken recipes") misses unparsed instances

### Why Existing Solutions Fall Short

1. **Current TUI (existing tool):** Excellent for processing 10-20 ingredients, becomes unsustainable at scale due to lack of batch operations and pattern recognition
2. **Mealie web UI:** Even slower—requires full page navigation between each ingredient decision
3. **Manual database editing:** Technically possible but requires SQL knowledge and bypasses Mealie's validation logic
4. **Improving NLP parser alone:** While better parsing reduces volume, human decisions are still needed for:
   - Ambiguous cases (aliases vs. new foods, regional variations)
   - User-specific taxonomy preferences ("I want all pasta types as aliases to 'pasta', not separate foods")
   - Quality control / validation of automated decisions
   - Even with hypothetical perfect NLP, users need efficient bulk review/correction tools

### Urgency and Importance

**Why now:**
- Mealie's popularity is growing (active self-hosted community, frequent bulk migrations from other platforms)
- The cleanup friction creates a significant adoption barrier that may cause users to abandon systematic recipe organization
- The existing TUI architecture is already in place; batch operations are a natural evolutionary step
- Preventing database pollution early (before users create hundreds of duplicate entries) is easier than cleanup later
- Future NLP improvements will complement (not replace) batch workflows—efficient review tools remain valuable regardless of parsing accuracy

