;----------------
; This file is part of CktSync design manager
;----------------

;----------------
; Fail if CKTSYNC_DIR is not defined.
;----------------
unless(csynSyncDir = getShellEnvVar("CKTSYNC_DIR")
    error(
        "Environment variable CKTSYNC_DIR is not set."
    )
)

csynSkillDir = strcat(csynSyncDir "/share/cds/skill/")

;----------------
; Print the program version.
;----------------
procedure(csynPrintVersion()
    let((verFile verStr lineCh)
        verFile = infile(strcat(csynSyncDir "/version"))
        while(gets(verStr verFile)
            if(rexMatchp("^#" verStr) then
                ; Do nothing
            else
    csynVersion = verStr
            )
        )
    )
    printf(
        "Loading CktSync Design Manager...\nVersion %s\n"
        csynVersion
    )
)
csynPrintVersion()


;----------------
; Load required files.
;----------------
csynSourceFiles = '(
    "csynUtil.il" "csynJSON.il"
    "csynLM.il" "csynConnect.il" "csynCSV.il"
    "csynCheckIn.il" "csynCheckOut.il" "csynCancelCo.il"
    "csynUpdate.il"
)

procedure(csynLoadSourceFiles()
    let((srcFile)
        foreach(srcFile csynSourceFiles
            load(strcat(csynSkillDir srcFile))
        )
    )
)

csynLoadSourceFiles()

csynJSONParse("M")
