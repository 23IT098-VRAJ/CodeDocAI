# AI_slop.md — Anti-Slop Reference

## Banned by default (do not use unless the design direction explicitly calls for it)
- Purple-to-blue gradient buttons/backgrounds (the Tailwind indigo-500 default)
- Inter, Roboto, Arial, or Space Grotesk as the primary typeface
- Glassmorphism / frosted-glass cards as a default choice
- Three feature cards in a row under a centered hero — the single most 
  overused SaaS-landing pattern
- Rounded cards with a colored left-accent border
- Gradient "orbs" used to represent AI/technology
- CSS-silhouette shapes standing in for real product screenshots
- Emoji used as bullet points or section markers
- Fake dashboard mockup screenshots with placeholder charts
- Generic drop shadows applied uniformly to every surface

## Required before any code is written
1. Commit to ONE named aesthetic direction (e.g. brutalist, editorial, 
   Nordic-minimal, retro-futuristic, maximalist) — "clean and modern" is 
   not a direction, it's the slop default.
2. Lock design tokens in writing before building anything:
   - Palette: exact hex values, not "blue-ish"
   - Type pairing: two fonts max, with explicit weights
   - Spacing scale: a defined step system, not ad hoc
   - Border/shadow philosophy: pick one, apply consistently
3. Check contrast against APCA (not just WCAG's older algorithm) before 
   calling any screen done.

## Self-check before delivering any UI
- Would this be visually distinguishable from a random AI-generated demo 
  if the branding were removed? If no, revise.
- Does it use anything from the banned list above? If yes, remove it.
- Are the design tokens from step 2 actually being followed, or has the 
  build drifted back toward the safe average?