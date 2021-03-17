FUNCTION INTERPOL_SORT, y_table, x_table, x_desired, SILENT=silent
;+
; FUNCTION INTERPOL_SORT, y_table, x_table, x_desired, SILENT=silent
;
; INTERPOL_SORT does linear interpolation of the relation defined
; by y and x at the desired (x_desired) x values and returns the
; corresponding y values.  This is faster than the IDL INTERPOL
; procedure.
; 
; For example:
;  interpolated_values = INTERPOL_SORT(y_table, x_table, x_of_desired_values)
;
; /SILENT suppresses printout of out-of-range notices.
;
;    ------------------------------------------------------------
;
; 8/31/94 dd Modified to not stop when out of the table range
;            instead it interpolates using bottom two or top two points.
;    ------------------------------------------------------------
;-

; x_desired can be a scalar or a vector
; if it is a scalar put it in a vector
xd = x_desired  ; default
x_type = size(x_desired)
if(x_type(0) EQ 0) then xd = [x_desired]


IF NOT keyword_set(SILENT) THEN BEGIN 
  ; Check the x's limits.  Flag it only if more than a bin or so...
  x_span = max(xd) - min(xd)

  if ( (min(xd) - min(x_table)) LT -x_span/n_elements(x_table) ) then begin
  
    print, "INTERPOL - x is less than x_table range"
    print, " min(x_table) =",min(x_table)
    print, " min(x_desired) = ", min(x_desired)
  ;  stop
  
  ENDIF
  
  if ( (max(xd) - max(x_table)) GT x_span/n_elements(x_table) ) then begin
    print, "INTERPOL - x is greater than x_table range"
    print, " max(x_table) =",max(x_table)
    print, " max(x_desired) = ", max(x_desired)
  ;  stop
  ENDIF

ENDIF

; Sort the x_desireds and go through them in order to
; avoid researching for each x_desired
imap = SORT(xd)

; setup output vector
yi = xd

; start at the bottom of the table
ipoint = 0L ; current index in table
xlow = x_table(ipoint)
xhigh = x_table(ipoint+1)
tab_size = n_elements(x_table)

; now go through the desired x's in increasing order
FOR ii = 0L, n_elements(xd)-1 DO BEGIN
xi = xd(imap(ii)) ; next x value to find in table
; Increase pointer in table until getting the high entry above the
;  desired lookup value.
; This has the effect that points below the table are interpolated
;  from the lowest two entries.
; Do not increase the pointer above the top of the table;
;  this has the effect that points above the table are interpolated
;  from the top two entries
WHILE (xhigh LT xi AND $
	ipoint LT tab_size-2) DO BEGIN
  ipoint = ipoint+1
  xlow = x_table(ipoint)
  xhigh = x_table(ipoint+1)
end
; now calculate the interpolated y value:
ylow=y_table(ipoint)
yhigh = y_table(ipoint+1)
yi(imap(ii)) = ylow + (xi-xlow)*(yhigh-ylow)/(xhigh-xlow)
; go to next point
END

; return a scalar if that is what came in to x_desired.
y_interp = yi
if(x_type(0) EQ 0) then y_interp = yi(0)
RETURN, y_interp
END





