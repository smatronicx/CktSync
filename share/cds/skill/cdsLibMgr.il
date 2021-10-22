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

    ; Update
    lmgrCreateMenuItem("csynUpdateLib" "simple"
        '(
            ("label" "Update")
            ("callback" ("csynLMCBUpdate" "noOpts"))
        )
    )

    lmgrInsertMenuItems("editCheckOutButton" "LCV"
        '("csynUpdateLib")
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

    lmgrInsertMenuItems("csynUpdateLib" "V"
        '("csynCheckIn" "csynCheckOut" "csynCancelCo")
    )

    ; Tag
    ; lmgrCreateMenuItem("csynTagLib" "simple"
    ;     '(
    ;         ("label" "Tag Library")
    ;         ("callback" ("csynLMCBCheckIn" "noOpts"))
    ;     )
    ; )
    ;
    ; lmgrCreateMenuItem("csynTagCell" "simple"
    ;     '(
    ;         ("label" "Tag Cellviews")
    ;         ("callback" ("csynLMCBCheckIn" "noOpts"))
    ;     )
    ; )
    ;
    ; lmgrCreateMenuItem("csynTagCellview" "simple"
    ;     '(
    ;         ("label" "Tag Cellview")
    ;         ("callback" ("csynLMCBCheckIn" "noOpts"))
    ;     )
    ; )
    ;
    ; lmgrInsertMenuItems("editCheckOutButton" "L"
    ;     '("csynTagLib")
    ; )
)
