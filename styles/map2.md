# Figma to React Style Mapping

This table provides a systematic mapping between Figma object types, their style attributes, and the equivalent React inline style properties using camelCase syntax. Use this as a reference when converting Figma designs to React components.

## TEXT

| Figma Type | Figma Style Attribute | React Style Equivalent |
|------------|------------------------|------------------------|
| TEXT | `fontFamily` | `fontFamily: '{value}, sans-serif'` |
| TEXT | `fontPostScriptName` | React doesn't have a direct equivalent; use `fontFamily` instead |
| TEXT | `fontSize` | `fontSize: '{value}px'` |
| TEXT | `fontWeight` | `fontWeight: {value}` (100-900) |
| TEXT | `letterSpacing` | `letterSpacing: '{value}px'` |
| TEXT | `lineHeightPercent` | `lineHeight: '{value}%'` |
| TEXT | `lineHeightPx` | `lineHeight: '{value}px'` |
| TEXT | `textAlignHorizontal: LEFT` | `textAlign: 'left'` |
| TEXT | `textAlignHorizontal: CENTER` | `textAlign: 'center'` |
| TEXT | `textAlignHorizontal: RIGHT` | `textAlign: 'right'` |
| TEXT | `textAlignHorizontal: JUSTIFIED` | `textAlign: 'justify'` |
| TEXT | `textAlignVertical: TOP` | `verticalAlign: 'top'` |
| TEXT | `textAlignVertical: CENTER` | `verticalAlign: 'middle'` |
| TEXT | `textAlignVertical: BOTTOM` | `verticalAlign: 'bottom'` |
| TEXT | `textAutoResize: HEIGHT` | `height: 'auto', width: '{value}px'` |
| TEXT | `textAutoResize: WIDTH_AND_HEIGHT` | `height: 'auto', width: 'auto'` |
| TEXT | `textAutoResize: NONE` | `height: '{value}px', width: '{value}px'` |
| TEXT | `fills > color` | `color: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |
| TEXT | `characters` | Content as children: `<element>{characters}</element>` |
| TEXT | `layoutAlign: STRETCH` | `alignSelf: 'stretch'` |
| TEXT | `layoutGrow: 0.0` | `flexGrow: 0` |
| TEXT | `layoutGrow: 1.0` | `flexGrow: 1` |
| TEXT | `layoutSizingHorizontal: FILL` | `width: '100%'` |
| TEXT | `layoutSizingHorizontal: HUG` | `width: 'fit-content'` |
| TEXT | `layoutSizingHorizontal: FIXED` | `width: '{value}px'` |
| TEXT | `layoutSizingVertical: FILL` | `height: '100%'` |
| TEXT | `layoutSizingVertical: HUG` | `height: 'fit-content'` |
| TEXT | `layoutSizingVertical: FIXED` | `height: '{value}px'` |

## FRAME

| Figma Type | Figma Style Attribute | React Style Equivalent |
|------------|------------------------|------------------------|
| FRAME | `layoutMode: HORIZONTAL` | `display: 'flex', flexDirection: 'row'` |
| FRAME | `layoutMode: VERTICAL` | `display: 'flex', flexDirection: 'column'` |
| FRAME | `layoutWrap: NO_WRAP` | `flexWrap: 'nowrap'` |
| FRAME | `layoutWrap: WRAP` | `flexWrap: 'wrap'` |
| FRAME | `layoutSizingHorizontal: FIXED` | `width: '{value}px'` |
| FRAME | `layoutSizingHorizontal: HUG` | `width: 'fit-content'` |
| FRAME | `layoutSizingHorizontal: FILL` | `width: '100%'` |
| FRAME | `layoutSizingVertical: FIXED` | `height: '{value}px'` |
| FRAME | `layoutSizingVertical: HUG` | `height: 'fit-content'` |
| FRAME | `layoutSizingVertical: FILL` | `height: '100%'` |
| FRAME | `layoutAlign: INHERIT` | Inherits parent alignment |
| FRAME | `layoutAlign: STRETCH` | `alignSelf: 'stretch'` |
| FRAME | `counterAxisSizingMode: FIXED` | Does not grow in the counter axis |
| FRAME | `counterAxisSizingMode: AUTO` | Sizes based on content |
| FRAME | `primaryAxisSizingMode: FIXED` | Does not grow in the primary axis |
| FRAME | `primaryAxisSizingMode: AUTO` | Sizes based on content |
| FRAME | `counterAxisAlignItems: CENTER` | `alignItems: 'center'` |
| FRAME | `counterAxisAlignItems: START` | `alignItems: 'flex-start'` |
| FRAME | `counterAxisAlignItems: END` | `alignItems: 'flex-end'` |
| FRAME | `primaryAxisAlignItems: CENTER` | `justifyContent: 'center'` |
| FRAME | `primaryAxisAlignItems: START` | `justifyContent: 'flex-start'` |
| FRAME | `primaryAxisAlignItems: END` | `justifyContent: 'flex-end'` |
| FRAME | `primaryAxisAlignItems: SPACE_BETWEEN` | `justifyContent: 'space-between'` |
| FRAME | `itemSpacing` | `gap: '{value}px'` |
| FRAME | `cornerRadius` | `borderRadius: '{value}px'` |
| FRAME | `cornerSmoothing` | React doesn't have a direct equivalent |
| FRAME | `strokeWeight` | `borderWidth: '{value}px'` |
| FRAME | `strokeAlign: INSIDE` | `boxSizing: 'border-box'` |
| FRAME | `strokeAlign: OUTSIDE` | `boxSizing: 'content-box'` |
| FRAME | `strokeAlign: CENTER` | For outline effect use outline property |
| FRAME | `strokes > color` | `borderColor: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |
| FRAME | `clipsContent: true` | `overflow: 'hidden'` |
| FRAME | `clipsContent: false` | `overflow: 'visible'` |
| FRAME | `backgroundColor` | `backgroundColor: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |
| FRAME | `fills > color` | `backgroundColor: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |
| FRAME | `background > color` | `backgroundColor: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |

## RECTANGLE

| Figma Type | Figma Style Attribute | React Style Equivalent |
|------------|------------------------|------------------------|
| RECTANGLE | `cornerRadius` | `borderRadius: '{value}px'` |
| RECTANGLE | `strokeWeight` | `borderWidth: '{value}px'` |
| RECTANGLE | `strokeAlign: INSIDE` | `boxSizing: 'border-box'` |
| RECTANGLE | `strokeAlign: OUTSIDE` | `boxSizing: 'content-box'` |
| RECTANGLE | `strokes > color` | `borderColor: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |
| RECTANGLE | `backgroundColor` | `backgroundColor: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |
| RECTANGLE | `fills > color` | `backgroundColor: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |
| RECTANGLE | `width` | `width: '{value}px'` |
| RECTANGLE | `height` | `height: '{value}px'` |

## VECTOR

| Figma Type | Figma Style Attribute | React Style Equivalent for SVG |
|------------|------------------------|---------------------------------|
| VECTOR | `strokeWeight` | `strokeWidth: '{value}px'` (SVG attribute) |
| VECTOR | `strokeAlign: CENTER` | SVG stroke alignment |
| VECTOR | `strokes > color` | `stroke: 'rgba({r*255}, {g*255}, {b*255}, {a})'` (SVG attribute) |
| VECTOR | `fills > color` | `fill: 'rgba({r*255}, {g*255}, {b*255}, {a})'` (SVG attribute) |
| VECTOR | `constraints horizontal: SCALE` | Responsive SVG - use viewBox and preserveAspectRatio |
| VECTOR | `constraints vertical: SCALE` | Responsive SVG - use viewBox and preserveAspectRatio |

## INSTANCE 

| Figma Type | Figma Style Attribute | React Style Equivalent |
|------------|------------------------|------------------------|
| INSTANCE | `componentId` | Reference to component definition (React component) |
| INSTANCE | `fills > color` | `backgroundColor: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |
| INSTANCE | `background > color` | `backgroundColor: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |
| INSTANCE | `width` | `width: '{value}px'` |
| INSTANCE | `height` | `height: '{value}px'` |

## ELLIPSE

| Figma Type | Figma Style Attribute | React Style Equivalent |
|------------|------------------------|------------------------|
| ELLIPSE | `strokeWeight` | `borderWidth: '{value}px'` |
| ELLIPSE | `strokes > color` | `borderColor: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |
| ELLIPSE | `fills > color` | `backgroundColor: 'rgba({r*255}, {g*255}, {b*255}, {a})'` |
| ELLIPSE | Equal width and height | `borderRadius: '50%'` for circle |
| ELLIPSE | Different width and height | `borderRadius: '50%'` with specific width/height for oval |

## Common Layout Properties

| Figma Layout Property | React Style Equivalent |
|------------------------|------------------------|
| `absoluteBoundingBox x, y` | `position: 'absolute', left: '{x}px', top: '{y}px'` |
| `absoluteBoundingBox width` | `width: '{width}px'` |
| `absoluteBoundingBox height` | `height: '{height}px'` |
| `constraints horizontal: LEFT` | `left: '{value}px'` |
| `constraints horizontal: RIGHT` | `right: '{value}px'` |
| `constraints horizontal: CENTER` | `left: '50%', transform: 'translateX(-50%)'` |
| `constraints horizontal: SCALE` | `left: '{value}%', width: '{value}%'` |
| `constraints vertical: TOP` | `top: '{value}px'` |
| `constraints vertical: BOTTOM` | `bottom: '{value}px'` |
| `constraints vertical: CENTER` | `top: '50%', transform: 'translateY(-50%)'` |
| `constraints vertical: SCALE` | `top: '{value}%', height: '{value}%'` |

## Effects Properties

| Figma Effect | React Style Equivalent |
|--------------|------------------------|
| `effects: DROP_SHADOW` | `boxShadow: '{offsetX}px {offsetY}px {radius}px {spread}px rgba({r}, {g}, {b}, {a})'` |
| `effects radius` | Used in boxShadow as blur radius |
| `effects visible: True` | Effect is applied |
| `effects visible: False` | Effect is not applied |
| `effects type: DROP_SHADOW` | `boxShadow` property |
| `effects type: INNER_SHADOW` | `boxShadow: 'inset {offsetX}px {offsetY}px {radius}px {spread}px rgba({r}, {g}, {b}, {a})'` |
| `effects type: LAYER_BLUR` | `filter: 'blur({radius}px)'` |
| `effects type: BACKGROUND_BLUR` | `backdropFilter: 'blur({radius}px)'` |

## Implementation Notes

1. Applying React Inline Styles:
```jsx
const textStyle = {
  fontFamily: "'Inter', sans-serif",
  fontSize: '24px',
  fontWeight: 500,
  color: 'rgba(0, 0, 0, 1)'
};

return <div style={textStyle}>Hello World</div>;
```
