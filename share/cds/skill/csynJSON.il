;----------------
; This file is part of CktSync design manager
;----------------

;----------------
; Procedure to convert string to JSON object
;----------------

;----------------
; Procedure for JSON Lexer
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
            (numpat nil)
        )
        jsonlen = strlen(jsonstr)
        while(curidx <= jsonlen
            tkn = nil
            ch = substring(jsonstr curidx 1)
            numpat = pcreExecute(pcreCompile("[0-9]") ch)
            cond(
                ; LBRACKET
                ((strcmp(ch "[")==0)
                    tkn = csynJSONToken(ch "LBRACKET" curline curcol)
                )
                ; RBRACKET
                ((strcmp(ch "]")==0)
                    tkn = csynJSONToken(ch "RBRACKET" curline curcol)
                )
                ; LBRACE
                ((strcmp(ch "{")==0)
                    tkn = csynJSONToken(ch "LBRACE" curline curcol)
                )
                ; RBRACE
                ((strcmp(ch "}")==0)
                    tkn = csynJSONToken(ch "RBRACE" curline curcol)
                )
                ; COLON
                ((strcmp(ch ":")==0)
                    tkn = csynJSONToken(ch "COLON" curline curcol)
                )
                ; COMMA
                ((strcmp(ch ",")==0)
                    tkn = csynJSONToken(ch "COMMA" curline curcol)
                )
                ; STRING
                ((strcmp(ch "\"")==0)
                    rtnval = csynJSONReadString(jsonstr curidx+1)
                    tkn = csynJSONToken(nth(2 rtnval) "STRING" curline curcol)
                    curidx = nth(0 rtnval)
                    curline = curline + nth(1 rtnval)
                )
                ; True
                ((strcmp(ch "t")==0)
                    rtnval = substring(jsonstr curidx 4)
                    tkn = csynJSONToken(rtnval "TRUE" curline curcol)
                    curidx = curidx+3
                )
            ;     ; False
                ((strcmp(ch "f")==0)
                    rtnval = substring(jsonstr curidx 5)
                    tkn = csynJSONToken(rtnval "FALSE" curline curcol)
                    curidx = curidx+4
                )
                ; Null
                ((strcmp(ch "n")==0)
                    rtnval = substring(jsonstr curidx 4)
                    tkn = csynJSONToken(rtnval "NULL" curline curcol)
                    curidx = curidx+3
                )
                ; Number
                ((null !numpat)
                    rtnval = csynJSONReadNumber(jsonstr curidx)
                    tkn = csynJSONToken(rtnval "NUMBER" curline curcol)
                    curidx = curidx + strlen(rtnval) - 1
                )
                ((strcmp(ch "-")==0)
                    curidx = curidx + 1
                    rtnval = csynJSONReadNumber(jsonstr curidx)
                    rtnval = strcat("-" rtnval)
                    tkn = csynJSONToken(rtnval "NUMBER" curline curcol)
                    curidx = curidx + strlen(rtnval) - 2
                )
                ; New line
                ((strcmp(ch "\n")==0)
                    curline = curline + 1
                )
                ; White space
                ((strcmp(ch "\r")==0)
                    ()
                )
                ((strcmp(ch "\t")==0)
                    ()
                )
                ((strcmp(ch " ")==0)
                    ()
                )
                ; Error
                (t
                    sprintf(rtnval "Unexpected character %s at %d\n", ch, curline)
                    error(rtnval)
                )
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

;----------------
; Procedure for JSON Parser
;----------------
procedure(csynJSONParseArray(tokens curidx)
    let(
        (
            (curtkn nil) (breakloop nil) (tokenlen 0) (rtnlist list(nil))
            (rtnval nil)
        )
        tokenlen = length(tokens)
        while((curidx < tokenlen) && !breakloop
            curtkn = nth(curidx tokens)
            cond(
                ((strcmp(curtkn["type"], "RBRACKET")==0)
                    breakloop = t
                )
                ((strcmp(curtkn["type"], "COMMA")==0)
                    ()
                )
                ; Read value
                (t
                    rtnval = csynJSONParseValue(tokens curidx)
                    tconc(rtnlist nth(0 rtnval))
                    curidx = nth(1 rtnval)
                )
            )
            curidx = curidx + 1
        )
        if(!breakloop then
            sprintf(rtnval "Unexpected token %s at %d\n", curtkn["value"], curtkn["row"])
            error(rtnval)
        )
        curidx = curidx - 1
        rtnlist = car(rtnlist)
        rtnval = list(rtnlist curidx)
        rtnval
    )
)

procedure(csynJSONParseObjectKV(tokens curidx)
    let(((rtnval nil) (key nil) (value nil) (curtkn nil))
        curtkn = nth(curidx tokens)
        if(strcmp(curtkn["type"], "STRING")!=0 then
            sprintf(rtnval "Expected string. Unexpected token %s at %d\n", curtkn["value"], curtkn["row"])
            error(rtnval)
        ))
        key = curtkn["value"]
        curidx = curidx + 1
        curtkn = nth(curidx tokens)
        if(strcmp(curtkn["type"], "COLON")!=0 then
            sprintf(rtnval "Expected :. Unexpected token %s at %d\n", curtkn["value"], curtkn["row"])
            error(rtnval)
        )
        curidx = curidx + 1
        rtnval = csynJSONParseValue(tokens curidx)
        value = nth(0 rtnval)
        curidx = nth(1 rtnval)
        rtnval = list(key value curidx)
        rtnval
    )
)

procedure(csynJSONParseObject(tokens curidx)
    let(
        (
            (curtkn nil) (breakloop nil) (tokenlen 0) (rtnobj makeTable("obj"))
            (rtnval nil) (key nil) (value nil)
        )
        tokenlen = length(tokens)
        while((curidx < tokenlen) && !breakloop
            curtkn = nth(curidx tokens)
            cond(
                ((strcmp(curtkn["type"], "RBRACE")==0)
                    breakloop = t
                )
                ((strcmp(curtkn["type"], "COMMA")==0)
                    ()
                )
                ; Read key value
                (t
                    rtnval = csynJSONParseObjectKV(tokens curidx)
                    key = nth(0 rtnval)
                    value = nth(1 rtnval)
                    curidx = nth(2 rtnval)
                    rtnobj[key] = value
                )
            )
            curidx = curidx + 1
        )
        if(!breakloop then
            sprintf(rtnval "Unexpected token %s at %d\n", curtkn["value"], curtkn["row"])
            error(rtnval)
        )
        curidx = curidx - 1
        rtnval = list(rtnobj curidx)
        rtnval
    )
)

procedure(csynJSONParseValue(tokens curidx)
    let(((curtkn nil) (rtnval nil))
        curtkn = nth(curidx tokens)
        cond(
            ((strcmp(curtkn["type"], "LBRACKET")==0)
                curidx = curidx + 1
                rtnval = csynJSONParseArray(tokens curidx)
                curidx = nth(1 rtnval)
                rtnval = nth(0 rtnval)
            )
            ((strcmp(curtkn["type"], "LBRACE")==0)
                curidx = curidx + 1
                rtnval = csynJSONParseObject(tokens curidx)
                curidx = nth(1 rtnval)
                rtnval = nth(0 rtnval)
            )
            ((strcmp(curtkn["type"], "NUMBER")==0)
                rtnval = curtkn["value"]
            )
            ((strcmp(curtkn["type"], "STRING")==0)
                rtnval = curtkn["value"]
            )
            ((strcmp(curtkn["type"], "TRUE")==0)
                rtnval = curtkn["value"]
            )
            ((strcmp(curtkn["type"], "FALSE")==0)
                rtnval = curtkn["value"]
            )
            ((strcmp(curtkn["type"], "NULL")==0)
                rtnval = curtkn["value"]
            )
            (t
                sprintf(rtnval "Unexpected token %s at %d\n", curtkn["value"], curtkn["row"])
                error(rtnval)
            )
        )
        rtnval = list(rtnval curidx)
        rtnval
    )
)

procedure(csynJSONParse(jsonstr)
    let((junk11)
    procedure(JSONLex1()
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
        junk11 = csynJSONLexer(cliresp)
        junk11 = csynJSONParseValue(junk11 0)
        println(nth(0 junk11))
        junk11 = csynJSONtoString(nth(0 junk11))
        printf("%s\n", junk11)
        ;print(cliresp)
    )
    JSONLex1())
)

;----------------
; Procedure for JSON object to string
;----------------
procedure(csynJSONWriteArray(jsonobj)
    let(((jsonstr "") (item nil) (rtnval nil))
        if(length(jsonobj)==0 then
            jsonstr = "[]"
        else
            foreach(item jsonobj
                rtnval = csynJSONtoString(item)
                sprintf(jsonstr, "%s, %s", jsonstr, rtnval)
            )
            sprintf(jsonstr, "[%s]", substring(jsonstr 3 length(jsonstr)-2))
        )
        jsonstr
    )
)

procedure(csynJSONWriteObject(jsonobj)
    let(((jsonstr "") (item nil) (rtnval nil))
        if(length(jsonobj)==0 then
            jsonstr = "{}"
        else
            foreach(item jsonobj
                rtnval = csynJSONtoString(jsonobj[item])
                sprintf(jsonstr, "%s, \"%s\": %s", jsonstr, item, rtnval)
            )
            sprintf(jsonstr, "{%s}", substring(jsonstr 3 length(jsonstr)-2))
        )
        jsonstr
    )
)

procedure(csynJSONWriteNumber(jsonobj)
    let(((jsonstr ""))
        cond(
            ((null !integerp(jsonobj))
                sprintf(jsonstr, "%d", jsonobj)
            )
            ((null !realp(jsonobj))
                sprintf(jsonstr, "%g", jsonobj)
            )
        )
        jsonstr
    )
)

procedure(csynJSONtoString(jsonobj)
    let(((objtype nil) (jsonstr ""))
        cond(
            ; Table
            ((null !tablep(jsonobj))
                jsonstr = csynJSONWriteObject(jsonobj)
            )
            ; List
            ((null !listp(jsonobj))
                jsonstr = csynJSONWriteArray(jsonobj)
            )
            ; String
            ((null !stringp(jsonobj))
                sprintf(jsonstr "\"%s\"" jsonobj)
            )
            ; Number
            ((null !integerp(jsonobj))
                jsonstr = csynJSONWriteNumber(jsonobj)
            )
            ((null !realp(jsonobj))
                jsonstr = csynJSONWriteNumber(jsonobj)
            )
            ; True
            ((null !jsonobj)
                jsonstr = "true"
            )
            ; False
            ((null jsonobj)
                jsonstr = "false"
            )
        )
        jsonstr
    )
)
