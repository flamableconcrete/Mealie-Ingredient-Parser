# User Interface Design Goals

## Overall UX Vision

The interface prioritizes **efficient batch decision-making** through clear visual grouping, minimal keystrokes, and progressive disclosure. Users should feel in control of large-scale operations while the TUI handles the mechanical repetition. The experience should feel like "teaching the system once, watching it apply everywhere" rather than "clicking through endless modals." Visual feedback must clearly distinguish between single-item actions and batch operations to prevent accidental mass changes.

## Key Interaction Paradigms

- **Keyboard-first navigation:** All core workflows accessible via single-key shortcuts (e.g., 'b' for batch mode, 'r' for review, Enter to confirm)
- **Preview-before-commit:** Every batch operation shows affected ingredients in a confirmation table before execution
- **Progressive disclosure:** Start with high-level pattern groups, drill down to individual ingredients only when needed
- **Stateful progress:** Visual indicators show processed/remaining/skipped counts; ability to resume interrupted sessions
- **Dual-mode operation:** Toggle between batch mode (pattern-based grouping) and sequential mode (current behavior) without losing progress

## Core Screens and Views

- **Pattern Group Screen:** Table view showing unique unparsed units/foods with action options (create, skip, review instances)
- **Batch Preview Screen:** Confirmation dialog displaying all ingredients that will be affected by a batch operation with accept/cancel options
- **Sequential Review Screen (existing):** Current ingredient-by-ingredient modal workflow, preserved for edge cases and user preference
- **Progress Dashboard:** Summary statistics showing overall parsing progress, recent batch operations, and remaining work

## Target Devices and Platforms

**Cross-Platform Terminal Environments:**
- Linux/macOS/Windows terminal emulators (iTerm2, Windows Terminal, GNOME Terminal, etc.)
- Minimum 80x24 character display, optimized for 120x40+ for richer tables
- SSH-compatible for remote Mealie server administration
- No GUI dependencies—pure terminal-based operation

---
