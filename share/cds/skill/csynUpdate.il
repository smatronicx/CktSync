;----------------
; This file is part of CktSync design manager
;----------------

;----------------
; Procedure to update workarea
;----------------
procedure(csynLMCBUpdate(menuName libName cellName viewName fileName catName)
    csynExecUpdate(libName cellName viewName fileName catName)
)

;----------------
; Procedure to send checkin command to cdsclient
;----------------
procedure(csynExecUpdate(libName cellName viewName fileName catName)
    let((argslist clicmd
            cliresp respcode
        )
        libPath = ddGetObj(libName)~>readPath
        arglist = list(
            "update"
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
            ddUpdateLibList()
            csynShowMessage("Update done")
        )
    )
)
