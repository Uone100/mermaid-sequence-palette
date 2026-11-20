# Highlight one handoff in a Mermaid sequence diagram

Suppose you want a reviewer to spot one approval message in an exported diagram. You will give the Editor box a pale blue background and the “Accept changes” arrow a green line and arrowhead.

## Try the bundled diagram

Download the named ZIP under **Assets** on the [release page](https://github.com/Uone100/mermaid-sequence-palette/releases/latest). Extract it, open a terminal in the folder containing `SKILL.md`, and use Python 3.9 or newer. The example needs no additional packages.

```sh
python scripts/palette.py examples/sample.svg
python scripts/palette.py examples/sample.svg examples/colors.json styled.svg
```

The first command lists the actor names and message captions available in the SVG. The second reports one box and one message. Open `styled.svg` in your browser and look for the green approval arrow. The original SVG is still available for comparison.

## Use your own diagram

1. Export a Mermaid **sequence diagram** as SVG and run the first command with its filename.
2. Copy `examples/colors.json`. Replace `Editor` and `Accept changes` with exact names from the inventory. Use hex colors. If a caption occurs twice, add `"occurrence": 2` to the message rule to target the second one.
3. Run the second command with your SVG, rules file and a fresh output filename. An existing destination is protected. If no captions appear, inspect the SVG export structure or try a fresh export in Mermaid.

## Ask an agent

For project installation, follow the [README](README.md). Try “List messages in my sequence SVG, then highlight only the second approval arrow in green. Save a separate SVG.” Give the agent the exported file and the caption to match.
