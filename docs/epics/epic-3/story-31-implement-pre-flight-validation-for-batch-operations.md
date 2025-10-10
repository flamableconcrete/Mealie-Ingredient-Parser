# Story 3.1: Implement Pre-Flight Validation for Batch Operations

**As a** user,
**I want** the system to validate my batch operation before execution,
**so that** I don't encounter API errors mid-batch that leave my database in an inconsistent state.

## Acceptance Criteria

1. Before executing batch unit creation, validate: unit abbreviation not empty, abbreviation doesn't conflict with existing units, description meets Mealie requirements
2. Before executing batch food creation, validate: food name not empty, name doesn't conflict with existing foods
3. Before executing batch alias addition, validate: target food exists, alias text not empty, alias doesn't already exist for that food
4. Validation failures display clear error modal explaining issue and preventing batch execution
5. Validation uses existing cached units/foods data from LoadingScreen to avoid additional API calls
6. Unit tests validate all validation rules and error message clarity
