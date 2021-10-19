;----------------
; This file is part of CktSync design manager
;----------------

;----------------
; Procedure to checkin a cellview
;----------------
procedure(csynLMCBCheckIn(menuName libName cellName viewName fileName catName)
    let((commentField ciForm)
        ; Comment for checkin
        commentField = hiCreateMLTextField(
            ?name 'commentField
            ?prompt "Checkin comment"
            ?value "Checkin comment"
            ?editable t
        )
        ; Checkin form
        ciForm = hiCreateAppForm(
            ?name 'ciForm
            ?fields list(commentField)
            ?formTitle "Check in"
            ?buttonLayout 'OKCancel
            ?callback "csynExecCheckIn(
                libName cellName viewName fileName catName ciForm
            )"
        )
        ; Display form
        hiDisplayForm(ciForm)
    )
)

;----------------
; Procedure to send checkin command to cdsclient
;----------------
procedure(csynExecCheckIn(libName cellName viewName fileName catName ciForm)
    let((argslist clicmd
            cliresp ciComment respcode
        )
        ciComment = hiEscapeStringChars(ciForm->commentField->value)
        libPath = ddGetObj(libName)~>readPath
        arglist = list(
            "cellci"
            libPath
            cellName
            viewName
            ciComment
        )
        ; Build command and send to client
        clicmd = csynCSVList2String(arglist)
        csynSendCommand(clicmd)
        ; Get response for command
        cliresp = csynGetResponse()
        cliresp = csynCSVString2List(cliresp)
        respcode = nth(0 cliresp)
        ; Check for error
        if(strcmp(respcode, "0") != 0 then
            csynShowMessage(nth(1 cliresp))
        )
        println("Checkin Done")
    )
)
