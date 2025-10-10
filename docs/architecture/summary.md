# Summary

This comprehensive architecture document defines the complete system and frontend architecture for the Mealie Ingredient Parser TUI application. Key architectural principles:

1. **System Overview:** Textual TUI app acting as Mealie API client
2. **Architecture Patterns:** Screen stack, persistent session, reactive state, API abstraction
3. **Tech Stack:** Python 3.13, Textual 6.2.1, aiohttp, minimal dependencies
4. **Project Structure:** Feature-based organization with clear separation of concerns
5. **Component Architecture:** App class, screens, modals, widgets, services, API layer
6. **Component Standards:** Modern Python type hints, PascalCase classes, snake_case methods
7. **Data Flow:** Startup → LoadingScreen → ModeSelection → RecipeList/PatternGroup
8. **Screen Navigation:** Push/pop stack model with modal overlays
9. **API Layer:** Centralized functions with consistent error handling
10. **State Management:** Three-tier model (app/screen/persistent) with reactive updates
11. **Routing:** Screen stack navigation with callback-based modal flow
12. **Styling Guidelines:** Textual CSS with theme variables and utility classes
13. **Testing Requirements:** Unit tests for business logic, integration tests for API layer
14. **Modal Workflows:** Reusable dialogs for unit/food creation
15. **Error Handling:** Multi-layer strategy with logging and user notifications
16. **Batch Integration Points:** New screens, modal reuse, API extension, state sharing
17. **Environment Configuration:** .env-based config with security best practices
18. **Deployment Architecture:** Local installation, simple upgrade, feature flag rollback
19. **Developer Standards:** Type safety, async-first, keyboard navigation, logging

## Key Integration Principles for Batch Mode

1. ✅ **Preserve Sequential Mode:** RecipeListScreen and IngredientReviewScreen unchanged
2. ✅ **Reuse Existing Modals:** CreateUnitModal, CreateFoodModal, SelectFoodModal
3. ✅ **Extend API Layer:** Add batch functions without modifying existing functions
4. ✅ **Share Session:** Use app.session consistently across all screens
5. ✅ **Follow Screen Pattern:** New screens (PatternGroupScreen, BatchPreviewScreen) follow existing lifecycle
6. ✅ **Feature Flag:** BATCH_MODE_ENABLED allows rollback without code changes

This architecture supports the PRD's batch processing enhancements while maintaining system integrity and allowing safe rollback if issues arise.
