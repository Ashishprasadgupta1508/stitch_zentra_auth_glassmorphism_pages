---
name: Learnify
colors:
  surface: '#f9f9ff'
  surface-dim: '#d8dae2'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3fc'
  surface-container: '#ecedf6'
  surface-container-high: '#e6e8f0'
  surface-container-highest: '#e1e2ea'
  on-surface: '#191c22'
  on-surface-variant: '#474555'
  inverse-surface: '#2d3037'
  inverse-on-surface: '#eff0f9'
  outline: '#787586'
  outline-variant: '#c8c4d7'
  surface-tint: '#5843dc'
  primary: '#4228c8'
  on-primary: '#ffffff'
  primary-container: '#5b47e0'
  on-primary-container: '#dfdaff'
  inverse-primary: '#c6bfff'
  secondary: '#086b53'
  on-secondary: '#ffffff'
  secondary-container: '#a0f3d4'
  on-secondary-container: '#167159'
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
  secondary-fixed: '#a0f3d4'
  secondary-fixed-dim: '#84d6b9'
  on-secondary-fixed: '#002117'
  on-secondary-fixed-variant: '#00513e'
  tertiary-fixed: '#ffdbca'
  tertiary-fixed-dim: '#ffb68f'
  on-tertiary-fixed: '#331200'
  on-tertiary-fixed-variant: '#773200'
  background: '#f9f9ff'
  on-background: '#191c22'
  surface-variant: '#e1e2ea'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  sidebar_width: 240px
  gutter: 24px
  margin_container: 32px
  stack_sm: 8px
  stack_md: 16px
  stack_lg: 24px
---

## Brand & Style
The design system establishes a high-performance environment for AI-assisted education. It balances a "senior management console" aesthetic—characterized by precision, structural integrity, and clarity—with a warm, operational tone that feels supportive rather than sterile. 

The aesthetic is a hybrid of **Minimalism** and **Glassmorphism**, specifically utilized for AI-driven insights to distinguish machine intelligence from static curriculum data. The interface prioritizes high-density information architecture without sacrificing legibility, using 1px borders and subtle hover interactions to communicate state and depth. The goal is to evoke a sense of focused productivity and institutional reliability.

## Colors
The palette is rooted in a professional "Dark Mode" sidebar for navigation, providing a strong visual anchor, while the main workspace utilizes a high-clarity "Light Mode" background. 

- **Primary Indigo-Violet:** Used for core actions, progress indicators, and primary navigation states.
- **Teacher Secondary Teal:** Reserved for instructor-specific workflows and affirmative "success" states in a pedagogical context.
- **Warning Amber:** Utilized for deadlines, low-engagement alerts, and critical system notifications.
- **Class Palette:** A curated set of five professional tones used to categorize different subjects or classrooms, ensuring distinct visual identification in dashboard views.
- **AI Surfaces:** Distinctive light violet tint with backdrop blurring to separate AI recommendations from standard content.

## Typography
The system uses **Inter** exclusively to maintain a systematic, utilitarian, and professional feel. 

- **Headlines:** Use tighter letter spacing and heavier weights to provide clear hierarchy in data-heavy screens.
- **Body:** Standardized at 14px for density, with 16px reserved for long-form reading materials or lesson content.
- **Labels:** Small caps or bold weights are used for metadata, stat labels, and table headers to provide clear distinction from body text.
- **Scalability:** Large display headings scale down significantly for mobile to prevent wrapping issues in narrow dashboard panels.

## Layout & Spacing
The layout follows a **Fixed Sidebar + Fluid Content** model. The 240px sidebar stays persistent to anchor the user's mental map of the platform.

- **The Grid:** A 12-column fluid grid is used for the main content area with 24px gutters. 
- **The Dashboard:** Employs an `aspect-square` logic for primary course/class cards to maintain a structured, "console" feel regardless of viewport width.
- **Vertical Rhythm:** A base-8 unit system is used for internal component padding, while large-scale layout sections are separated by 32px or 48px to prevent visual clutter.
- **Breakpoints:** On tablet, the sidebar collapses into a narrow icon-only rail. On mobile, the sidebar becomes a bottom navigation bar or a hidden drawer, and cards stack vertically.

## Elevation & Depth
Depth in this design system is communicated through **structural layering** rather than heavy shadows.

- **Level 0 (Floor):** Main Background (#F5F6FA), flat.
- **Level 1 (Cards):** Surface-white with a 1px solid border (#E4E6ED). No shadow in default state.
- **Level 2 (Interaction):** On hover, cards transition to a subtle "lift" using a soft, neutral shadow: `0 4px 12px rgba(26, 29, 35, 0.08)`.
- **AI Layer:** Glassmorphism is reserved for AI interactions. Use a `backdrop-filter: blur(8px)` with a 5% opacity primary color tint. This creates a "heads-up display" effect over the standard curriculum content.

## Shapes
The system utilizes a **Soft (0.25rem)** rounding philosophy to maintain the professional, management-console vibe. Sharp corners are avoided to keep the "educational/warm" intent, but large rounded corners are avoided to prevent a "toy-like" appearance.

- **Base Components:** 4px (0.25rem) for buttons, input fields, and small cards.
- **Containers:** 8px (0.5rem) for main dashboard panels.
- **Exceptions:** Chips and status indicators utilize a full **Pill-shape** (100px) to distinguish them as interactive or informative metadata tags.

## Components
- **Cards:** Must maintain an `aspect-square` ratio for the dashboard. 1px border (#E4E6ED), white background. Content inside should be vertically centered or top-aligned with 24px padding.
- **Stat Chips:** Pill-shaped, using low-opacity versions of the class palette colors for backgrounds, with high-contrast text for accessibility.
- **Buttons:** 
  - *Primary:* Solid #5B47E0, white text, 4px radius. 
  - *Secondary:* 1px border #5B47E0, text #5B47E0.
- **Input Fields:** 1px border #E4E6ED, background #FFFFFF. On focus, border changes to #5B47E0 with a 2px outer glow of the same color at 10% opacity.
- **AI Panel:** Floating or docked panel with glassmorphism effect. Internal text should use `body-md` for maximum information density.
- **Lists:** Clean rows with 1px bottom border separator. Hover state should change background to a very subtle gray (#F9FAFB).
- **Sidebar Items:** Background #1A1D23. Active state uses a 4px vertical "pill" indicator on the left edge in Primary Accent color.