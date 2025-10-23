# Batch Mode User Guide

## Overview

Batch mode allows you to efficiently process multiple unparsed ingredients at once by identifying common patterns across your recipes. Instead of manually reviewing each ingredient individually, you can group similar ingredients together and process them all with a single action.

## When to Use Batch Mode

**Use Batch Mode when:**
- You have many recipes with unparsed ingredients
- You want to quickly create units or foods that appear multiple times
- You want to see patterns across your recipe collection
- You prefer bulk operations over one-by-one processing

**Use Recipe Mode when:**
- You want to review ingredients in the context of specific recipes
- You prefer sequential, step-by-step processing
- You need fine-grained control over each ingredient

## Starting Batch Mode

1. Launch the application: `python main.py`
2. Wait for the loading screen to analyze your recipes
3. Select **"Start Batch Mode [2]"** from the mode selection screen

You'll see the Pattern Group screen with two tabs:
- **Unit Patterns** - Groups ingredients by missing units
- **Food Patterns** - Groups ingredients by missing foods

## Understanding the Pattern Table

Each row in the table shows:

| Column | Description |
|--------|-------------|
| **Pattern Text** | The text that appears across multiple ingredients (e.g., "cup", "flour", "1 tbsp olive oil") |
| **Ingredients** | Number of ingredient instances with this pattern |
| **Recipes** | Number of recipes containing this pattern |
| **Status** | Current processing status (see below) |

### Pattern Status Values

- **`pending`** - Not yet processed, ready for action
- **`parsing`** - Automated parsing in progress (NLP/Brute/OpenAI)
- **`completed`** - Successfully processed (unit/food created or alias added)
- **`skipped`** - Marked as skipped (you chose to skip this pattern)

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **↑/↓** | Navigate between patterns |
| **Enter** | Select and process the highlighted pattern |
| **Tab** | Switch between Unit Patterns and Food Patterns tabs |
| **s** | Skip the currently selected pattern |
| **u** | Undo skip (restore a skipped pattern to pending) |
| **q** or **Esc** | Exit batch mode |

## Processing Patterns: Step-by-Step Workflow

### Step 1: Select a Pattern

Use arrow keys or click to select a pattern row, then press **Enter** or click on the row.

### Step 2: Choose an Action

You'll see a modal with action options:

#### For Unit Patterns:
- **Create New Unit** - Creates a new unit in Mealie with this pattern text
- **Skip** - Skip this pattern for now (you can undo later)
- **Review Individual** *(coming soon)* - Process each ingredient separately

#### For Food Patterns:
- **Create New Food** - Creates a new food in Mealie with this pattern text
- **Add Alias to Existing Food** - Link this pattern to an existing food as an alias
- **Skip** - Skip this pattern for now (you can undo later)
- **Review Individual** *(coming soon)* - Process each ingredient separately

### Step 3: Provide Details (if creating new)

If you chose **Create New Unit**:
1. Enter the unit **Name** (e.g., "tablespoon")
2. Enter the **Abbreviation** (e.g., "tbsp")
3. Optionally add a **Description**
4. Press **Submit**

If you chose **Create New Food**:
1. Enter the food **Name** (e.g., "olive oil")
2. Optionally add a **Description**
3. Press **Submit**

If you chose **Add Alias to Existing Food**:
1. Search for the existing food in the searchable table
2. Select the correct food
3. The pattern text will be added as an alias to that food

### Step 4: Preview Affected Ingredients

After creating a unit/food or selecting an alias target, you'll see the **Batch Preview Screen** showing:
- The operation type (e.g., "Create Unit", "Add Food Alias")
- All ingredients that will be updated
- Which recipes contain these ingredients

Review the list and:
- Press **Execute** to apply the batch operation
- Press **Cancel** to abort without making changes

### Step 5: Execution and Results

The app will:
1. Update all matching ingredients in the affected recipes
2. Show progress in real-time
3. Display success/failure counts
4. Mark the pattern as `completed`
5. Save your progress automatically

## Progress Tracking

The status bar at the bottom shows:
```
Processed: 15/256 | Skipped: 3
```

- **Processed** - Patterns successfully completed
- **Total** - Total patterns available (unit patterns + food patterns)
- **Skipped** - Patterns you've marked to skip

Your progress is automatically saved and can be resumed if the app crashes or you exit.

## Working with Completely Unparsed Ingredients

**Important Note:** If your ingredients are completely unparsed (no structure at all), the pattern text will be the **full ingredient note**. For example:

- Pattern: `"1 tbsp extra-virgin olive oil"`
- Pattern: `"2 cups all-purpose flour"`
- Pattern: `"1/4 tsp black pepper"`

In this case, you'll see many unique patterns. Consider:

1. **Parsing first** - Use Mealie's NLP parser on your recipes to extract structure
2. **Processing common patterns** - Focus on patterns that appear in multiple recipes
3. **Skipping unique items** - Skip one-off ingredients and handle them in Recipe Mode

## Tips for Efficient Batch Processing

### 1. Start with High-Frequency Patterns
Sort mentally by the "Ingredients" and "Recipes" columns. Process patterns that appear many times first for maximum impact.

### 2. Use the Skip Feature Liberally
If you're unsure about a pattern or it needs special handling, skip it (`s` key) and come back later.

### 3. Group Similar Work Together
Process all unit patterns first, then switch to food patterns (or vice versa) to maintain focus.

### 4. Review Before Executing
Always review the Batch Preview Screen carefully. Once executed, the operation updates multiple ingredients across multiple recipes.

### 5. Take Advantage of Aliases
For foods, using "Add Alias" is faster than creating duplicate foods. For example:
- Food: "Olive Oil"
- Aliases: "extra-virgin olive oil", "EVOO", "olive oil extra virgin"

### 6. Watch for Pattern Quality
If patterns show full ingredient text (e.g., "1 cup flour, sifted"), consider:
- Using Recipe Mode for these specific items
- Parsing recipes first to extract better structure
- Skipping and handling manually

## Session Recovery

If the app crashes or you exit:
1. Restart the app: `python main.py`
2. You'll see a **Session Resume Modal** asking if you want to resume
3. Select **Yes** to continue from where you left off
4. Select **No** to start fresh

The session saves:
- Which patterns you've completed
- Which patterns you've skipped
- Overall progress statistics

## Troubleshooting

### "Processed: 0/0" shows at the bottom
This means no patterns were found. Possible causes:
- All your ingredients are already fully parsed
- The pattern analyzer couldn't extract patterns from your data
- Check if your recipes actually have unparsed ingredients

### Modal doesn't appear when clicking a pattern
- Make sure you're clicking on a `pending` status row
- Try pressing **Enter** instead of clicking
- Check the logs for errors

### Too many unique patterns
If you see hundreds of unique patterns with only 1-2 ingredients each:
- Your ingredients are likely completely unparsed
- Consider using Mealie's parser first to add structure
- Or switch to Recipe Mode for more granular control

### Pattern is stuck in "parsing" status
- Restart the app - the pattern will return to "pending"
- This can happen if the app crashed during parsing

## Next Steps After Batch Mode

After completing batch mode:
1. **Switch to Recipe Mode** to handle remaining unparsed ingredients individually
2. **Re-run the parser** on affected recipes to verify the changes
3. **Check your Mealie instance** to see the newly created units/foods and aliases

## Example Workflow

Here's a typical batch mode session:

```
1. Start app → Select Batch Mode
2. Tab: Unit Patterns (128 patterns)
   - Select "cup" (appears in 45 ingredients) → Create New Unit
   - Select "tbsp" (appears in 32 ingredients) → Create New Unit
   - Select "tsp" (appears in 28 ingredients) → Create New Unit
   - Skip unique patterns with 1-2 ingredients

3. Tab: Food Patterns (128 patterns)
   - Select "olive oil" (appears in 15 ingredients) → Create New Food
   - Select "EVOO" (appears in 8 ingredients) → Add Alias → Select "olive oil"
   - Select "garlic" (appears in 23 ingredients) → Create New Food
   - Skip complex patterns like "1 cup flour, sifted"

4. Status: Processed: 6/256 | Skipped: 122
5. Exit batch mode → Switch to Recipe Mode for remaining items
```

## Summary

Batch mode is powerful for:
- ✅ Processing common patterns quickly
- ✅ Creating units/foods that appear across many recipes
- ✅ Building alias relationships efficiently
- ✅ Reducing repetitive work

But remember:
- ⚠️ Always review the Batch Preview before executing
- ⚠️ Skip patterns you're unsure about
- ⚠️ Use Recipe Mode for complex or unique cases
- ⚠️ Your progress is saved automatically

Happy batch processing! 🎉
