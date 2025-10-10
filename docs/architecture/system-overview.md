# System Overview

## High-Level Architecture

The Mealie Ingredient Parser is a **terminal-based user interface (TUI)** application built with the Textual framework. It acts as an **API client** to an existing Mealie instance, providing an enhanced workflow for processing unparsed recipe ingredients.

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│            Mealie Ingredient Parser TUI             │
│                  (Textual App)                      │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │   Screens    │  │   Modals     │  │  Widgets │ │
│  │              │  │              │  │          │ │
│  │ - Loading    │  │ - UnitAction │  │ - Tables │ │
│  │ - ModeSelect │  │ - CreateUnit │  │ - Buttons│ │
│  │ - RecipeList │  │ - FoodAction │  │ - Labels │ │
│  │ - IngReview  │  │ - CreateFood │  │          │ │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘ │
│         │                 │                 │       │
│         └────────┬────────┴─────────────────┘       │
│                  │                                   │
│         ┌────────▼─────────┐                        │
│         │   API Layer      │                        │
│         │  (api.py)        │                        │
│         │                  │                        │
│         │ - get_recipes    │                        │
│         │ - get_units      │                        │
│         │ - create_unit    │                        │
│         │ - update_recipe  │                        │
│         └────────┬─────────┘                        │
│                  │                                   │
│         ┌────────▼─────────┐                        │
│         │ aiohttp Session  │                        │
│         │ (persistent)     │                        │
│         └────────┬─────────┘                        │
└──────────────────┼─────────────────────────────────┘
                   │
          ┌────────▼─────────┐
          │                  │
          │  Mealie REST API │
          │  (External)      │
          │                  │
          │ /recipes         │
          │ /units           │
          │ /foods           │
          │ /parser          │
          └──────────────────┘
```

## System Characteristics

| Characteristic | Description |
|---------------|-------------|
| **Architecture Type** | Monolithic client application |
| **Deployment Model** | Single-user, local terminal process |
| **Framework** | Textual >=6.2.1 (Python TUI framework) |
| **Language** | Python >=3.13 |
| **State** | Stateless (all data via Mealie API) |
| **Async Model** | asyncio + aiohttp for non-blocking I/O |
| **Session Management** | Single persistent HTTP session |
| **Configuration** | Environment variables (.env file) |

## Framework Constraints

- Terminal-based rendering (80x24 minimum, 120x40+ optimal)
- Character-cell grid layout system
- CSS-like styling via Textual CSS
- Event-driven architecture with async support
- Widget-based component system

---
