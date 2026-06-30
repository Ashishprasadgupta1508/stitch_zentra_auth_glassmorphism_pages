---
name: Academic Ethereal
colors:
  surface: '#13121b'
  surface-dim: '#13121b'
  surface-bright: '#393842'
  surface-container-lowest: '#0e0d16'
  surface-container-low: '#1b1b24'
  surface-container: '#1f1f28'
  surface-container-high: '#2a2933'
  surface-container-highest: '#35343e'
  on-surface: '#e4e1ee'
  on-surface-variant: '#c7c4d8'
  inverse-surface: '#e4e1ee'
  inverse-on-surface: '#302f39'
  outline: '#918fa1'
  outline-variant: '#464555'
  surface-tint: '#c3c0ff'
  primary: '#c3c0ff'
  on-primary: '#1d00a5'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#4d44e3'
  secondary: '#c3c0ff'
  on-secondary: '#2a276a'
  secondary-container: '#413f82'
  on-secondary-container: '#b0aef9'
  tertiary: '#ffb695'
  on-tertiary: '#571f00'
  tertiary-container: '#a44100'
  on-tertiary-container: '#ffd2be'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#e2dfff'
  secondary-fixed-dim: '#c3c0ff'
  on-secondary-fixed: '#140f54'
  on-secondary-fixed-variant: '#413f82'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb695'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#7b2f00'
  background: '#13121b'
  on-background: '#e4e1ee'
  surface-variant: '#35343e'
typography:
  display-lg:
    fontFamily: DM Serif Display
    fontSize: 48px
    fontWeight: '400'
    lineHeight: '1.1'
  display-lg-mobile:
    fontFamily: DM Serif Display
    fontSize: 36px
    fontWeight: '400'
    lineHeight: '1.1'
  headline-md:
    fontFamily: DM Serif Display
    fontSize: 32px
    fontWeight: '400'
    lineHeight: '1.2'
  title-lg:
    fontFamily: plusJakartaSans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  body-main:
    fontFamily: plusJakartaSans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-caps:
    fontFamily: plusJakartaSans
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.08em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-padding: 24px
  gutter: 20px
  card-gap: 24px
---

## Brand & Style

This design system establishes a sanctuary for deep work and scholarly pursuit. It is built on a foundation of **Sophisticated Glassmorphism**, blending the moody, focused atmosphere of a night-time library with the high-end precision of a luxury travel application. 

The aesthetic is "Atmospheric-Academic." It utilizes deep, dark layers to minimize eye strain during long study sessions, while using translucent surfaces to maintain a sense of lightness and digital depth. The interaction model is intentional and quiet, favoring smooth transitions and subtle glows over aggressive animations. The goal is to make the student feel empowered, calm, and intellectually focused.

## Colors

The palette is centered on a high-contrast relationship between deep space-navies and vibrant Indigo. 

- **The Void (Background):** A rich, atmospheric navy layered over photographic textures. The overlay acts as a "focus veil," pushing the background imagery into the distance.
- **The Lens (Surfaces):** Dark tinted glass with a heavy 20px Gaussian blur. This creates a tactile sense of depth, suggesting that the UI elements are suspended in a physical, light-filled space.
- **The Spark (Primary):** Indigo is used sparingly for critical actions and focus states, often accompanied by a soft, diffused glow to simulate bioluminescence or light reflecting off glass.

## Typography

This system employs a "Traditional meets Modern" typographic pairing. 

- **DM Serif Display** provides the academic soul. It is used for large headlines and display moments, evoking the feeling of a prestige publication or a classic leather-bound book.
- **Plus Jakarta Sans** provides the modern utility. Its open apertures and clean geometric forms ensure high legibility for long-form study notes and complex UI controls.

**Hierarchy Rules:**
- Use Serif for "Human" moments: greetings, section titles, and narrative text.
- Use Sans for "Tool" moments: data, input labels, buttons, and system feedback.
- Maintain generous line heights to ensure a relaxed reading pace.

## Layout & Spacing

The layout philosophy is **Generous and Focused**. It avoids information density in favor of clarity.

- **Grid:** A 12-column fluid grid for desktop with 24px margins. Content is often centered in a "Focus Column" (800px max width) to prevent eye-scanning fatigue.
- **Rhythm:** An 8px linear scale is used. However, component internal padding should favor larger increments (24px, 32px) to reinforce the premium, "roomy" feel of high-end travel apps.
- **Mobile:** Elements reflow into a single column with 16px side margins. Cards remain full width to maximize the glass surface area.

## Elevation & Depth

Depth is not communicated through traditional drop shadows, but through **Optical Refraction** and **Luminance**.

- **Z-Index 0:** The atmospheric background image with navy overlay.
- **Z-Index 1 (Base Cards):** Glass surfaces with 20px backdrop-blur and a 1px solid border (rgba(255, 255, 255, 0.1)).
- **Z-Index 2 (Floating/Modals):** Increased blur (40px) and a subtle inner-glow on the top edge to simulate a catch-light.
- **Focus State:** When an element is active, it emits a soft, 15px-25px diffused Indigo glow (`#4F46E5`) instead of a harsh stroke, making the element appear "energized."

## Shapes

The shape language is defined by **Large Radii (24px)**. 

- **Primary Containers:** 24px (rounded-xl) for all cards and main surfaces. This softness contrasts with the sharp, elegant serifs of the display type.
- **Interactive Elements:** Buttons and inputs follow a 12px or 16px radius to maintain a distinct "tappable" feel while remaining part of the rounded family.
- **Icons:** Use medium-weight strokes with slightly rounded caps to match the UI's friendliness.

## Components

### Buttons
- **Primary:** Solid Indigo fill with white text. On hover, add a 20px Indigo outer glow.
- **Secondary:** Glass-fill with white border. Subtle scaling effect (0.98) on click to feel "tactile."

### Cards
- Always use the glassmorphic style: `rgba(15, 12, 35, 0.55)` background + 20px blur. 
- Border must be a 1px "Hairline" using `rgba(255, 255, 255, 0.1)`.
- Internal padding should be a minimum of 24px.

### Input Fields
- Inputs are dark, semi-transparent wells with a subtle bottom-border. 
- Custom leading icons are mandatory (use thin-line style). 
- Active state: The bottom border brightens to Indigo and a soft Indigo glow fills the background of the input.

### Chips/Badges
- Small, pill-shaped glass elements. Use `label-caps` typography. For "AI-generated" content, use a subtle Indigo gradient background.

### Lists
- Items are separated by subtle 1px dividers. On hover, the entire list item should take on a light white-tinted glass background (rgba(255,255,255, 0.05)).