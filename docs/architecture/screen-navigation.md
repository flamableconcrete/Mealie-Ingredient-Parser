# Screen Navigation

## Current Screen Flow (Sequential Mode)

```
┌──────────────┐
│ LoadingScreen│
│              │
│ - Fetch data │
│ - Find       │
│   unparsed   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ ModeSelection    │
│ Screen           │
│                  │
│ [Sequential Mode]│
│ [Batch Mode]     │ ◄─── NEW batch mode entry
└──────┬───────────┘
       │
       │ (Sequential Mode)
       ▼
┌──────────────────┐
│ RecipeListScreen │
│                  │
│ - Table of       │
│   unparsed       │
│   recipes        │
│ - Stats bar      │
└──────┬───────────┘
       │
       │ (User selects recipe)
       ▼
┌──────────────────────┐
│ IngredientReview     │
│ Screen               │
│                      │
│ - Review each        │
│   ingredient         │
│ - Trigger modals     │
│   for missing        │
│   units/foods        │
└──────┬───────────────┘
       │
       │ (Recipe complete)
       ▼
┌──────────────────┐
│ RecipeListScreen │
│ (return with     │
│  updated stats)  │
└──────────────────┘
```

## Screen Lifecycle

Each screen follows Textual's lifecycle:

1. **`__init__()`** - Initialize with data dependencies
2. **`compose()`** - Define widget structure (declarative)
3. **`on_mount()`** - Setup after widgets created (imperative)
4. **Event handlers** - React to user input (`action_*`, `on_*`)
5. **`on_unmount()`** - Cleanup (if needed)

---
