# Story 3.2: Implement Graceful Error Recovery for Partial Batch Failures

**As a** user,
**I want** batch operations to continue processing remaining ingredients even if some fail,
**so that** transient API errors don't force me to restart the entire batch.

## Acceptance Criteria

1. Batch update functions (from Epic 1 Story 1.4) implement retry logic: 3 attempts with exponential backoff for failed API calls
2. After exhausting retries, operation collects failure details (ingredient ID, error message) and continues with next ingredient
3. Upon batch completion, system displays summary modal: "X of Y ingredients updated successfully. Z failed."
4. Summary modal lists failed ingredients with recipe names and error messages
5. Failed ingredients remain in "Pending" state; pattern not marked "Completed" if any failures occurred
6. User can retry failed subset via "Retry Failed" option on summary modal
