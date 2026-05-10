# changelog

all notable changes to this project will be documented in this file.

## [0.1.0] - 2026-05-10

### added
- technical workstation refactor with 120 fps rendering engine.
- responsive high-density layout that gracefully handles terminal resizing.
- variable anchor point support (unlocked p0 and p3 editing).
- searchable preset explorer with 100+ categories (classic, cinematic, game, physics).
- fully functional dna intensity system: dynamically scales control point deviation from center for real-time visual exaggeration and physics modulation.
- velocity momentum graph and technical spectrum analysis.
- cross-platform shift-tab input handling via native modifier polling (windows) and ansi escape sequences (unix).
- physics simulation panel (tension and friction derivation).
- history breadcrumb trail for coordinate tracking.
- swiftui export format support.
- pulse animation preview with high-contrast tracking.
- universal lowercase formal minimalist aesthetic.

### fixed
- resolved horizontal tail artifacts and braille rendering gaps with new column-by-column bresenham rasterization.
- prevented rendering engine from plotting control points out of canvas bounds.
- resolved blocking input loop causing animation staggering.
- fixed distorted layout artifacts during terminal resizing via rich layout migration.
- corrected markup rendering issues in preset browser.
- resolved import errors and type safety violations in state management.
- fixed silent exit issues by refining console flush and error handling.
