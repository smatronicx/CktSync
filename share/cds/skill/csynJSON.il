;----------------
; This file is part of CktSync design manager
;----------------

;----------------
; Procedure to convert string to JSON object
;----------------
procedure(csynJSONToken(str type row col)
    let((tkn)
        tkn = makeTable("token")
        tkn["value"] = str
        tkn["type"] = type
        tkn["row"] = row
        tkn["col"] = col
        tkn
    )
)

procedure(csynJSONReadString(jsonstr startidx)
    let(((curidx startidx) (jsonlen 0) (outstr nil) (linefeed 0))
        jsonlen = strlen(jsonstr)
        while((curidx <= jsonlen) && !outstr
            ch = substring(jsonstr curidx 1)
            ; Escape
            if(strcmp(ch "\\")==0 then
                curidx = curidx + 1
            )
            ; new line
            if(strcmp(ch "\n")==0 then
                linefeed = linefeed + 1
            )
            ; End of string
            if(strcmp(ch "\"")==0 then
                outstr = substring(jsonstr startidx curidx-startidx)
            )
            curidx = curidx + 1
        )
        curidx = curidx - 1
        list(curidx linefeed outstr)
    )
)

procedure(csynJSONReadNumber(jsonstr startidx)
    let(((jsonlen 0) (outstr nil) (repat nil))
        repat = pcreCompile("([0-9][0-9]*([.][0-9])?[0-9]*([e|E]([+|-])*[0-9][0-9]*)*)")
        jsonlen = strlen(jsonstr)
        outstr = substring(jsonstr startidx jsonlen)
        pcreExecute(repat outstr)
        outstr = pcreSubstitute("\\0")
        outstr
    )
)

procedure(csynJSONLexer(jsonstr)
    let(
        (
            (curidx 1) (curline 1) (tokens list(nil)) (tkn nil)
            (curcol 0) (jsonlen 0) (rtnval nil)
            (repat nil)
        )
        jsonlen = strlen(jsonstr)
        while(curidx <= jsonlen
            tkn = nil
            ch = substring(jsonstr curidx 1)
            ; LBRACKET
            if(strcmp(ch "[")==0 then
                tkn = csynJSONToken(ch "LBRACKET" curline curcol)
            )
            ; RBRACKET
            if(strcmp(ch "]")==0 then
                tkn = csynJSONToken(ch "RBRACKET" curline curcol)
            )
            ; LBRACE
            if(strcmp(ch "{")==0 then
                tkn = csynJSONToken(ch "LBRACE" curline curcol)
            )
            ; RBRACE
            if(strcmp(ch "}")==0 then
                tkn = csynJSONToken(ch "RBRACE" curline curcol)
            )
            ; COLON
            if(strcmp(ch ":")==0 then
                tkn = csynJSONToken(ch "COLON" curline curcol)
            )
            ; COMMA
            if(strcmp(ch ",")==0 then
                tkn = csynJSONToken(ch "COMMA" curline curcol)
            )
            ; STRING
            if(strcmp(ch "\"")==0 then
                rtnval = csynJSONReadString(jsonstr curidx+1)
                tkn = csynJSONToken(nth(2 rtnval) "STRING" curline curcol)
                curidx = nth(0 rtnval)
                curline = curline + nth(1 rtnval)
            )
            ; True
            if(strcmp(ch "t")==0 then
                rtnval = substring(jsonstr curidx 4)
                tkn = csynJSONToken(rtnval "TRUE" curline curcol)
                curidx = curidx+3
            )
            ; False
            if(strcmp(ch "f")==0 then
                rtnval = substring(jsonstr curidx 5)
                tkn = csynJSONToken(rtnval "FALSE" curline curcol)
                curidx = curidx+4
            )
            ; Null
            if(strcmp(ch "n")==0 then
                rtnval = substring(jsonstr curidx 4)
                tkn = csynJSONToken(rtnval "NULL" curline curcol)
                curidx = curidx+3
            )
            ; Number
            repat = pcreCompile("[0-9]")
            if(pcreExecute(repat ch) then
                rtnval = csynJSONReadNumber(jsonstr curidx)
                tkn = csynJSONToken(rtnval "NUMBER" curline curcol)
                curidx = curidx + strlen(rtnval) - 1
            )
            if(strcmp(ch "-")==0 then
                curidx = curidx + 1
                rtnval = csynJSONReadNumber(jsonstr curidx)
                rtnval = strcat("-" rtnval)
                tkn = csynJSONToken(rtnval "NUMBER" curline curcol)
                curidx = curidx + strlen(rtnval) - 2
            )
            ; New line
            if(strcmp(ch "\n")==0 then
                curline = curline + 1
            )
            ; White space
            if(strcmp(ch "\r")==0 then
                ()
            )
            if(strcmp(ch "\t")==0 then
                ()
            )
            if(strcmp(ch " ")==0 then
                ()
            )

            ; Add token
            if(tkn
                tconc(tokens tkn)
            )
            curidx = curidx + 1
        )
        tokens = car(tokens)
        ; printf("%d\n" length(tokens))
        ; foreach(tkn tokens
        ;     printf("%d:%d:%s:%s\n" tkn["row"] tkn["col"] tkn["type"] tkn["value"])
        ; )
        tokens
    )
)

procedure(csynJSONParse(jsonstr)
    let((junk11)
    procedure(JSONLex1()
        ;junk11 = "\"string\\n\""
        arglist = list(
            "cellcanco"
            "libPath"
            "cellName"
            "viewName"
        )
        ; Build command and send to client
        clicmd = csynCSVList2String(arglist)
        csynSendCommand(clicmd)
        ; Get response for command
        cliresp = csynGetResponse()
        ;cliresp = csynCSVString2List(cliresp)
        ;respcode = nth(0 cliresp)
        csynJSONLexer(cliresp)
        ;print(cliresp)
    )
    JSONLex1())
)
