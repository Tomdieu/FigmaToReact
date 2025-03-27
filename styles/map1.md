# Figma to React Style Mapping Table

This comprehensive table maps Figma style attributes to their corresponding React/HTML style attributes, helping you properly translate Figma designs to React code in your MDA transformation process.

## 1. Font and Text Styles

| Element Type | Figma Style Attribute | React/HTML Style Attribute | Example Value | Notes |
|--------------|------------------------|----------------------------|---------------|-------|
| TEXT | fontFamily | fontFamily | "Inter" | Use the same font family name |
| TEXT | fontSize | fontSize | "24.0px" | Add 'px' unit |
| TEXT | fontWeight | fontWeight | 400 | Use the same numeric weight |
| TEXT | letterSpacing | letterSpacing | "0.0px" | Add 'px' unit |
| TEXT | lineHeightPx | lineHeight | "29.045454px" | Add 'px' unit |
| TEXT | textAlignHorizontal: LEFT | textAlign | "left" | Convert to lowercase |
| TEXT | textAlignHorizontal: CENTER | textAlign | "center" | Convert to lowercase |
| TEXT | textAlignHorizontal: RIGHT | textAlign | "right" | Convert to lowercase |
| TEXT | textAlignVertical: TOP | alignItems | "flex-start" | Map to flex alignment |
| TEXT | textAlignVertical: CENTER | alignItems | "center" | Map to flex alignment |
| TEXT | textAlignVertical: BOTTOM | alignItems | "flex-end" | Map to flex alignment |

## 2. Layout Styles

| Element Type | Figma Style Attribute | React/HTML Style Attribute | Example Value | Notes |
|--------------|------------------------|----------------------------|---------------|-------|
| FRAME | layoutMode: HORIZONTAL | display, flexDirection | "flex", "row" | Set both properties |
| FRAME | layoutMode: VERTICAL | display, flexDirection | "flex", "column" | Set both properties |
| FRAME | layoutWrap: NO_WRAP | flexWrap | "nowrap" | Default in React |
| FRAME | layoutWrap: WRAP | flexWrap | "wrap" | For wrapping content |
| FRAME | itemSpacing | gap | "10px" | Add 'px' unit |
| FRAME | primaryAxisAlignItems: MIN | justifyContent | "flex-start" | For main axis alignment |
| FRAME | primaryAxisAlignItems: CENTER | justifyContent | "center" | For main axis alignment |
| FRAME | primaryAxisAlignItems: MAX | justifyContent | "flex-end" | For main axis alignment |
| FRAME | primaryAxisAlignItems: SPACE_BETWEEN | justifyContent | "space-between" | For main axis alignment |
| FRAME | counterAxisAlignItems: MIN | alignItems | "flex-start" | For cross axis alignment |
| FRAME | counterAxisAlignItems: CENTER | alignItems | "center" | For cross axis alignment |
| FRAME | counterAxisAlignItems: MAX | alignItems | "flex-end" | For cross axis alignment |

## 3. Dimension and Position Styles

| Element Type | Figma Style Attribute | React/HTML Style Attribute | Example Value | Notes |
|--------------|------------------------|----------------------------|---------------|-------|
| All | x | left | "294.0px" | Add 'px' unit |
| All | y | top | "183.0px" | Add 'px' unit |
| All | width | width | "852.0px" | Add 'px' unit or use percentage |
| All | height | height | "659.0px" | Add 'px' unit or use percentage |
| FRAME | layoutSizingHorizontal: FIXED | width | "367.0px" | Fixed width |
| FRAME | layoutSizingHorizontal: FILL | width | "100%" | Fill container width |
| FRAME | layoutSizingHorizontal: HUG | width | "fit-content" | Size to content |
| FRAME | layoutSizingVertical: FIXED | height | "60.0px" | Fixed height |
| FRAME | layoutSizingVertical: FILL | height | "100%" | Fill container height |
| FRAME | layoutSizingVertical: HUG | height | "fit-content" | Size to content |

## 4. Border and Background Styles

| Element Type | Figma Style Attribute | React/HTML Style Attribute | Example Value | Notes |
|--------------|------------------------|----------------------------|---------------|-------|
| All | backgroundColor | backgroundColor | "rgba(0, 0, 0, 0.0)" | Convert Figma color to CSS rgb/rgba |
| All | color (fills) | color | "rgb(0, 0, 0)" | Convert Figma color to CSS rgb/rgba |
| All | borderColor (strokes) | borderColor | "rgb(194, 187, 187)" | Convert Figma color to CSS rgb/rgba |
| FRAME | cornerRadius | borderRadius | "8.0px" | Add 'px' unit |
| FRAME | strokeWeight | borderWidth | "1.0px" | Add 'px' unit |
| FRAME | strokeAlign: INSIDE | boxSizing | "border-box" | Default in React |
| FRAME | strokeAlign: OUTSIDE | boxSizing | "content-box" | Rarely used |
| FRAME | strokeAlign: CENTER | boxSizing | "border-box" | Simplified in React |

## 5. Other Styles

| Element Type | Figma Style Attribute | React/HTML Style Attribute | Example Value | Notes |
|--------------|------------------------|----------------------------|---------------|-------|
| FRAME | clipsContent: true | overflow | "hidden" | Hide content outside container |
| FRAME | clipsContent: false | overflow | "visible" | Show content outside container |
| FRAME | layoutGrow | flexGrow | 1 | For flexible sizing |
| FRAME | layoutAlign: STRETCH | alignSelf | "stretch" | For cross-axis stretching |
| FRAME | layoutAlign: INHERIT | alignSelf | "auto" | Default behavior |

## 6. Complete Style Object Examples

### Text Element (Label)

```javascript
// Figma TEXT element (label)
const labelStyle = {
  fontFamily: "Inter",
  fontSize: "24.0px",
  fontWeight: 400,
  letterSpacing: "0.0px",
  lineHeight: "29.045454px",
  textAlign: "left",
  display: "flex",
  alignItems: "center",
  color: "rgb(0, 0, 0)",
  width: "100%",
  height: "auto",
  whiteSpace: "pre-wrap",
  wordBreak: "break-word"
};
```

### Input Container

```javascript
// Figma FRAME element (input container)
const inputContainerStyle = {
  left: "536.5px",
  top: "398.0px",
  width: "367.0px",
  height: "60.0px",
  backgroundColor: "rgba(0, 0, 0, 0.0)",
  borderRadius: "8.0px",
  borderWidth: "1.0px",
  borderColor: "rgb(194, 187, 187)",
  borderStyle: "solid",
  boxSizing: "border-box",
  display: "flex",
  flexDirection: "row",
  gap: "4px",
  justifyContent: "center",
  alignItems: "center",
  width: "100%",
  height: "100%"
};
```

### Button Element

```javascript
// Figma FRAME element (button)
const buttonStyle = {
  left: "536.5px",
  top: "666.0px",
  width: "367.0px",
  height: "49.0px",
  backgroundColor: "rgb(72, 101, 250)",
  borderRadius: "4.0px",
  borderWidth: "1.0px",
  borderColor: "rgb(255, 255, 255)",
  borderStyle: "solid",
  boxSizing: "border-box",
  display: "flex",
  flexDirection: "row",
  gap: "10px",
  justifyContent: "center",
  alignItems: "center",
  width: "100%",
  height: "fit-content"
};
```

## 7. Special Considerations

1. **Color Conversion**: Figma colors use 0-1 scale for RGB values, while CSS uses 0-255. Multiply Figma values by 255 for CSS.

2. **Layout Modes**: Figma's layout modes (HORIZONTAL/VERTICAL) map to flexbox in React with appropriate direction.

3. **Text Alignment**: Figma's text alignment properties need to be mapped to appropriate CSS properties:
   - textAlignHorizontal → textAlign
   - textAlignVertical → alignItems (when in a flex container)

4. **Size Units**: Add 'px' to numeric values from Figma for dimensions, spacing, and font sizes.

5. **Auto Layout**: Figma's auto layout maps to flexbox in React, with appropriate properties for direction, alignment, and spacing.

6. **Nested Styles**: Complex Figma elements may have nested styles that need to be applied to nested React components.

7. **Responsive Considerations**: Consider using relative units (%, em, rem) instead of fixed pixel values for responsive designs.
