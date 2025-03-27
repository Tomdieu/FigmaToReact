lazy rule CreateNestedTextElement {
    from
        F : Figma!TEXT
    to
        -- For text elements, we need the text content directly
        R : React!HTMLElement (
            name <- F.getTextTag(),  -- Use the appropriate HTML tag based on the text style
            key <- F.id + '_text',
            isSelfClosing <- false,
            content <- if not F.characters.oclIsUndefined() then F.characters else '' endif,
            attributes <- Sequence {
                thisModule.CreateAttribute('style', 
                    '{' +
                    (if not F.style.oclIsUndefined() then
                        'fontFamily: "' + F.style.fontFamily + '", ' +
                        'fontSize: "' + F.style.fontSize + 'px", ' +
                        'fontWeight: ' + F.style.fontWeight + ', '
                    else
                        ''
                    endif) +
                    'textDecoration: "none", ' +
                    'color: "inherit"' +
                    '}'
                )
            }
        )
}
