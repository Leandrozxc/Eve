---
name: Eve
description: Tactile editorial minimalism for shift scheduling, organization rosters, and real-time attendance coordination.
colors:
  eve-obsidian: "#141413"
  eve-obsidian-hover: "#292927"
  eve-emerald: "#0d6e55"
  eve-emerald-bright: "#10b981"
  eve-emerald-dark-link: "#34d399"
  eve-mint-pro: "#5eead4"
  eve-canvas: "#faf9f5"
  eve-canvas-dark: "#0c0e0d"
  eve-surface: "#ffffff"
  eve-surface-subtle: "#f2f0e8"
  eve-surface-dark: "#151917"
  eve-pro-forest: "#162420"
  eve-pro-deep: "#111715"
  eve-text: "#141413"
  eve-text-secondary: "#4a4945"
  eve-text-tertiary: "#5c5b56"
  eve-text-dark: "#f4f3ef"
  eve-text-dark-secondary: "#a8a7a1"
  eve-text-dark-tertiary: "#96958e"
  eve-pro-muted: "#b0b8b4"
  eve-border: "#dfddd4"
  eve-amber: "#9a4406"
  eve-crimson: "#b91c1c"
  eve-indigo: "#4f46e5"
typography:
  stat-figure:
    fontFamily: "'JetBrains Mono', ui-monospace, monospace"
    fontSize: "clamp(2.35rem, 3.8vw, 3.25rem)"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.04em"
  display:
    fontFamily: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "clamp(2rem, 3.8vw, 2.85rem)"
    fontWeight: 800
    lineHeight: 1.12
    letterSpacing: "-0.032em"
  headline:
    fontFamily: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "clamp(1.5rem, 2.6vw, 2.1rem)"
    fontWeight: 700
    lineHeight: 1.16
    letterSpacing: "-0.026em"
  title:
    fontFamily: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "clamp(1.2rem, 1.8vw, 1.45rem)"
    fontWeight: 700
    lineHeight: 1.22
    letterSpacing: "-0.02em"
  date-day:
    fontFamily: "'JetBrains Mono', ui-monospace, monospace"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.1
  lead:
    fontFamily: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.55
  body:
    fontFamily: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "-0.011em"
  body-secondary:
    fontFamily: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.52
  ui-control:
    fontFamily: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.35
  ui-compact:
    fontFamily: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    lineHeight: 1.35
  label:
    fontFamily: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.35
  micro-mono:
    fontFamily: "'JetBrains Mono', ui-monospace, monospace"
    fontSize: "11px"
    fontWeight: 600
    lineHeight: 1.2
rounded:
  xs: "6px"
  tab: "7px"
  mark: "8px"
  sm: "10px"
  md: "14px"
  lg: "18px"
  xl: "22px"
  pill: "980px"
spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "28px"
  xl: "44px"
  xxl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.eve-obsidian}"
    textColor: "{colors.eve-surface}"
    rounded: "{rounded.sm}"
    padding: "10px 20px"
  button-secondary:
    backgroundColor: "{colors.eve-surface}"
    textColor: "{colors.eve-text}"
    rounded: "{rounded.sm}"
    padding: "10px 20px"
---

# Design System: Eve

## Overview

**Creative North Star: "Chronometer Studio Minimalism"**

Eve pairs the calm negative space and restraint of high-craft minimalist interfaces with its own unmistakable identity rooted in precision timekeeping and editorial paper surfaces. Rather than mimicking Apple's `#0071e3` blue store chrome, Eve combines a **Warm Alabaster Paper** canvas (`#faf9f5`), **Obsidian Ink** (`#141413`) tactile squircle buttons, and **Deep Forest Emerald** (`#0d6e55`) live-telemetry accents.

Typography is driven by **Plus Jakarta Sans** for geometric, approachable workspace headers paired with **JetBrains Mono** for shift windows (`09:00 AM – 05:00 PM`), calendar badges, table column headers, and attendance readiness percentages.

**Key Characteristics:**
- Floating glassmorphic studio header (`.eve-navbar`) with an inset segmented navigation track
- Left-aligned workspace headers (`.eve-workspace-header`) that pair clear context with right-aligned action buttons
- Asymmetric 12-column Bento grids (`8 + 4` and `7 + 5` spans) with zero nested cards
- Tactile `10px`-radius buttons and `6px`-radius status tags instead of generic full-capsule pills
- Precision `JetBrains Mono` numerals (`tabular-nums`) across all shift windows, dates, and counters

## Colors

Warm stone neutrals paired with Obsidian Ink primary actions and Deep Forest Emerald telemetry accents.

### Primary
- **Obsidian Ink** (`#141413` Light / `#10b981` Dark): Primary button surface and high-authority foreground.
- **Deep Forest Emerald** (`#0d6e55` Light / `#34d399` Dark): Directional text links, progress bars, calendar month headers, and confirmed shift status.

### Secondary
- **Pending Amber** (`#9a4406` Light / `#fbbf24` Dark): Indicates assigned shifts awaiting confirmation.
- **Critical Crimson** (`#b91c1c` Light / `#f87171` Dark): Marks cancelled/declined states and destructive actions.
- **Executive Indigo** (`#4f46e5` Light / `#818cf8` Dark): Identifies Organization Owner badges.

### Neutral
- **Warm Alabaster Canvas** (`#faf9f5` Light / `#0c0e0d` Dark): Primary background canvas.
- **Pure Ivory Surface** (`#ffffff` Light / `#151917` Dark): Elevated Bento tiles and form containers.
- **Warm Stone Subtle** (`#f2f0e8` Light / `#1e2421` Dark): Segmented control tracks, date badges, and table headers.
- **Warm Stone Border** (`#dfddd4` Light / `#2c3330` Dark): 1px structural borders on tiles and inputs.

## Typography

**Display & UI Font:** `Plus Jakarta Sans`, `-apple-system`, `sans-serif`
**Chronometer & Telemetry Font:** `JetBrains Mono`, `ui-monospace`, `monospace`

### Hierarchy
- **Display** (`800`, `clamp(2rem, 3.8vw, 2.85rem)`, `1.12` line-height, `-0.032em` tracking): Primary workspace greetings.
- **Headline** (`700`, `clamp(1.5rem, 2.6vw, 2.1rem)`, `1.16` line-height, `-0.026em` tracking): Page and section headers.
- **Title** (`700`, `clamp(1.2rem, 1.8vw, 1.45rem)`, `1.22` line-height, `-0.02em` tracking): Tile and card titles.
- **Body** (`400`, `16px`, `1.5` line-height): Primary interface prose.
- **Chronometer Mono** (`600`, `11px`–`18px`, `JetBrains Mono`): Shift hours, calendar badges, table headers, and readiness figures.

## Layout

Pages use left-aligned workspace headers (`.eve-workspace-header`) on a crisp white stage (`.apple-section-white`) followed by asymmetric 12-column Bento grids (`.apple-bento-grid`) on the Warm Alabaster canvas (`.apple-section-canvas`).

## Elevation & Depth

Surfaces rely on crisp `1px solid #dfddd4` borders and a subtle tactile contact shadow (`0 2px 10px rgba(20, 20, 19, 0.03)`).

## Shapes

- **Bento Tiles:** `18px` radius (`--apple-radius-lg`) with `28px` internal padding.
- **Buttons, Inputs & Date Badges:** `10px` tactile squircle radius (`--apple-radius-sm`).
- **Status & Role Badges:** `6px` architectural tag radius (`--apple-radius-xs`).

## Components

### Buttons
- **Primary (`.btn-apple-primary`):** Solid `#141413` background (`#10b981` in Dark mode), `10px` radius, `42px` height.
- **Secondary (`.btn-apple-secondary`):** `#ffffff` surface with `1px solid #dfddd4` border and `10px` radius.

### Navigation
- **Floating Studio Header (`.eve-navbar`):** `54px` floating rounded bar (`14px` radius) with emerald clock-history mark, inset pill-track navigation list, and user profile chip.

## Do's and Don'ts

### Do:
- **Do** use `JetBrains Mono` (`.tabular-nums`) for all time windows, dates, and numeric telemetry.
- **Do** use left-aligned workspace headers (`.eve-workspace-header`) with right-aligned primary actions.

### Don't:
- **Don't** place uppercase eyebrow/kicker labels above headings.
- **Don't** nest bordered cards inside `.apple-tile` containers.
