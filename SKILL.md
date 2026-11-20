---
name: mermaid-sequence-palette
description: Recolor selected participant boxes and message arrows in an existing Mermaid sequence SVG using stable participant names and exact message labels, with a dry inventory and checks for ambiguous matches.
---
Use for exported Mermaid sequence diagrams. Obtain the source SVG, or render the user's .mmd with their existing Mermaid renderer. Keep the original source and SVG.

1. Run `python scripts/palette.py diagram.svg` to inspect the box names and eligible message labels. Use the labels in the inventory; repeated captions also need a 1-based occurrence.
2. Create a rules JSON following examples/colors.json. Each actor rule selects its top and bottom rectangle; each message rule colors the label, line and private copies of the referenced arrowhead markers. Choose colors with enough contrast against the existing background.
3. Run `python scripts/palette.py diagram.svg colors.json styled.svg`. Use a fresh output name. Compare the returned match counts with the request, then open the SVG in the destination viewer. If it embeds a raster copy or ignores SVG styles, export the styled SVG there as a separate step.
4. Report ambiguous or unsupported renderer layouts. Semantic matches use rendered names, not Mermaid source line numbers. A style is applied to this export; rerun after diagrams are regenerated.
