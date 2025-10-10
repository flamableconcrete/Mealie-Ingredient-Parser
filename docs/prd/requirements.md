# Requirements

## Functional Requirements

**FR1:** The system shall identify and group unparsed ingredients by pattern (e.g., all instances of "tsp", "chicken breast") across multiple recipes

**FR2:** The system shall allow users to create a unit once and automatically apply it to all matching ingredient instances

**FR3:** The system shall allow users to create a food once and automatically apply it to all matching ingredient instances

**FR4:** The system shall allow users to add an alias to an existing food and automatically apply it to all matching ingredient instances

**FR5:** The system shall provide a batch review interface showing all ingredients affected by a proposed action before execution

**FR6:** The system shall support pattern-based matching to suggest related ingredients (e.g., "chicken breast", "chicken breasts", "boneless chicken breast") for batch operations

**FR7:** The system shall maintain compatibility with existing Mealie API endpoints for units, foods, and aliases without requiring Mealie core modifications

**FR8:** The system shall allow users to skip/defer ingredients or groups of ingredients for later review

**FR9:** The system shall preserve the existing sequential ingredient review mode for users who prefer one-at-a-time processing

**FR10:** The system shall display progress tracking showing total ingredients processed, remaining, and batch operations applied

**FR11:** The system shall validate all batch operations against Mealie API constraints before execution (e.g., duplicate unit abbreviations, invalid food names)

## Non-Functional Requirements

**NFR1:** Batch operations on 500 ingredients shall complete within 15 minutes of active user decision-making time (excluding API response time)

**NFR2:** The system shall display pattern groupings within 2 seconds of loading recipe data

**NFR3:** The system shall maintain responsive TUI performance (< 100ms input lag) when processing datasets of 1000+ ingredients

**NFR4:** The system shall handle API errors gracefully with retry logic and clear error messages to prevent partial batch operations

**NFR5:** The system shall use the existing aiohttp session architecture for all API calls to maintain consistent authentication and connection pooling

**NFR6:** The system shall operate within terminal environments with minimum 80x24 character display dimensions

**NFR7:** The system shall maintain the existing Textual-based TUI architecture and UI consistency with current screen implementations

**NFR8:** The system shall log all batch operations with sufficient detail for troubleshooting and audit purposes

**NFR9:** The system shall not log API keys or sensitive credentials; all credential storage shall use existing .env file pattern with appropriate file permissions

---
