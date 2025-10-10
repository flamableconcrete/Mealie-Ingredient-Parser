# Accessibility Requirements

## Compliance Target

**Standard:** WCAG 2.1 Level AA principles adapted for terminal-based interfaces. Focus on keyboard navigation, screen reader compatibility, and visual contrast rather than traditional web accessibility guidelines.

## Key Requirements

**Visual:**
- **Color contrast ratios:** Minimum 4.5:1 for normal text, 3:1 for large text. Use Textual's built-in color schemes which meet these ratios for standard terminals.
- **Focus indicators:** Visible focus state on all interactive elements (▶ symbol + highlighted border). Focus indicator must have 3:1 contrast with background.
- **Text sizing:** Respect user's terminal font size settings. No application-enforced minimum sizes. Test at various terminal font configurations (10pt-16pt typical range).
- **Color independence:** Never rely solely on color to convey information. Always pair with symbols/text (e.g., "✓ Completed" in green, not just green text).

**Interaction:**
- **Keyboard navigation:** 100% keyboard accessible - no mouse required. All functions available via single-key shortcuts or arrow key navigation.
- **Screen reader support:** Use semantic Textual widgets (DataTable, Modal, etc.) which provide ARIA-like hints. Test with terminal screen readers (e.g., ORCA on Linux, VoiceOver on macOS with Terminal app).
- **Touch targets:** N/A for terminal applications (keyboard-only interaction model).
- **Navigation order:** Logical tab/focus order follows visual layout (top to bottom, left to right within tables).

**Content:**
- **Alternative text:** All status symbols must have text equivalents (● Pending, ✓ Completed, etc.). Status columns include both symbol and label.
- **Heading structure:** Use visual hierarchy (UPPERCASE for H1, Title Case for H2, etc.) to indicate structure. Screen readers interpret these as logical sections.
- **Form labels:** All input modals (CreateUnitModal, CreateFoodModal) include clear field labels. Error messages reference specific fields.
- **Progress indicators:** Include both visual (progress bar) and textual (percentage) representations.

## Testing Strategy

**Manual Testing:**
- **Keyboard-only navigation:** Complete all workflows without mouse/touchpad. Verify focus visibility and logical navigation order.
- **Screen reader testing:** Use ORCA (Linux), NVDA (Windows), VoiceOver (macOS) with terminal application. Verify table contents, modal dialogs, and status changes are announced.
- **Color blindness simulation:** Test with terminal color schemes for deuteranopia, protanopia, tritanopia. Verify status symbols remain distinguishable.
- **High contrast mode:** Test with light-on-dark and dark-on-light terminal themes. Verify all UI elements remain visible.

**Automated Testing:**
- **Contrast validation:** Verify color pairings meet WCAG AA ratios using terminal color analysis tools.
- **Widget accessibility:** Ensure all Textual components use proper semantic roles (table, dialog, button).

**User Testing:**
- **Power user validation:** Test with actual Mealie users who rely on keyboard navigation for efficiency.
- **Assistive technology users:** Recruit terminal users who rely on screen readers for feedback on navigation clarity.

---
