# Animation & Micro-interactions

## Motion Principles

**Terminal Constraint-Aware Design:** Terminal applications have limited animation capabilities compared to GUI applications. Motion design focuses on state transitions, progress feedback, and visual confirmation rather than decorative animations.

**Core Principles:**
- **Immediate Feedback:** Every keypress should produce instant visual response (< 50ms)
- **Purposeful Motion:** Animations indicate system state (loading, processing, success) rather than decoration
- **Performance-First:** Never sacrifice input responsiveness for animation smoothness
- **Accessibility:** Respect terminal refresh rates (typically 60Hz); avoid rapid flashing (seizure risk)

## Key Animations

- **Row Focus Transition:** When navigating table rows, focus indicator (▶) moves smoothly rather than jumping (Duration: 100ms, Easing: linear)
- **Pattern Status Change:** When pattern marked completed/skipped, row color/strikethrough fades in (Duration: 200ms, Easing: ease-out)
- **Modal Appear/Dismiss:** Modals fade in from center (Duration: 150ms, Easing: ease-in-out) rather than instant appearance
- **Progress Bar Fill:** During batch operations, progress bar fills smoothly (Duration: 300ms per update, Easing: linear) synchronized with API call completion
- **Success/Error Flash:** Brief highlight flash on success (Duration: 400ms, Easing: pulse) or error (Duration: 600ms, slower pulse for urgency)
- **Batch Operation Spinner:** Animated spinner (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ rotation) during API calls (Duration: 80ms per frame, continuous loop)

**Implementation Note:** Textual framework supports these animations via CSS transitions and programmatic screen updates. Test animation performance on older hardware/terminals.

---
