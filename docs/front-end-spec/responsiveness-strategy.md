# Responsiveness Strategy

## Breakpoints

| Breakpoint | Min Width (columns) | Max Width (columns) | Target Use Cases |
|------------|---------------------|---------------------|------------------|
| Minimal | 80 | 100 | Minimum viable terminal size, SSH sessions, constrained environments |
| Standard | 100 | 120 | Typical terminal window (default on most systems) |
| Wide | 120 | 160 | Large desktop terminals, ultra-wide monitors |
| Ultra-wide | 160+ | - | Multi-monitor setups, presentation mode |

## Adaptation Patterns

**Layout Changes:**
- **Minimal (80-100 cols):** Tables use abbreviated column headers, pattern text truncated with ellipsis (...), modals occupy full width minus 4-character margin
- **Standard (100-120 cols):** Default layout as shown in wireframes, all content visible without truncation for typical patterns
- **Wide (120-160 cols):** Tables add whitespace padding for readability, modals max-width at 100 columns (centered), additional metadata columns optional (e.g., "Last Updated" timestamp)
- **Ultra-wide (160+ cols):** Side-by-side layout options (e.g., pattern list + preview simultaneously), expanded dashboard with more statistics visible

**Navigation Changes:**
- Navigation shortcuts remain consistent across all breakpoints (no layout-dependent shortcuts)
- Help footer adapts: minimal = show only critical shortcuts, wide = show extended shortcuts

**Content Priority:**
- **Essential (always visible):** Pattern text, count, status, action shortcuts
- **Important (hidden < 100 cols):** Full recipe names in preview (truncate to 20 chars), detailed error messages (summarize)
- **Optional (visible > 120 cols):** Operation timestamps, detailed statistics, similarity suggestions

**Interaction Changes:**
- No interaction model changes based on terminal size (keyboard-first always)
- Scroll behavior adapts: smaller terminals may require more scrolling for same content

---
