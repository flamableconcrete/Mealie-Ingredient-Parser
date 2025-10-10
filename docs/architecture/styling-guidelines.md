# Styling Guidelines

## Styling Approach

**Textual CSS System:** The application uses Textual's CSS-like styling language (TCSS) with automatic terminal capability detection.

**Core Philosophy:**
- Separation of concerns: Visual styling in `.tcss` files, component logic in Python
- Component-scoped styles: Each screen/widget has dedicated CSS rules
- Theme-driven design: CSS variables define color palette, spacing scale
- Terminal-aware: Styles gracefully degrade across terminal capabilities

**File Organization:**
```
mealie_parser/styles/
├── app.tcss          # Global theme variables and base styles
├── screens.tcss      # Screen-specific styles
├── modals.tcss       # Modal dialog styles
└── widgets.tcss      # Custom widget styles
```

## Global Theme Variables

```css
/* mealie_parser/styles/app.tcss - Global theme and base styles */

/* ===== COLOR PALETTE ===== */
$primary: #00d9d9;           /* Cyan - focused elements */
$secondary: #5c9ccc;         /* Blue - headers, dividers */
$accent: #d957d9;            /* Magenta - important counts */
$success: #5fa85f;           /* Green - completed patterns */
$warning: #ffd700;           /* Yellow - partial success */
$error: #d95757;             /* Red - failures */
$neutral-dark: #808080;      /* Gray - skipped/dimmed */
$neutral-light: #ffffff;     /* White - primary text */
$background: #000000;        /* Black - default background */

/* ===== SPACING SCALE ===== */
$spacing-xs: 1;
$spacing-sm: 2;
$spacing-md: 3;
$spacing-lg: 5;
$spacing-xl: 8;

/* ===== TRANSITIONS ===== */
$transition-fast: 150ms;
$transition-medium: 300ms;
$transition-slow: 500ms;

/* ===== BASE STYLES ===== */
Screen {
    background: $background;
    color: $neutral-light;
}

Header {
    background: $secondary;
    color: $neutral-light;
    text-style: bold;
    dock: top;
    height: 1;
}

Footer {
    background: $neutral-dark;
    color: $neutral-light;
    dock: bottom;
    height: 1;
}

DataTable {
    background: $background;
    color: $neutral-light;
    border: solid $neutral-dark;
}

DataTable > .datatable--cursor {
    background: $primary-darken-2;
}

DataTable:focus > .datatable--cursor {
    background: $primary;
    color: $background;
    text-style: bold;
}

Button {
    background: $primary-darken-1;
    color: $neutral-light;
    min-width: 12;
    height: 3;
}

Button:hover {
    background: $primary;
    text-style: bold;
}

Input {
    background: $neutral-dark;
    color: $neutral-light;
    border: solid $primary-darken-2;
}

Input:focus {
    border: solid $primary;
}

/* ===== UTILITY CLASSES ===== */
.text-success { color: $success; }
.text-error { color: $error; }
.text-warning { color: $warning; }
.text-dim { color: $neutral-dark; }
.text-bold { text-style: bold; }
.text-center { text-align: center; }

.mt-1 { margin-top: 1; }
.mt-2 { margin-top: 2; }
.mb-1 { margin-bottom: 1; }
.mb-2 { margin-bottom: 2; }
.p-1 { padding: 1; }
.p-2 { padding: 2; }
```

## Styling Rationale

**Key Decisions:**
- **CSS Variables:** All colors as variables for easy theming
- **Semantic naming:** `$success`, `$error` instead of `$green`, `$red`
- **Character-based spacing:** Scale based on character cell counts
- **Focus state emphasis:** Bold + high contrast for keyboard navigation
- **Utility classes:** Common patterns like `.text-success`, `.mt-1`

**Accessibility:**
- Minimum 4.5:1 contrast for normal text
- Bold text for focused elements
- Semantic colors paired with symbols (✓ not just green)

---
