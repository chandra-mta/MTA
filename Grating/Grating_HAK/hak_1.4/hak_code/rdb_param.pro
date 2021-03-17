FUNCTION rdb_param, file_name, param_name, HEADER=header
;+
; FUNCTION rdb_param, file_name, param_name, HEADER=header
;
; Get an rdb parameter string from the rdb header comments.
; If the HEADER is supplied then file_name is not needed and
; a dummy variable can be used in the call...
;    ------------------------------------------------
; Pretty big kludge!  Would be better to read the whole
; rdb file into memory (common) with an rdb_open and
; then have rdb_param look in memory...
; 7/4/99 dd Modified to accept HEADER array of strings
;           search that array for parameters...
;           Less kludgey and faster.
;           But strict: the parameter must be in the
;           header in the form:  "#<pname>:" or
;           "# <pname>:"; the next character (usually a TAB)
;           is ignored and the subsequent characters are the
;           returned value.
;    ------------------------------------------------
;-

if n_elements(HEADER) GT 0 then begin
  ; Search in the header for the parameter...
  in_here = WHERE(STRPOS(header, '#'+param_name+':') EQ 0, nfound)
  ; one more chance:
  if nfound EQ 0 then begin
    in_here = WHERE(STRPOS(header, '# '+param_name+':') EQ 0, nfound)
  end
  if nfound EQ 1 then begin
    this_line = header(in_here(0))
    where_is_it = STRPOS(this_line,':')
    param_str = STRMID(this_line, where_is_it+2, 80)
  end else begin
    param_str = ''
  end
end else begin
  ; use "grep" to find the parameter - arg!!!
  SPAWN, 'grep ' + param_name + ' ' + file_name, grep_out
  if STRLEN(grep_out(0)) EQ 0 then begin
    ; oops
    print, " ( rdb_param: couldn't find the parameter "+param_name+ ' )'
    RETURN, ''
  end

  where_is_it = STRPOS(grep_out(0),':')
  param_str = STRMID(grep_out(0), where_is_it+2, 80)
end

RETURN, param_str
END
