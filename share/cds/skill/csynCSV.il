;----------------
; This file is part of CktSync design manager
;----------------

;----------------
; Procedure to escape string
;----------------
procedure(csynCSVEscape(str)
    (let (rtnstr patmat)
        ; Escape \n
        patmat = pcreCompile("\\n")
        rtnstr = pcreReplace(patmat str "\\\\n" 0)
        ; Escape ,
        patmat = pcreCompile(",")
        rtnstr = pcreReplace(patmat rtnstr "\\\\," 0)
        rtnstr
    )
)

;----------------
; Procedure to unescape string
;----------------
procedure(csynCSVUnescape(str)
    (let (rtnstr patmat)
        ; Unescape ,
        patmat = pcreCompile("\\\\,")
        rtnstr = pcreReplace(patmat str "," 0)
        ; Unescape \n
        patmat = pcreCompile("\\\\n")
        rtnstr = pcreReplace(patmat rtnstr "\n" 0)
        rtnstr
    )
)

;----------------
; Procedure to convert list to csv string
;----------------
procedure(csynCSVList2String(arglist)
    (let (rtnstr argitem)
        arglist = (foreach mapcar argitem arglist
            ; Escape each string
            csynCSVEscape(argitem)
        )
        ; Make string
        rtnstr = buildString(arglist ",")
        rtnstr
    )
)

;----------------
; Procedure to convert csv string to list
;----------------
procedure(csynCSVString2List(csvstr)
    (let (rtnlist rtnitem idx ch)
        ; Make list
        rtnlist = nil
        rtnitem = ""
        while(idx = nindex(csvstr ",")
            if(idx == 1 then
                ; Empty string
    csvstr = substring(csvstr idx+1)
    rtnlist = cons(rtnitem rtnlist)
    rtnitem = ""
            else
    ch = substring(csvstr idx-1 1)
    if(strcmp(ch "\\") == 0 then
        ; Ignore \,
        rtnitem = strcat(rtnitem substring(csvstr 1 idx))
        csvstr = substring(csvstr idx+1)
    else
        ; Split
        rtnitem = strcat(rtnitem substring(csvstr 1 idx-1))
        csvstr = substring(csvstr idx+1)
        ;println(rtnitem)
        rtnlist = cons(rtnitem rtnlist)
        rtnitem = ""
    )
            )
        )
        ; Last string
        rtnitem = strcat(rtnitem csvstr)
        rtnlist = cons(rtnitem rtnlist)
        rtnlist = reverse(rtnlist)
        rtnlist = (foreach mapcar rtnitem rtnlist
            ; Unescape each string
            csynCSVUnescape(rtnitem)
        )
        rtnlist
    )
)
