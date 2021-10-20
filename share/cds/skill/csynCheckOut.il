;----------------
; This file is part of CktSync design manager
;----------------

;----------------
; Procedure to checkout a cellview
;----------------
procedure(csynLMCBCheckOut(menuName libName cellName viewName fileName catName)
    let((commentField coForm)
        ; Comment for checkin
        commentField = hiCreateLabel(
            ?name 'commentField
            ?labelText "Do you want to checkout the cell?"
            ?justification 'center
        )
        ; Checkin form
        coForm = hiCreateAppForm(
            ?name 'coForm
            ?fields list(commentField)
            ?formTitle "Check out"
            ?buttonLayout 'OKCancel
            ?callback "csynExecCheckOut(
                libName cellName viewName
    fileName catName)"
        )
        ; Display form
        hiDisplayForm(coForm)
    )
)

;----------------
; Procedure to send checkin command to cdsclient
;----------------
procedure(csynExecCheckOut(libName cellName viewName fileName catName)
    let((argslist clicmd
            cliresp respcode
        )
        libPath = ddGetObj(libName)~>readPath
        arglist = list(
            "cellco"
            libPath
            cellName
            viewName
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
        else
            println("Checkout Done")
        )
    )
)
