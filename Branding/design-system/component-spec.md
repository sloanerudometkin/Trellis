# Trellis Component Specification

## Global hierarchy

Every screen answers, in order: **What happened? Why does it matter? What should I do next?** Use one visually dominant action per section.

## Navigation

- Marketing header: horizontal logo, Product, How it works, Who it is for, and one primary action.
- Product navigation: Overview, AEO, SEO/Content, SEM, Reports, Organizer.
- Show the current location with text, weight, and shape—not color alone.
- Collapse to a labeled menu button on small screens. Preserve the same information order.

## Buttons

- Primary: Moss Deep background, Paper text, Public Sans 600, minimum height 44px.
- Secondary: transparent background, Moss Deep border and text.
- Tertiary: underlined text link for low-emphasis actions.
- Use specific verbs: “Analyze my site,” “Add to plan,” or “View recommendations.” Avoid “Submit” and “Click here.”
- Required states: default, hover, pressed, keyboard focus, loading, disabled, success, and error.
- A disabled button must be accompanied by an explanation when the reason is not obvious.

## Forms

- Keep labels visible above fields.
- Put format guidance before input and recovery guidance after an error.
- Preserve user-entered information after validation failures.
- URL example: “https://example.org,” never a placeholder pretending to be a label.
- Use one-column forms by default. Place fields side by side only when their relationship is obvious.

## Cards

- Use cards for meaningful groups, not every metric.
- Recommendation order: title, one-sentence reason, priority and status labels, next action, optional methodology.
- Health Score order: current score, since-last-scan delta, what changed, next recommendation.
- SEM summary remains separate from the organic Health Score.

## Status and progress

- Official workflow: Suggested → In Plan → In Production → Published.
- Always pair color with a text label and, where useful, an icon.
- Gold is reserved for a meaningful delta, new flag, or limited highlight and appears no more than once per screen whenever practical.
- Progress animation is brief and informative; respect reduced-motion preferences.

## Alerts and feedback

- Success confirms what changed and what happens next.
- Warning identifies a decision the user must make.
- Error describes the problem without blame and provides a recovery step.
- Informational notices do not compete visually with the screen’s main action.

## Empty and loading states

- Empty states explain why the area will become useful and offer one next action.
- Use a progress indicator and plain-language status for waits longer than one second.
- For analysis, show the current stage without inventing an exact completion percentage.

## Tables and reports

- Keep row labels visible and align numeric values consistently.
- IBM Plex Mono is for the values; Public Sans is for explanations and controls.
- On narrow screens, convert tables into labeled records rather than forcing horizontal reading.
- Report comparisons state the selected dates and clearly distinguish calculated Trellis metrics from connected third-party data.
