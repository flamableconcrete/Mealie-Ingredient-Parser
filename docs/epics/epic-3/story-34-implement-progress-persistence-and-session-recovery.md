# Story 3.4: Implement Progress Persistence and Session Recovery

**As a** user,
**I want** my progress saved so I can close the app and resume later,
**so that** I don't have to complete large parsing sessions in one sitting.

## Acceptance Criteria

1. System saves progress state to JSON file (`.mealie_parser_state.json`) after each completed batch operation
2. State includes: processed pattern groups, skipped patterns, completed recipe IDs, timestamp
3. On app startup (LoadingScreen), system checks for existing state file and offers: "Resume previous session" or "Start fresh"
4. "Resume previous session" loads state, marks patterns as completed/skipped in PatternGroupScreen, excludes completed recipes from RecipeListScreen
5. "Start fresh" deletes state file and begins new session
6. State file stored in user's home directory or alongside .env file (configurable)
7. System gracefully handles missing, corrupted, or incompatible state files by offering 'Start Fresh' option
8. Manual testing validates state save/load across app restarts
