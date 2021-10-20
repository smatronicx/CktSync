;----------------
; This file is part of CktSync design manager
;----------------

;----------------
; Procedure to cancel checkout of a cellview
;----------------
procedure(csynLMCBCancelCo(menuName libName cellName viewName fileName catName)
    let((commentField coForm)
        ; Comment for checkin
        commentField = hiCreateLabel(
            ?name 'commentField
            ?labelText "Do you want to cancel checkout the cell?"
            ?justification 'center
        )
        ; Checkin form
        cancoForm = hiCreateAppForm(
            ?name 'cancoForm
            ?fields list(commentField)
            ?formTitle "Cancel Checkout"
            ?buttonLayout 'OKCancel
            ?callback "csynExecCancelCo(
                libName cellName viewName
    fileName catName)"
        )
        ; Display form
        hiDisplayForm(cancoForm)
    )
)

;----------------
; Procedure to send checkin command to cdsclient
;----------------
procedure(csynExecCancelCo(libName cellName viewName fileName catName)
    let((argslist clicmd
            cliresp respcode
        )
        libPath = ddGetObj(libName)~>readPath
        arglist = list(
            "cellcanco"
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
            println("Checkout Cancelled")
        )
    )
)
