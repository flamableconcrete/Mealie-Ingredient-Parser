# Data Flow

## Application Startup Flow

```
1. main.py
   └─> MealieParserApp()
       └─> on_mount()
           ├─> Create aiohttp.ClientSession
           │   └─> headers = {"Authorization": "Bearer <MEALIE_API_KEY>"}
           └─> push_screen(LoadingScreen)

2. LoadingScreen
   └─> on_mount()
       └─> asyncio.create_task(load_data())
           ├─> get_all_recipes(session)
           ├─> get_units_full(session)
           ├─> get_foods_full(session)
           ├─> Check each recipe with is_recipe_unparsed()
           └─> push_screen(ModeSelectionScreen)

3. ModeSelectionScreen
   └─> User selects mode
       ├─> Sequential Mode → push_screen(RecipeListScreen)
       └─> Batch Mode → push_screen(PatternGroupScreen)  [NEW]

4. RecipeListScreen (Sequential Mode)
   └─> User selects recipe
       ├─> get_recipe_details(session, slug)
       ├─> parse_ingredients(session, raw_ingredients)
       └─> push_screen_wait(IngredientReviewScreen)
           ├─> For each ingredient:
           │   ├─> Check missing unit → UnitActionModal
           │   │   └─> create_unit() → update_recipe()
           │   └─> Check missing food → FoodActionModal
           │       └─> create_food() or add_food_alias()
           └─> Return to RecipeListScreen with stats
```

## Data Dependencies

```
┌───────────────────────────────────────────────────┐
│            LoadingScreen (on_mount)               │
├───────────────────────────────────────────────────┤
│                                                   │
│  1. Fetch all recipes          (API: GET /recipes)
│  2. Fetch all units            (API: GET /units)
│  3. Fetch all foods            (API: GET /foods)
│  4. For each recipe:                              │
│     └─> get_recipe_details()  (API: GET /recipes/{slug})
│         └─> is_recipe_unparsed(ingredients)      │
│                                                   │
└──────────────┬────────────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────────────┐
│         ModeSelectionScreen / RecipeListScreen    │
├───────────────────────────────────────────────────┤
│                                                   │
│  Receives from LoadingScreen:                    │
│  - unparsed_recipes: list[Recipe]                │
│  - session: aiohttp.ClientSession                │
│  - known_units_full: list[Unit]                  │
│  - known_foods_full: list[Food]                  │
│                                                   │
└──────────────┬────────────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────────────┐
│          IngredientReviewScreen (Sequential)      │
├───────────────────────────────────────────────────┤
│                                                   │
│  1. parse_ingredients()       (API: POST /parser/ingredients)
│  2. For each ingredient:                          │
│     ├─> If missing unit:                          │
│     │   └─> create_unit()     (API: POST /units)
│     └─> If missing food:                          │
│         ├─> create_food()     (API: POST /foods)
│         └─> add_food_alias()  (API: PUT /foods/{id})
│  3. update_recipe()           (API: PUT /recipes/{slug})
│  4. Refresh caches:                               │
│     ├─> get_units_full()                          │
│     └─> get_foods_full()                          │
│                                                   │
└───────────────────────────────────────────────────┘
```

---
