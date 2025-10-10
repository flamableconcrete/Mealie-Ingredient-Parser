# Performance Considerations

## Performance Goals

- **Page Load:** Initial LoadingScreen data fetch < 5 seconds for 1000 recipes (dependent on Mealie API response time)
- **Interaction Response:** Keyboard input to visual feedback < 100ms for all UI interactions (pattern selection, modal open, table navigation)
- **Animation FPS:** Maintain 30+ FPS for animations on typical hardware (60 FPS target on modern systems)
- **Batch Operation Throughput:** Process 500 ingredient updates in ~15 minutes total (API-bound, ~1.8 seconds per pattern including user decision time)

## Design Strategies

**Pattern Analysis Optimization:**
- Perform pattern grouping during LoadingScreen asynchronously (don't block UI)
- Use efficient data structures (dictionaries/sets) for pattern matching (O(1) lookup vs. O(n) iteration)
- Limit similarity detection to top 100 most common patterns (avoid O(n²) comparisons on full dataset)

**Table Rendering Efficiency:**
- Implement virtual scrolling for tables > 50 rows (only render visible rows + buffer)
- Use Textual's built-in DataTable widget which optimizes large dataset rendering
- Cache table cell formatting (don't recompute status badges on every render)

**Modal Responsiveness:**
- Lazy-load preview table data (fetch affected ingredients only when BatchPreviewScreen opens, not during pattern analysis)
- Paginate preview tables if > 100 ingredients (show 50 at a time with "scroll for more" indicator)
- Debounce search input in SelectFoodModal (300ms delay before filtering to avoid re-rendering on every keystroke)

**State Management:**
- Write state file asynchronously after batch operations complete (don't block UI)
- Compress state JSON if > 100KB (gzip compression for large session states)
- Use incremental state updates rather than full rewrites

**Memory Management:**
- Release recipe data from memory after pattern analysis completes (only store pattern groups, not full recipe objects)
- Limit operation history in dashboard to last 50 operations (older entries archived to log file)
- Clear completed patterns from active memory after user confirmation (maintain in state file only)

**Network Optimization:**
- Reuse aiohttp session with connection pooling (already implemented in codebase)
- Implement request timeout (10 seconds for API calls, 3 retries with exponential backoff)
- Batch ingredient updates in groups of 10 with concurrent API calls (asyncio.gather) rather than strict sequential processing

---
