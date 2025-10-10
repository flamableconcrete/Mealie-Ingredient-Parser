# Story 3.3: Add Comprehensive Operation Logging

**As a** developer or advanced user,
**I want** detailed logs of all batch operations,
**so that** I can troubleshoot issues and audit what changes were made.

## Acceptance Criteria

1. System logs to file (e.g., `mealie_parser.log`) with timestamps, log levels, and structured messages
2. Log entry for batch operation start: pattern text, operation type, affected ingredient count
3. Log entry for each API call: ingredient ID, recipe ID, API endpoint, request payload, response status
4. Log entry for batch operation completion: success count, failure count, total duration
5. Log entries for validation failures: what was validated, why it failed
6. Log file location displayed in app footer or accessible via help screen
7. Logs include sufficient detail for reproducing issues without exposing sensitive data (API keys redacted)
