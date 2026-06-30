---
name: Cognitive Luminescence
colors:
  surface: '#f8f9fd'
  surface-dim: '#d9dade'
  surface-bright: '#f8f9fd'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3f7'
  surface-container: '#edeef2'
  surface-container-high: '#e7e8ec'
  surface-container-highest: '#e1e2e6'
  on-surface: '#191c1f'
  on-surface-variant: '#474555'
  inverse-surface: '#2e3134'
  inverse-on-surface: '#eff1f5'
  outline: '#787586'
  outline-variant: '#c8c4d7'
  surface-tint: '#5843dc'
  primary: '#4228c8'
  on-primary: '#ffffff'
  primary-container: '#5b47e0'
  on-primary-container: '#dfdaff'
  inverse-primary: '#c6bfff'
  secondary: '#5c5e65'
  on-secondary: '#ffffff'
  secondary-container: '#dedfe8'
  on-secondary-container: '#60626a'
  tertiary: '#7d3500'
  on-tertiary: '#ffffff'
  tertiary-container: '#a24700'
  on-tertiary-container: '#ffd6c2'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e4dfff'
  primary-fixed-dim: '#c6bfff'
  on-primary-fixed: '#160066'
  on-primary-fixed-variant: '#3f23c5'
  secondary-fixed: '#e1e2ea'
  secondary-fixed-dim: '#c4c6ce'
  on-secondary-fixed: '#191c22'
  on-secondary-fixed-variant: '#44474d'
  tertiary-fixed: '#ffdbca'
  tertiary-fixed-dim: '#ffb68f'
  on-tertiary-fixed: '#331200'
  on-tertiary-fixed-variant: '#773200'
  background: '#f8f9fd'
  on-background: '#191c1f'
  surface-variant: '#e1e2e6'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  sidebar-width: 280px
  max-content-width: 1200px
---

## Brand & Style
The design system focuses on a **Corporate / Modern** aesthetic infused with subtle **Glassmorphism** to evoke a sense of high-intelligence and premium education. It balances a deep, focused sidebar environment with a high-clarity, spacious main workspace. The goal is to provide a "flow state" environment for AI-assisted learning—professional, disciplined, and technologically advanced yet approachable.

The style utilizes crisp 1px borders, generous whitespace, and purposeful translucency to create a tiered information architecture. It is designed for adult learners and professionals who value precision and a distraction-free cognitive experience.

## Colors
The palette is rooted in contrast. The **Deep Slate** (#1A1D23) provides a grounding, high-focus area for navigation and persistent tools. The **Soft Off-White** (#F5F6FA) workspace reduces eye strain during long reading sessions.

**Refined Indigo-Violet** (#5B47E0) acts as the primary signal color, used for active states, primary actions, and AI-related highlights. **Soft Amber** (#EF6C00) is reserved for warning states and high-priority reminders, ensuring they remain sophisticated and not overly aggressive.

## Typography
The system utilizes **Inter** exclusively to maintain a systematic, utilitarian feel. The hierarchy is highly disciplined:
- **Headings (600):** Use for page titles and section headers. Slightly tightened letter spacing on larger sizes for a premium editorial feel.
- **Labels (500):** Optimized for UI controls, navigation items, and button text to provide clear affordance without the weight of a heading.
- **Body (400):** Set with comfortable line heights to ensure readability of AI-generated content and educational material.

## Layout & Spacing
The layout follows a **Fixed-Fluid Hybrid** model. A fixed sidebar (280px) houses the deep-slate navigation, while the main content area utilizes a fluid grid that caps at 1200px to maintain line-length readability.

- **Grid:** 12-column system for the main workspace.
- **Gutters:** 24px on desktop, scaling down to 16px on mobile.
- **Margins:** 32px safe area on desktop containers.
- **Rhythm:** An 8px linear scale (with a 4px half-step for tight UI elements) governs all padding and margins.

## Elevation & Depth
This design system rejects heavy shadows in favor of **Glassmorphism** and **Tonal Layers** to represent depth.

- **Tier 1 (AI Insights):** Uses a translucent Indigo tint `rgba(91, 71, 224, 0.08)` with a 12px backdrop blur. This is reserved for AI-generated suggestions or overlays.
- **Tier 2 (Standard Surfaces):** Uses a white translucent base `rgba(255, 255, 255, 0.6)` with an 8px blur, perfect for floating panels or navigation headers over content.
- **Tier 3 (Contextual Alerts):** A subtle amber-tinted glass `rgba(255, 248, 240, 0.7)` for warnings or high-priority educational callouts.
- **Hover States:** Transition from a flat border to a `0 4px 12px rgba(0, 0, 0, 0.05)` shadow over 0.15s to indicate interactivity.

## Shapes
The shape language is precise and varied based on component scale:
- **Cards & Large Containers:** Use a 12px radius for a soft, modern container feel.
- **Buttons & Inputs:** Use an 8px radius to maintain a professional, organized look.
- **Badges & Pills:** Use a full 999px radius (Pill-shaped) to distinguish them from interactive buttons.
- **Borders:** Fixed at 1px width. Use `#E4E6ED` for standard containers and `rgba(91, 71, 224, 0.2)` for primary-accented glass elements.

## Components
- **Buttons:** Primary buttons use the Indigo-Violet background with white text. Hover states trigger the subtle 0.05 opacity shadow and a slight brightness increase.
- **Input Fields:** 1px solid `#E4E6ED` border, 8px radius. On focus, the border transitions to Primary Indigo-Violet with a 2px soft glow (0.15s transition).
- **Cards:** White surface, 12px radius. In the main content area, cards should have no shadow by default, gaining the subtle hover shadow only when interactive.
- **Chips/Pills:** Used for categories or tags. These use the 999px radius. AI-generated tags should use Tier 1 Glassmorphism.
- **Sidebar Items:** High-contrast text on `#1A1D23`. Active states should use a left-aligned 4px Indigo-Violet indicator and a subtle background tint.
- **Progress Bars:** Thin (4px - 6px) with a rounded 999px cap. Use Primary Indigo for completed progress and the neutral background for the track.