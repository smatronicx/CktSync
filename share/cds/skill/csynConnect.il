;----------------
; This file is part of CktSync design manager
;----------------

;----------------
; Procedure to start cdsclient
;----------------
procedure(csynStartClient()
    csynClientPID = ipcBeginProcess(
        strcat(getShellEnvVar("CKTSYNC_DIR") "/share/cds/bin/cdsclient.sh")
        "" "" ""
    )
)
csynStartClient()

;----------------
; Procedure to purge pid
;----------------
procedure(csynPurge(pid)
    let((ipcReturn)
        while(
            (ipcReturn = ipcReadProcess(pid)) &&
            (ipcReturn != "")
            t
        )
    )
)


;----------------
; Procedure to read line from pid
;----------------
procedure(csynReadLine(pid @key (timeOut 30))
    let(
        (
            ipcReturn (ipcLine "") (continueRead t)
        )
        while(continueRead && (ipcReturn = ipcReadProcess(pid timeOut))
            if(ipcReturn == "" then
                ; got blank line, break
                continueRead = nil
            else
                ipcLine = strcat(ipcLine ipcReturn)
                if(rexMatchp("\n$" ipcLine) then
                    ; got full line, break
                    continueRead = nil
                )
            )
        )
        ipcLine
    )
)

;----------------
; Procedure to read response to cdsclient
;----------------
procedure(csynGetResponse(@key (timeOut 30))
    let(((responseVal ""))
        if(boundp('csynClientPID) && ipcIsActiveProcess(csynClientPID) then
            responseVal = csynReadLine(csynClientPID ?timeOut timeOut)
        else
            csynShowMessage("CktSync Client is not running")
        )
        ; Remove trailing \n
        responseVal = substring(responseVal 1 length(responseVal)-1)
        responseVal
    )
)

;----------------
; Procedure to send command to cdsclient
;----------------
procedure(csynSendCommand(csynCmd)
    let(()
        if(boundp('csynClientPID) && ipcIsActiveProcess(csynClientPID) then
            csynCmd = strcat(csynCmd "\n")
            csynPurge(csynClientPID)
            ipcWriteProcess(csynClientPID csynCmd)
        else
            csynShowMessage("CktSync Client is not running")
        )
    )
)
