;----------------
; This file is part of CktSync design manager
;----------------

;----------------
; Show message box.
;----------------
procedure(csynShowMessage(msg)
    let((msgField msgForm)
        ; message
        msgField = hiCreateLabel(
            ?name 'commentField
            ?labelText msg
            ?justification 'center
        )
        ; Checkin form
        msgForm = hiCreateAppForm(
            ?name 'msgForm
            ?fields list(msgField)
            ?formTitle "Message"
            ?buttonLayout 'Close
        )
        ; Display form
        hiDisplayForm(msgForm)
    )
)
