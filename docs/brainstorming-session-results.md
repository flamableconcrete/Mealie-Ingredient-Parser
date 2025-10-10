# Brainstorming Session Results

**Session Date:** 2025-10-07
**Facilitator:** Business Analyst Mary
**Participant:** User

## Executive Summary

**Topic:** Improving the intuitive usability of the Mealie Ingredient Parser TUI - specifically the workflow for adding units/ingredients parsed from Mealie's NLP parser into the database

**Session Goals:** Focused ideation on specific workflow improvements for adding parsed units and ingredients to the Mealie database

**Techniques Used:** Question Storming (15 min), What If Scenarios (15 min), First Principles Thinking (10 min)

**Total Ideas Generated:** 12+ questions and 4 major solution themes

### Key Themes Identified:
- Batch processing capability for efficiency across multiple recipes
- Dual mode system to accommodate different user preferences and use cases
- Safety mechanisms for bulk operations
- Better handling of edge cases and outliers

## Technique Sessions

### Question Storming - 15 minutes

**Description:** Generate questions instead of answers first to explore the problem space and uncover core challenges

**Ideas Generated:**
1. Why can't I add multiple missing units or ingredients at once?
2. When the parser finds something weird, how can I get it to match something I've already created?
3. Can the workflow be improved to be more intuitive for users?
4. When I see a weird unit like "cups cups", I don't know what the workflow should be - how can we deal with outliers?
5. Would it be possible to have one mode to go in batches and another mode to do one at a time depending on my mood?
6. Can we bulk insert the missing units or ingredients, but only after a screen that asks "are you sure?"?
7. Can we keep a log of recent actions that actually change the database in case we want to undo an operation?

**Insights Discovered:**
- Current workflow is strictly sequential (one ingredient at a time)
- User experiences friction with repetitive tasks across multiple recipes
- Safety and reversibility are concerns when making bulk changes
- Edge cases (like "cups cups") create decision paralysis
- Different use cases require different interaction patterns

**Notable Connections:**
- Batch operations naturally pair with safety confirmations
- User mood/context affects preferred workflow style
- Pattern recognition (already handled by Mealie) vs bulk efficiency (missing feature)

### What If Scenarios - 15 minutes

**Description:** Provocative hypothetical questions to spark creative solution possibilities

**Ideas Generated:**
1. Dashboard view showing ALL unparsed ingredients across recipes with ability to handle in any order
2. Grouping similar missing items together (rejected as too complex for initial needs)
3. Dual mode system: "Quick Batch Mode" vs "Careful Review Mode"
4. Consolidated view of missing units/foods across multiple recipes

**Insights Discovered:**
- User strongly resonated with dashboard/consolidated view concept
- Simplicity preferred over complex intelligent grouping
- Flexibility between modes is more valuable than one "perfect" workflow
- Mealie already handles some pattern learning, no need to duplicate

**Notable Connections:**
- Batch mode naturally leads to dashboard requirement
- Different modes serve different user intents (speed vs precision)
- Multi-recipe visibility enables pattern recognition by user

### First Principles Thinking - 10 minutes

**Description:** Breaking down concepts to fundamental truths to build solutions from the ground up

**Ideas Generated:**
1. Batch Mode fundamental: Work across entire instance, focus on efficiency, unit of work is the missing item itself
2. Review Mode fundamental: Work on single recipe, focus on context/precision, unit of work is the recipe
3. Minimal batch creation: Only name required (Mealie API requirement)
4. Multi-select capability for bulk operations

**Insights Discovered:**
- The two modes have fundamentally different scopes and intents
- Batch mode should be truly minimal - just names, no extra details
- Current review mode already exists and works well for its use case
- API constraint (name-only creation) actually simplifies batch UX

**Notable Connections:**
- Less information required = faster batch operations
- Scope difference (instance-wide vs single recipe) drives different UI needs
- User can always add details later in individual edit mode

## Idea Categorization

### Immediate Opportunities
*Ideas ready to implement now*

1. **Batch Mode for Units (MVP)**
   - Description: Add batch mode that lists all unique missing units across recipes, allows multi-select, creates with names only, includes confirmation dialog
   - Why immediate: Clear requirements, simple API needs (name only), proves concept before expanding to foods
   - Resources needed: New screen/view in Textual TUI, API integration for bulk unit creation, confirmation modal

2. **Mode Selection Interface**
   - Description: Add ability to choose between Batch Mode and Review/Recipe Mode at workflow entry point
   - Why immediate: Simple UI addition, enables the dual-mode system, low complexity
   - Resources needed: Mode selection screen or toggle, routing logic to appropriate workflow

3. **Unique Missing Units Dashboard**
   - Description: Consolidated view showing all unique missing units across selected or all recipes
   - Why immediate: Core requirement for batch mode, straightforward data aggregation from existing API calls
   - Resources needed: Data aggregation logic, table/list view in Textual, multi-select widget

### Future Innovations
*Ideas requiring development/research*

1. **Batch Mode for Foods**
   - Description: Extend batch mode pattern to foods after proving concept with units
   - Development needed: Similar dashboard for foods, handle food-specific fields, alias considerations
   - Timeline estimate: After units batch mode is validated (2-4 weeks post-MVP)

2. **Outlier Detection and Handling**
   - Description: Special workflow for ambiguous cases like "cups cups", "smidgen", malformed input
   - Development needed: Define outlier criteria, design special handling UI, user guidance
   - Timeline estimate: Medium-term (1-2 months), requires usage data from batch mode

3. **Action Logging and Undo**
   - Description: Track database-changing operations with ability to undo/rollback
   - Development needed: Logging infrastructure, undo mechanism (possibly via Mealie API if supported), history UI
   - Timeline estimate: Longer-term (2-3 months), requires investigation of Mealie API undo capabilities

### Moonshots
*Ambitious, transformative concepts*

1. **Intelligent Workflow Recommendation**
   - Description: System suggests batch vs review mode based on context (e.g., "You have 50 recipes with 15 unique missing units - try Batch Mode?")
   - Transformative potential: Guides users to most efficient workflow without requiring prior knowledge
   - Challenges to overcome: Define heuristics for recommendations, avoid annoying users, make it feel helpful not pushy

### Insights & Learnings
*Key realizations from the session*

- **Simplicity wins**: User rejected complex grouping/intelligence in favor of straightforward list-and-select approach. Simpler solutions often have higher adoption.
- **Dual modes serve different intents**: Batch mode is about efficiency across the instance; Review mode is about precision within a recipe. Both are valid, neither replaces the other.
- **API constraints can simplify UX**: The fact that Mealie only requires a name for creation actually makes batch mode cleaner - no complex forms needed.
- **Prove before expanding**: Starting with units-only batch mode provides validation before investing in foods batch mode.
- **User already knows the domain**: Pattern learning already exists in Mealie, so focus should be on workflow efficiency, not duplicating existing smarts.

## Action Planning

### Top 3 Priority Ideas

#### #1 Priority: Batch Mode for Units (MVP)

- **Rationale:** Proves the dual-mode concept, addresses immediate efficiency pain point, has clear/simple requirements, uses existing API capabilities
- **Next steps:**
  1. Design batch mode screen layout in Textual (table with multi-select)
  2. Implement unique units aggregation across recipes
  3. Build bulk creation API call with names only
  4. Add confirmation dialog before database write
  5. Update recipe list to offer mode selection
- **Resources needed:**
  - Textual DataTable or ListView widget with multi-select
  - Aggregation logic from existing recipe/ingredient data
  - Bulk API integration (possibly multiple sequential creates)
  - Modal confirmation dialog
- **Timeline:** 1-2 weeks for MVP implementation

#### #2 Priority: Mode Selection Interface

- **Rationale:** Enables users to choose their preferred workflow, simple to implement, foundational for the dual-mode system
- **Next steps:**
  1. Decide on mode selection point (at recipe list, or dedicated screen after loading)
  2. Design mode selection UI (buttons, menu, or toggle)
  3. Wire up routing to batch mode vs existing review mode
  4. Add visual indicators for which mode user is in
- **Resources needed:**
  - New screen or widget for mode selection
  - Routing/navigation logic
  - Visual mode indicators
- **Timeline:** 3-5 days, can be done in parallel with batch mode development

#### #3 Priority: Dashboard View for Missing Units

- **Rationale:** Core component of batch mode, provides visibility across entire instance, reusable foundation for future foods dashboard
- **Next steps:**
  1. Extract unique missing units from all recipes
  2. Design dashboard layout (table with columns: unit name, count of recipes affected)
  3. Implement multi-select interaction
  4. Add filter/search if list becomes long
- **Resources needed:**
  - Data aggregation and deduplication logic
  - Textual table/list component
  - Multi-select state management
  - Optional: search/filter widgets
- **Timeline:** 1 week, overlaps with batch mode MVP

## Reflection & Follow-up

### What Worked Well
- Question Storming revealed core pain points quickly and effectively
- What If scenarios generated concrete solution concepts
- First Principles breakdown clarified the fundamental differences between modes
- User had clear opinions and preferences, making prioritization straightforward
- Progressive technique flow moved naturally from broad exploration to specific action items

### Areas for Further Exploration
- **Outlier handling workflow**: How to design the UX when user encounters "cups cups" or other ambiguous inputs - needs dedicated design thinking
- **Foods batch mode specifics**: How aliases, descriptions, and other food-specific fields factor into batch creation
- **Undo/rollback mechanics**: Investigation into Mealie API capabilities for reversing operations, or local tracking mechanisms
- **Cross-mode transitions**: Can user start in review mode, realize they want batch mode, and switch mid-workflow?
- **Batch mode for aliases**: Should adding aliases to existing units/foods also have a batch mode?

### Recommended Follow-up Techniques
- **SCAMPER Method**: Once batch mode MVP is built, use SCAMPER to iterate and enhance (Substitute, Combine, Adapt, Modify, Put to other use, Eliminate, Reverse)
- **Role Playing**: Test the dual-mode concept from different user perspectives (hurried user, meticulous user, first-time user, power user)
- **Assumption Reversal**: Challenge assumption that units and foods need separate batch modes - what if they could be handled together?

### Questions That Emerged
- Should batch mode show count of how many recipes each missing unit appears in?
- What happens to recipes after batch unit creation - do they auto-update, or require refresh?
- Can user preview which recipes will be affected before confirming batch creation?
- Should there be a "mixed mode" where user can batch-create some items and review others in one session?
- How do we handle concurrent edits if Mealie database is being modified by other users/processes?

### Next Session Planning
- **Suggested topics:**
  1. Outlier handling workflow design
  2. Foods batch mode detailed requirements
  3. Safety and reversibility mechanisms (logging, undo)
- **Recommended timeframe:** After batch mode MVP is implemented and user-tested (4-6 weeks)
- **Preparation needed:**
  - Gather user feedback from batch mode MVP
  - Document edge cases encountered during testing
  - Research Mealie API capabilities for undo/rollback
  - List specific outlier examples to design solutions around

---

*Session facilitated using the BMAD-METHOD™ brainstorming framework*
