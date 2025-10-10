# Branding & Style Guide

## Visual Identity

**Brand Guidelines:** Inherits from Mealie project branding (https://mealie.io) - community-driven, practical, approachable. TUI application maintains professional terminal aesthetic while providing clear visual feedback for batch operations.

## Color Palette

| Color Type | Hex Code / Terminal Color | Usage |
|------------|---------------------------|-------|
| Primary | Cyan (#00D9D9) / `bright_cyan` | Focused elements, selected rows, interactive highlights |
| Secondary | Blue (#5C9CCC) / `blue` | Headers, section dividers, informational text |
| Accent | Magenta (#D957D9) / `magenta` | Important counts, high-priority warnings |
| Success | Green (#5FA85F) / `green` | Completed patterns, successful operations, checkmarks |
| Warning | Yellow (#FFD700) / `yellow` | Partial success, caution messages, skip indicators |
| Error | Red (#D95757) / `red` | Failed operations, validation errors, critical alerts |
| Neutral Dark | Gray (#808080) / `bright_black` | Skipped/completed items (dimmed), secondary text |
| Neutral Light | White (#FFFFFF) / `white` | Primary text, table content, default foreground |
| Background | Black (#000000) / `black` | Default background (terminal default) |

**Color Usage Notes:**
- Terminal color support varies (8-color, 16-color, 256-color, true color) - use named Textual colors for compatibility
- Success/Warning/Error follow standard semantic conventions for accessibility
- Avoid relying solely on color - always pair with symbols/text (e.g., "✓ Completed" not just green text)

## Typography

### Font Families

- **Primary:** Monospace (terminal default) - e.g., Menlo, Consolas, DejaVu Sans Mono
- **Fallback:** System monospace font
- **Note:** Font family controlled by user's terminal emulator settings, not by application

### Type Scale

| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| H1 | N/A (1 line) | Bold | 1 | Screen titles (e.g., "PROGRESS DASHBOARD") |
| H2 | N/A (1 line) | Bold | 1 | Section headers (e.g., "UNIT PATTERNS") |
| H3 | N/A (1 line) | Normal | 1 | Subsection labels (e.g., "Recent Operations") |
| Body | N/A (1 char) | Normal | 1 | Table content, descriptions, messages |
| Small | N/A (1 char) | Normal | 1 | Footer text, hints, metadata |

**Typography Notes:**
- Terminal UIs use character cells, not pixels - "size" is controlled by terminal settings
- Emphasis achieved through: UPPERCASE, **bold**, color, borders, not font size changes
- Line height fixed at 1 character cell per line

## Iconography

**Icon Library:** Unicode symbols and box-drawing characters

**Symbol Set:**
- Status: ● (pending), ✓ (completed), ⊘ (skipped), ⚠ (warning), ✗ (error)
- Navigation: ▶ (focused item), ▼ (scroll indicator), ← ↑ → ↓ (arrows)
- Tree structure: ├─ └─ │ (nested relationships)
- Borders: ┌─┐│└┘ ═ ║ (table/modal frames)
- Progress: █ (filled), ░ (empty)

**Usage Guidelines:**
- Test all symbols in target terminal emulators (some older terminals lack Unicode support)
- Provide text fallbacks for critical symbols (e.g., "[PENDING]" if ● not supported)
- Maintain consistent symbol usage across all screens

## Spacing & Layout

**Grid System:** Character-based grid (80 columns minimum, 120 columns optimal)

**Column allocation:**
- Pattern tables: 20ch (pattern) + 6ch (type) + 7ch (count) + 30ch (status) + margins
- Preview tables: 25ch (recipe) + 35ch (ingredient) + 12ch (status) + margins
- Modals: 60-75 column width for readability, centered horizontally

**Spacing Scale:**
- Minimal: 1 character (inline spacing, table cell padding)
- Standard: 2-3 characters (between sections, modal padding)
- Large: 5+ characters (top/bottom margins for modals, section separators)

**Layout Guidelines:**
- Maintain 2-character margin from screen edges when possible
- Use horizontal rules (─────) to separate major sections
- Tables should occupy maximum width for data visibility
- Modals should be visually centered with balanced padding

---
