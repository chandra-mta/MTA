PRO rdb_write, filename, rdb_struct, HEADER=header, SILENT=silent
;+
; PRO rdb_write, filename, rdb_struct, HEADER=header, SILENT=silent
;
; Create an rdb file from an rdb_structure
; (and array of a structure).  The rdb
; columns get the names of the structure
; tags and the type (N or S) is determined
; as well.
;      ---------------------------------------------------
; 970412 dd HEADER is an optional string array that
; will be printed as lines before the rdb data
; e.g. HEADER=hdr with hdr set to:
;   hdr = STRARR(2)
;   hdr(0) = '# Love header info'
;   hdr(1) = '# LiveTime	: 10.0'
; 990704 dd Check for leading "#" in all header lines
;           and add it if not there.
; 990705 dd Remove the "FLOAT( )" in the writing out "N" type
;           data: if it's integer we'll get a smaller file.
;      ---------------------------------------------------
;-

; get the tag names
tags = TAG_NAMES(rdb_struct(0))

; create the column names and types lines
names = ''
types = ''
type_arr = STRARR(n_elements(tags))
for ic=0,n_elements(tags)-1 do begin
  if ic NE 0 then begin
    ; TAB delimited
    names = names + STRING(9B)
    types = types + STRING(9B)
  end
  names = names + STRLOWCASE(tags(ic)) ; use lower case
  size_arr = SIZE(rdb_struct(0).(ic))
  if size_arr(1) EQ 7 then this_type = 'S' else this_type = 'N'
  types = types + this_type
  type_arr(ic) = this_type
end
; Show what's happening...
if NOT(KEYWORD_SET(SILENT)) then begin
  print, names
  print, types
end
 
; Write it out
OPENW, outunit, filename, /GET
if KEYWORD_SET(HEADER) then begin
  for ih=0,n_elements(header)-1 do begin
    if STRPOS(header(ih),'#') EQ 0 then begin
      printf, outunit, header(ih)
    end else begin
      printf, outunit, '#'+header(ih)
    end
  end
end else begin
  printf, outunit, '# created by rdb_write.pro, '+SYSTIME()
end

printf, outunit, names
printf, outunit, types
ir = LONG(0)
while ir LT n_elements(rdb_struct) do begin
  this_line = ''
  for ic=0,n_elements(tags)-1 do begin
    if ic NE 0 then this_line = this_line + STRING(9B)
    if type_arr(ic) EQ 'S' then begin
      this_line = this_line + rdb_struct(ir).(ic)
    end else begin
      this_line = this_line + $
	STRCOMPRESS(STRING(rdb_struct(ir).(ic)),/REMOVE)
    end
  end
  printf, outunit, this_line
  ir = ir + 1
end
CLOSE, outunit
FREE_LUN, outunit

RETURN
END
