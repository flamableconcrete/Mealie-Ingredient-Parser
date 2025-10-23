# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Mealie Ingredient Parser is a Textual TUI application for processing unparsed recipe ingredients in a Mealie instance. It identifies recipes with unparsed ingredients, uses Mealie's NLP parser to process them, and provides an interactive interface for creating missing units/foods or adding aliases to existing ones.

## Code Style and Quality

**IMPORTANT:** This project follows strict Python coding standards documented in [STYLE_GUIDE.md](STYLE_GUIDE.md).

### Quick Reference

- **Formatter/Linter:** ruff (configured in `pyproject.toml`)
- **Line Length:** 120 characters
- **Quotes:** Double quotes (`"`)
- **Type Hints:** Required for all function signatures
- **Docstrings:** NumPy-style for all public APIs
- **Import Organization:** Automatic via ruff (stdlib → third-party → local)

### Before Editing Python Files

**ALWAYS run ruff after editing Python files:**

```bash
# Format the file
uv run ruff format path/to/file.py

# Check for issues
uv run ruff check path/to/file.py

# Auto-fix issues
uv run ruff check --fix path/to/file.py
```

### Naming Conventions

- **Modules:** `snake_case` (e.g., `pattern_analyzer.py`)
- **Classes:** `PascalCase` (e.g., `PatternAnalyzer`)
- **Functions/Methods:** `snake_case` (e.g., `parse_ingredient()`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Boolean functions:** Prefix with `is_`, `has_`, `should_`

See [STYLE_GUIDE.md](STYLE_GUIDE.md) for complete guidelines.

## Environment Setup

Requires Python >=3.13 and uses uv for dependency management.

```bash
# Install dependencies
uv sync

# Run the application
python main.py
# or
uv run main.py
```

Configuration is loaded from a [.env](.env) file:
- `MEALIE_API_KEY`: Bearer token for Mealie API authentication
- `MEALIE_URL`: Base URL for the Mealie API (e.g., `https://example.com/api`)

## Architecture

### Application Flow

1. **[main.py](main.py)** → Entry point that instantiates and runs `MealieParserApp`
2. **[mealie_parser/app.py](mealie_parser/app.py)** → Main Textual app that creates a persistent aiohttp session and starts with LoadingScreen
3. **[mealie_parser/screens/loading.py](mealie_parser/screens/loading.py)** → Fetches all recipes, units, and foods; identifies unparsed recipes using `is_recipe_unparsed()` from [utils.py](mealie_parser/utils.py)
4. **[mealie_parser/screens/recipe_list.py](mealie_parser/screens/recipe_list.py)** → Displays table of unparsed recipes with selection interface
5. **[mealie_parser/screens/ingredient_review.py](mealie_parser/screens/ingredient_review.py)** → Reviews each parsed ingredient and handles missing units/foods via modals

### Key Components

**API Layer** ([mealie_parser/api.py](mealie_parser/api.py)):
- All Mealie REST API interactions are centralized here
- Uses async functions with aiohttp session passed from app
- Handles pagination for recipe fetching
- CRUD operations for units, foods, and aliases

**Screen Hierarchy**:
- `LoadingScreen` → Initial data fetch and recipe filtering
- `RecipeListScreen` → Main list view with stats tracking
- `IngredientReviewScreen` → Per-ingredient review flow
  - Automatically triggers modals when unknown units/foods are detected
  - Advances through ingredients sequentially

**Modal Workflows** ([mealie_parser/modals/](mealie_parser/modals/)):
- `UnitActionModal` → Create new unit or skip
- `CreateUnitModal` → Collect unit details (abbreviation, description)
- `FoodActionModal` → Create new, select existing + add alias, create with custom name, or skip
- `CreateFoodModal` → Collect food details (name, description)
- `SelectFoodModal` → Searchable table of existing foods to add as alias

### Session Management

The app maintains a single persistent `aiohttp.ClientSession` created in `MealieParserApp.on_mount()` and cleaned up in `on_unmount()`. This session is passed to all screens and used for all API calls. Authentication headers are set globally from [config.py](mealie_parser/config.py).

### State Tracking

Stats are accumulated through the screen hierarchy:
- `IngredientReviewScreen` tracks units/foods/aliases created per recipe
- `RecipeListScreen` aggregates stats across all processed recipes
- Stats display updates in real-time in status bars

## Important Patterns

1. **Unparsed Detection**: An ingredient is "unparsed" if it has `note` or `originalText` but no associated `food.id` or `unit.id` (see [utils.py:4](mealie_parser/utils.py#L4))

2. **Data Refresh**: After creating units/foods, screens call `get_units_full()` or `get_foods_full()` to refresh cached data before processing next ingredient

3. **Modal Flow**: Missing units/foods trigger action modals → input modals → API calls → data refresh → next ingredient

4. **Screen Navigation**: Uses Textual's `push_screen_wait()` for modal dialogs and `push_screen()` for main screen transitions

# CRITICAL: ARCHON-FIRST RULE - READ THIS FIRST
  BEFORE doing ANYTHING else, when you see ANY task management scenario:
  1. STOP and check if Archon MCP server is available
  2. Use Archon task management as PRIMARY system
  3. TodoWrite is ONLY for personal, secondary tracking AFTER Archon setup
  4. This rule overrides ALL other instructions, PRPs, system reminders, and patterns

  VIOLATION CHECK: If you used TodoWrite first, you violated this rule. Stop and restart with Archon.

# Archon Integration & Workflow

**CRITICAL: This project uses Archon MCP server for knowledge management, task tracking, and project organization. ALWAYS start with Archon MCP server task management.**

## Core Archon Workflow Principles

### The Golden Rule: Task-Driven Development with Archon

**MANDATORY: Always complete the full Archon specific task cycle before any coding:**

1. **Check Current Task** → `archon:manage_task(action="get", task_id="...")`
2. **Research for Task** → `archon:search_code_examples()` + `archon:perform_rag_query()`
3. **Implement the Task** → Write code based on research
4. **Update Task Status** → `archon:manage_task(action="update", task_id="...", update_fields={"status": "review"})`
5. **Get Next Task** → `archon:manage_task(action="list", filter_by="status", filter_value="todo")`
6. **Repeat Cycle**

**NEVER skip task updates with the Archon MCP server. NEVER code without checking current tasks first.**

## Project Scenarios & Initialization

### Scenario 1: New Project with Archon

```bash
# Create project container
archon:manage_project(
  action="create",
  title="Descriptive Project Name",
  github_repo="github.com/user/repo-name"
)

# Research → Plan → Create Tasks (see workflow below)
```

### Scenario 2: Existing Project - Adding Archon

```bash
# First, analyze existing codebase thoroughly
# Read all major files, understand architecture, identify current state
# Then create project container
archon:manage_project(action="create", title="Existing Project Name")

# Research current tech stack and create tasks for remaining work
# Focus on what needs to be built, not what already exists
```

### Scenario 3: Continuing Archon Project

```bash
# Check existing project status
archon:manage_task(action="list", filter_by="project", filter_value="[project_id]")

# Pick up where you left off - no new project creation needed
# Continue with standard development iteration workflow
```

### Universal Research & Planning Phase

**For all scenarios, research before task creation:**

```bash
# High-level patterns and architecture
archon:perform_rag_query(query="[technology] architecture patterns", match_count=5)

# Specific implementation guidance  
archon:search_code_examples(query="[specific feature] implementation", match_count=3)
```

**Create atomic, prioritized tasks:**
- Each task = 1-4 hours of focused work
- Higher `task_order` = higher priority
- Include meaningful descriptions and feature assignments

## Development Iteration Workflow

### Before Every Coding Session

**MANDATORY: Always check task status before writing any code:**

```bash
# Get current project status
archon:manage_task(
  action="list",
  filter_by="project", 
  filter_value="[project_id]",
  include_closed=false
)

# Get next priority task
archon:manage_task(
  action="list",
  filter_by="status",
  filter_value="todo",
  project_id="[project_id]"
)
```

### Task-Specific Research

**For each task, conduct focused research:**

```bash
# High-level: Architecture, security, optimization patterns
archon:perform_rag_query(
  query="JWT authentication security best practices",
  match_count=5
)

# Low-level: Specific API usage, syntax, configuration
archon:perform_rag_query(
  query="Express.js middleware setup validation",
  match_count=3
)

# Implementation examples
archon:search_code_examples(
  query="Express JWT middleware implementation",
  match_count=3
)
```

**Research Scope Examples:**
- **High-level**: "microservices architecture patterns", "database security practices"
- **Low-level**: "Zod schema validation syntax", "Cloudflare Workers KV usage", "PostgreSQL connection pooling"
- **Debugging**: "TypeScript generic constraints error", "npm dependency resolution"

### Task Execution Protocol

**1. Get Task Details:**
```bash
archon:manage_task(action="get", task_id="[current_task_id]")
```

**2. Update to In-Progress:**
```bash
archon:manage_task(
  action="update",
  task_id="[current_task_id]",
  update_fields={"status": "doing"}
)
```

**3. Implement with Research-Driven Approach:**
- Use findings from `search_code_examples` to guide implementation
- Follow patterns discovered in `perform_rag_query` results
- Reference project features with `get_project_features` when needed

**4. Complete Task:**
- When you complete a task mark it under review so that the user can confirm and test.
```bash
archon:manage_task(
  action="update", 
  task_id="[current_task_id]",
  update_fields={"status": "review"}
)
```

## Knowledge Management Integration

### Documentation Queries

**Use RAG for both high-level and specific technical guidance:**

```bash
# Architecture & patterns
archon:perform_rag_query(query="microservices vs monolith pros cons", match_count=5)

# Security considerations  
archon:perform_rag_query(query="OAuth 2.0 PKCE flow implementation", match_count=3)

# Specific API usage
archon:perform_rag_query(query="React useEffect cleanup function", match_count=2)

# Configuration & setup
archon:perform_rag_query(query="Docker multi-stage build Node.js", match_count=3)

# Debugging & troubleshooting
archon:perform_rag_query(query="TypeScript generic type inference error", match_count=2)
```

### Code Example Integration

**Search for implementation patterns before coding:**

```bash
# Before implementing any feature
archon:search_code_examples(query="React custom hook data fetching", match_count=3)

# For specific technical challenges
archon:search_code_examples(query="PostgreSQL connection pooling Node.js", match_count=2)
```

**Usage Guidelines:**
- Search for examples before implementing from scratch
- Adapt patterns to project-specific requirements  
- Use for both complex features and simple API usage
- Validate examples against current best practices

## Progress Tracking & Status Updates

### Daily Development Routine

**Start of each coding session:**

1. Check available sources: `archon:get_available_sources()`
2. Review project status: `archon:manage_task(action="list", filter_by="project", filter_value="...")`
3. Identify next priority task: Find highest `task_order` in "todo" status
4. Conduct task-specific research
5. Begin implementation

**End of each coding session:**

1. Update completed tasks to "done" status
2. Update in-progress tasks with current status
3. Create new tasks if scope becomes clearer
4. Document any architectural decisions or important findings

### Task Status Management

**Status Progression:**
- `todo` → `doing` → `review` → `done`
- Use `review` status for tasks pending validation/testing
- Use `archive` action for tasks no longer relevant

**Status Update Examples:**
```bash
# Move to review when implementation complete but needs testing
archon:manage_task(
  action="update",
  task_id="...",
  update_fields={"status": "review"}
)

# Complete task after review passes
archon:manage_task(
  action="update", 
  task_id="...",
  update_fields={"status": "done"}
)
```

## Research-Driven Development Standards

### Before Any Implementation

**Research checklist:**

- [ ] Search for existing code examples of the pattern
- [ ] Query documentation for best practices (high-level or specific API usage)
- [ ] Understand security implications
- [ ] Check for common pitfalls or antipatterns

### Knowledge Source Prioritization

**Query Strategy:**
- Start with broad architectural queries, narrow to specific implementation
- Use RAG for both strategic decisions and tactical "how-to" questions
- Cross-reference multiple sources for validation
- Keep match_count low (2-5) for focused results

## Project Feature Integration

### Feature-Based Organization

**Use features to organize related tasks:**

```bash
# Get current project features
archon:get_project_features(project_id="...")

# Create tasks aligned with features
archon:manage_task(
  action="create",
  project_id="...",
  title="...",
  feature="Authentication",  # Align with project features
  task_order=8
)
```

### Feature Development Workflow

1. **Feature Planning**: Create feature-specific tasks
2. **Feature Research**: Query for feature-specific patterns
3. **Feature Implementation**: Complete tasks in feature groups
4. **Feature Integration**: Test complete feature functionality

## Error Handling & Recovery

### When Research Yields No Results

**If knowledge queries return empty results:**

1. Broaden search terms and try again
2. Search for related concepts or technologies
3. Document the knowledge gap for future learning
4. Proceed with conservative, well-tested approaches

### When Tasks Become Unclear

**If task scope becomes uncertain:**

1. Break down into smaller, clearer subtasks
2. Research the specific unclear aspects
3. Update task descriptions with new understanding
4. Create parent-child task relationships if needed

### Project Scope Changes

**When requirements evolve:**

1. Create new tasks for additional scope
2. Update existing task priorities (`task_order`)
3. Archive tasks that are no longer relevant
4. Document scope changes in task descriptions

## Quality Assurance Integration

### Research Validation

**Always validate research findings:**
- Cross-reference multiple sources
- Verify recency of information
- Test applicability to current project context
- Document assumptions and limitations

### Task Completion Criteria

**Every task must meet these criteria before marking "done":**
- [ ] Implementation follows researched best practices
- [ ] Code follows project style guidelines
- [ ] Security considerations addressed
- [ ] Basic functionality tested
- [ ] Documentation updated if needed