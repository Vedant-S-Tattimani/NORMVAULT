# Hyperframes Composition Brief: NORMVAULT

## Objective
Create a short, prestigious launch-style brag video for NORMVAULT, demonstrating how it turns ambiguous public procurement tender specifications into audit-proof Indian Standards compliance packages.

## Output
- Composition directory: `brag-output/composition/`
- Rendered video: `brag-output/brag.mp4`
- Format: landscape — 1920x1080 (30fps)
- Duration: 21.00 seconds

## Source Material
- Project root: `c:\Users\Lenovo\Desktop\NORMVAULT`
- Primary files read: `apps/frontend/src/index.css`, `apps/frontend/tailwind.config.js`, `apps/frontend/src/pages/HomePage.tsx`, `apps/frontend/src/components/home/HeroSection.tsx`, `README.md`
- Product name: NORMVAULT
- Tagline / strongest claim: "From Specifications to the Right Standards." / "A single outdated standard can halt a ₹500 Cr public tender."
- Key UI or visual moment to recreate: The deterministic clause reconciliation card with parameter verification for **IS 1786:2008** and the GFR 144(i) audit-ready stamp.
- Copy that must appear verbatim:
  - "From Specifications to the Right Standards."
  - "IS 1786 : 2008 — High Strength Deformed Steel Bars"
  - "MANDATORY DPIIT QCO ORDER ACTIVE"
  - "AUDIT-READY FOR CAG & CVC SCRUTINY"
  - "STANDARDS FOR A STRONGER INDIA"

## Creative Direction
- Tone preset: `polished`
- Creative direction: "Prestigious institutional engineering & national standards intelligence"
- Interpretation: Restrained, authoritative pacing; crisp architectural drafting aesthetics; zero cartoonish SaaS fluff; clear contrast and readability.
- Angle: Replacing tender uncertainty and outdated citations with deterministic BIS and QCO compliance.
- Hook: "A single outdated standard can halt a ₹500 Cr public tender."
- Outro / punchline: "From Specifications to the Right Standards. Audit-ready. Uncompromised."

## Visual Identity
- Background: `#F6F2EA` (warm architectural parchment)
- Card Surfaces: `#FCFAF6` with fine `#D9D0C1` drafting borders
- Primary Text: `#1E2320` (obsidian ink)
- Secondary Text: `#525650`
- Mineral Accent: `#2C6E80` (mineral blue)
- Sage Green (Compliant): `#2D5A43` / `#EBF2EE` badge
- Display font: Playfair Display / Cormorant Garamond
- Body font: Inter
- Monospace font: JetBrains Mono

## Storyboard
Total duration: 21.00 seconds
1. **Scene 1 (0.00s - 3.55s)**: Hook — High-stakes national procurement problem statement.
2. **Scene 2 (3.55s - 7.35s)**: Tender Specification Doc with live ambiguous clause parameters.
3. **Scene 3 (7.35s - 13.11s)**: NORMVAULT Deterministic Engine — Resolution to IS 1786:2008 with 3 beat-synced parameter verifications.
4. **Scene 4 (13.11s - 17.47s)**: Audit-Ready Decision Package view with CAG/CVC stamps and GeM Export.
5. **Scene 5 (17.47s - 21.00s)**: Outro with NORMVAULT branding and "STANDARDS FOR A STRONGER INDIA".

## Audio
- Audio role: Warm corporate bed with refined rhythm and clear accents.
- Music: `assets/music/happy-beats-business-moves-vol-10-by-ende-dot-app.mp3`
- Music treatment: Starts at 0.00s at volume 0.70; dips slightly during technical highlights; fades out smoothly from 20.00s to 21.00s.
- Audio-coupled moments:
  - 8.73s: Parameter check 1 (Mechanical Yield Stress) — `click1.ogg`
  - 9.83s: Parameter check 2 (Chemical Carbon/Phosphorus) — `click1.ogg`
  - 10.93s: Parameter check 3 (Elongation ≥ 16%) — `click1.ogg`
  - 13.11s: Decision Package Stamp — `drop_001.ogg`
- Music cue guidance:
  - Key transitions snap to cues at 3.55s, 7.35s, 13.11s, 17.47s.
  - Verification items sync to beat grid at 8.73s, 9.83s, 10.93s.

## Hyperframes Instructions
- Build the composition in `brag-output/composition/` using standard Hyperframes markup (`index.html`, `styles.css`, `composition.json` / `hyperframes.json`).
- Ensure all fonts are imported via Google Fonts (`Playfair Display`, `Inter`, `JetBrains Mono`).
- Ensure WCAG contrast passes with flying colors (use `#1E2320` text on `#F6F2EA` and `#FCFAF6`).
- Include the audio elements (`<audio>` tags) with precise start times and volumes.
- Verify with `npx hyperframes check` before rendering.
