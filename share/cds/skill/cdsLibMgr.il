;----------------
; This file is part of CktSync design manager
;----------------
when(getShellEnvVar("CKTSYNC_DIR")

    ;Remove existing Design Manager
    lmgrManageMenuItems(
        '(
            "editDeleteButton"
            "editDeleteViewButton"
            ;"FileNewCVButton"
            "editCheckInButton"
            "editCheckOutButton"
            "editCancelCheckOutButton"
            "workAreaUpdateButton"
            "submitButton"
            "smallUpdateButton"
            "submitSeparator"
            "workAreaSeparator"
            "dmPropertyCascade"
            "designSeparator2"
            "designSeparator1"
        )
        nil
    )

    ;Popup control for CktSync
    lmgrCreateMenu("popup"
        '(
            ("mapCallback" ("csynPopup"))
        )
    )

    ; Check in/out/cancel
    lmgrCreateMenuItem("csynCheckOut" "simple"
        '(
            ("label" "Check Out")
            ("callback" ("csynLMCBCheckOut" "noOpts"))
        )
    )

    lmgrCreateMenuItem("csynCheckIn" "simple"
        '(
            ("label" "Check In")
            ("callback" ("csynLMCBCheckIn" "noOpts"))
        )
    )

    lmgrCreateMenuItem("csynCancelCo" "simple"
        '(
            ("label" "Cancel Checkout")
            ("callback" ("csynLMCBCancelCo" "noOpts"))
        )
    )

    lmgrInsertMenuItems("editCheckOutButton" "Vv"
        '("csynCheckIn" "csynCheckOut" "csynCancelCo")
    )
)
