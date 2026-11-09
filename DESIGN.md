---
name: Eve
description: Precision shift scheduling, organization rosters, and real-time attendance coordination inspired by Apple.com.
colors:
  apple-blue: "#0071e3"
  apple-blue-link: "#0066cc"
  apple-bg: "#f5f5f7"
  apple-bg-dark: "#000000"
  apple-surface: "#ffffff"
  apple-surface-dark: "#1d1d1f"
  apple-pro-radial: "#2c2c2e"
  apple-text: "#1d1d1f"
  apple-text-secondary: "#515154"
  apple-text-tertiary: "#5c5c61"
  apple-text-dark-secondary: "#a1a1a6"
  apple-border: "#d2d2d7"
  apple-segmented-track: "rgba(118, 118, 128, 0.12)"
  apple-progress-track: "rgba(120, 120, 128, 0.16)"
  apple-green: "#186a3b"
  apple-orange: "#9a4406"
  apple-red: "#c50013"
  apple-purple: "#6332b8"
typography:
  stat-figure:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif"
    fontSize: "clamp(2.75rem, 4.5vw, 4rem)"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.04em"
  display:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif"
    fontSize: "clamp(2.5rem, 5vw, 3.75rem)"
    fontWeight: 700
    lineHeight: 1.06
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif"
    fontSize: "clamp(1.85rem, 3.5vw, 2.75rem)"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.03em"
  auth-title:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif"
    fontSize: "32px"
    fontWeight: 600
    lineHeight: 1.15
  title:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif"
    fontSize: "clamp(1.35rem, 2.2vw, 1.75rem)"
    fontWeight: 600
    lineHeight: 1.16
    letterSpacing: "-0.024em"
  lead:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif"
    fontSize: "clamp(1.1rem, 1.8vw, 1.35rem)"
    fontWeight: 400
    lineHeight: 1.38
  subhead:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif"
    fontSize: "19px"
    fontWeight: 400
    lineHeight: 1.4
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.47
    letterSpacing: "-0.022em"
  input-text:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.4
  body-secondary:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.48
  ui-control:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif"
    fontSize: "14px"
    fontWeight: 500
    lineHeight: 1.35
  ui-compact:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif"
    fontSize: "13px"
    fontWeight: 500
    lineHeight: 1.35
  label:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: 1.35
    letterSpacing: "-0.008em"
  micro-label:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif"
    fontSize: "11px"
    fontWeight: 600
    lineHeight: 1.2
rounded:
  hairline: "2px"
  xs: "8px"
  sm: "12px"
  badge: "14px"
  md: "18px"
  lg: "24px"
  pill: "980px"
spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "32px"
  xl: "56px"
  xxl: "64px"
components:
  button-primary:
    backgroundColor: "{colors.apple-blue}"
    textColor: "{colors.apple-surface}"
    rounded: "{rounded.pill}"
    padding: "10px 22px"
  button-secondary:
    backgroundColor: "{colors.apple-surface}"
    textColor: "{colors.apple-blue-link}"
    rounded: "{rounded.pill}"
    padding: "10px 22px"
---

# Design System: Eve

## Overview

**Creative North Star: "Cupertino Editorial Precision"**

Eve adopts the spatial architecture, typographic authority, and tactile restraint of Apple's official website (`apple.com`). Instead of dense admin chrome or nested Bootstrap boxes, every page is structured as a sequence of full-bleed alternating chapters—pure white editorial stages (`#ffffff`) paired with warm aluminum-gray Bento canvases (`#f5f5f7` in Daylight, `#000000` / `#161617` in Pro Dark).

Hierarchy is carried by scale, negative space, and hairline specification strips rather than decorative borders or uppercase kicker labels. Interactive controls use pill geometry (`980px`) paired with directional chevron links (`Explore organizations ›`) to establish an unmistakable distinction between primary actions and secondary navigation.

**Key Characteristics:**
- 44px frosted-glass GlobalNav paired with 52px sticky LocalSubNav chapter bars
- Full-bleed alternating section rhythm (`.apple-section-white` and `.apple-section-canvas`)
- Asymmetric 12-column Bento grids (`8 + 4` and `7 + 5` spans) with zero nested cards
- Hairline specification strips (`.apple-spec-strip`) and clean horizontal row lists (`.apple-row-list`)
- Tabular numerals (`font-variant-numeric: tabular-nums`) across all dates, shift windows, and telemetry counters

## Colors

The palette balances warm daylight neutrals and obsidian dark surfaces with a single authoritative interactive accent.

### Primary
- **Apple Interactive Blue** (`#0071e3`): Reserved exclusively for primary pill CTAs, active progress bars, focus rings, and interactive highlights.
- **Editorial Link Blue** (`#0066cc` Light / `#2997ff` Dark): Used for chevron text CTAs, secondary outline buttons, and inline links.

### Secondary
- **Verification Green** (`#186a3b` Light / `#30d158` Dark): Indicates confirmed attendance, completed shifts, and active role administration.
- **Pending Amber** (`#9a4406` Light / `#ff9f0a` Dark): Marks assigned shifts awaiting staff confirmation.
- **Critical Crimson** (`#c50013` Light / `#ff453a` Dark): Used for declined/cancelled states, destructive actions, and calendar month headers.
- **Executive Violet** (`#6332b8` Light / `#bf5af2` Dark): Identifies Organization Owner badges.

### Neutral
- **Warm Aluminum Canvas** (`#f5f5f7` Light / `#000000` Dark): Primary page canvas behind Bento tiles.
- **Pure Editorial Surface** (`#ffffff` Light / `#161617` Dark): Elevated Bento tiles, full-bleed hero stages, and table surfaces.
- **Pro Obsidian Surface** (`#1d1d1f`): High-contrast dark feature tiles used for contrast within light pages.
- **Obsidian Ink** (`#1d1d1f` Light / `#f5f5f7` Dark): Primary headline and body copy.
- **Graphite Secondary** (`#515154` Light / `#a1a1a6` Dark): Lead copy and supporting descriptions (`>= 7.5:1` contrast).
- **Titanium Caption** (`#5c5c61` Light / `#98989d` Dark): WCAG AA-compliant captions, timestamps, and table column headers (`>= 6.0:1` contrast).
- **Hairline Divider** (`#d2d2d7` / `rgba(0, 0, 0, 0.08)`): 1px structural dividers for specification strips and row lists.

### Named Rules
**The Single Accent Rule.** Apple Interactive Blue (`#0071e3`) appears only on actionable controls and live progress indicators—never as decorative card borders or background fills.
**The Contrast Floor Rule.** All functional text, including `12px` captions and input placeholders, maintains at least `4.5:1` contrast against both `#ffffff` surfaces and `#f5f5f7` canvases.

## Typography

**Display Font:** `-apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", sans-serif`
**Body Font:** `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif`

**Character:** Tight, confident negative tracking on large display headlines paired with open, effortless readability at body and caption scales.

### Hierarchy
- **Display** (`700`, `clamp(2.5rem, 5vw, 3.75rem)`, `1.06` line-height, `-0.035em` tracking): Centered hero greetings and primary landing statements.
- **Headline** (`600`, `clamp(1.85rem, 3.5vw, 2.75rem)`, `1.1` line-height, `-0.03em` tracking): Section titles introducing Bento grids and shift lineups.
- **Title** (`600`, `clamp(1.35rem, 2.2vw, 1.75rem)`, `1.16` line-height, `-0.024em` tracking): Bento tile titles and modal/card headers.
- **Body** (`400`, `17px`, `1.47` line-height, `-0.022em` tracking, max `65ch`): Primary interface prose and descriptions.
- **Label** (`500`, `12px`, `1.35` line-height, `-0.008em` tracking): GlobalNav items, status pills, and specification labels (never below `11px`).

### Named Rules
**The No-Kicker Rule.** Headings never carry uppercase eyebrow or kicker labels above them; the headline's scale and phrasing establish context on their own.
**The Tabular Telemetry Rule.** Every date, time window, member count, and percentage uses `font-variant-numeric: tabular-nums`.

## Layout

Pages alternate between full-bleed white stages (`.apple-section-white`, `56px` vertical padding) and warm gray canvases (`.apple-section-canvas`, `64px` vertical padding). Content is constrained to `.apple-container` (`1024px`) for navigation and forms, or `.apple-container-wide` (`1120px`) for asymmetric 12-column Bento grids (`.apple-bento-grid`, `20px` gap). On viewports below `992px`, multi-column Bento spans (`8+4`, `7+5`, `6+6`) collapse cleanly to full-width 12-column stacks.

## Elevation & Depth

Depth is achieved primarily through surface luminance contrast (`#ffffff` tiles resting on `#f5f5f7` canvas) reinforced by a single ambient offset shadow. Navigation bars float above scrolling content using translucent frosted glass (`backdrop-filter: saturate(180%) blur(20px)`).

### Shadow Vocabulary
- **Card Rest** (`box-shadow: 0 6px 24px rgba(0, 0, 0, 0.04)`): Subtle ambient lift on `.apple-tile` surfaces.
- **Interactive Hover** (`box-shadow: 0 12px 36px rgba(0, 0, 0, 0.08)`): Elevated state when hovering interactive Bento tiles.
- **Floating Overlay** (`box-shadow: 0 20px 50px rgba(0, 0, 0, 0.12)`): Reserved for keyboard skip links and floating popovers.

### Named Rules
**The Zero-Nested-Box Rule.** Cards and Bento tiles never contain smaller bordered cards inside them; internal metadata is separated strictly with 1px hairline specification strips (`.apple-spec-strip`).

## Shapes

- **Bento Tiles:** Generous `24px` continuous-feel corners (`--apple-radius-lg`) with `32px` internal padding (`24px` on mobile).
- **Buttons, Status Badges & Segmented Controls:** Full pill geometry (`980px`).
- **Form Inputs & Demo Credential Pills:** Tactile `12px` rounded rectangles (`--apple-radius-sm`) with `50px` height.
- **Calendar Date Badges:** `14px` squircle badges (`58×58px`) displaying uppercase month and tabular day numeral.

## Components

### Buttons
- **Shape:** Pill-shaped (`980px` radius) with `42px` default height (`36px` compact `.btn-apple-sm`, `48px` large `.btn-apple-lg`).
- **Primary (`.btn-apple-primary`):** Solid `#0071e3` background, `#ffffff` text, `0.65rem 1.4rem` padding.
- **Hover / Focus:** Transitions to `#0077ed` on hover, `scale(0.985)` on active press, and `2px` `#0066cc` outline on `:focus-visible`.
- **Secondary (`.btn-apple-secondary`) & Chevron CTA (`.apple-link-cta`):** `1px solid #0066cc` pill outline button, or borderless `#0066cc` text link with animated right chevron (`›`).

### Chips
- **Style:** Semantic tinted pill badges (`.eve-status-pill`, `.eve-role-badge`) with `0.3rem 0.78rem` padding and `12px` (`0.75rem`) medium text.
- **State:** Includes a `6px` status indicator dot (`.eve-status-dot`) colored to match `Confirmed` (green), `Pending` (amber), `Completed` (blue), or `Declined` (red).

### Cards / Containers
- **Corner Style:** `24px` radius (`.apple-tile`).
- **Background:** `#ffffff` in Light mode (`#161617` in Dark mode); `.apple-tile-pro` uses a radial dark obsidian gradient (`#2c2c2e` to `#161617`).
- **Shadow Strategy:** Ambient offset shadow (`0 6px 24px rgba(0, 0, 0, 0.04)`).
- **Border:** `1px solid rgba(0, 0, 0, 0.06)` (`rgba(255, 255, 255, 0.08)` in Dark mode).
- **Internal Padding:** `32px` desktop, `24px` mobile.

### Inputs / Fields
- **Style:** `1px solid #d2d2d7` stroke, `#ffffff` background, `12px` radius, `50px` minimum height, `16px` font size to prevent mobile zoom.
- **Focus:** `#0071e3` border with `0 0 0 4px rgba(0, 113, 227, 0.28)` focus halo.
- **Error / Disabled:** Readonly/disabled inputs shift to `#f5f5f7` background with `#515154` text.

### Navigation
- **GlobalNav (`.eve-navbar`):** `44px` sticky frosted bar with brand mark on the left, centered `12px` link list (`.eve-nav-list`) with `1.5px` active underline indicator, and user profile chip + Sign Out action on the right.
- **LocalNav (`.apple-localnav`):** `52px` sticky secondary bar (`top: 44px`) carrying the current module title on the left and contextual actions (`Schedule Event`, `Edit`, status switcher) on the right.

## Do's and Don'ts

### Do:
- **Do** alternate `.apple-section-white` and `.apple-section-canvas` to create clear chapter transitions across long pages.
- **Do** use `.apple-spec-strip` and `.apple-row-list` with `1px` hairlines (`--apple-divider`) to organize metadata without adding box clutter.
- **Do** keep all functional UI text at `11px` or larger and interactive touch targets at `36px–44px` minimum height.

### Don't:
- **Don't** place uppercase eyebrow/kicker labels above headings.
- **Don't** nest bordered cards or shaded boxes inside `.apple-tile` containers.
- **Don't** use 4 equal-width icon+heading+blurb cards as a page scaffold; use asymmetric Bento spans (`8+4`, `7+5`, `6+6`) or horizontal row lists instead.
