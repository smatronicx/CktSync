;----------------
; This file is part of CktSync design manager
;----------------

;----------------
; Procedure to respond to popup
;----------------
procedure(csynPopup(menuName libName cellName viewName fileName catName)
    ; Sensitize check in/out/cancel
    lmgrSensitizeMenuItems(
        '("csynCheckIn" "csynCheckOut" "csynCancelCo")
    ;  nil
         t
    )
    let((libPath)
        libPath = ddGetObj(libName)~>readPath
        printf("%s:%s\n" libName libPath)
    )

)
