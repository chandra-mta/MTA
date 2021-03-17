PRO rpf_get_value, rpf, pname, pvalue, $
	ERROR=error, DESCRIPTION=description, UNIT=unit
;+
; PRO rpf_get_value, rpf, pname, pvalue, $
;	ERROR=error, DESCRIPTION=description, UNIT=unit
;
; This procedure returns the value of a parameter from an rpf structure
; and, optionally, the parameter's error, description, and/or units.
;
; For more information see:  <this_directory>/rpf_description.txt
;     -------------------------------------------------
; 7/3/99 dd
;     -------------------------------------------------
;-

if n_elements(rpf) LE 0 then begin
  doc_library, 'rpf_get_value'
  RETURN
end

; is pname one of the parameters?
this_one = where(rpf.name EQ pname, nfound)

if nfound GE 1 then begin
  ; For multiple occurances get the one with the greatest
  ; index (e.g., most recent, or "last in, first out"):
  this_one = this_one(nfound-1)
  ; OK, found it: return the info
  if STRUPCASE(rpf(this_one).DataType) EQ 'STRINGVALUE' then begin
    ; StringValue
    pvalue = rpf(this_one).StringValue
  end else begin
    ; ScalarValue
    pvalue = rpf(this_one).ScalarValue
    error = rpf(this_one).Error
  end
  description = rpf(this_one).Description
  unit = rpf(this_one).Unit
end else begin
  ; whoopsies: pname not found in rpf structure...
  ; leave pvalue, etc undefined and call for a fatal error
  ; with some helpful info added.
  name_list = rpf(0).NAME
  for in=1,n_elements(rpf)-1 do  name_list = name_list+','+rpf(in).NAME
  MESSAGE, '"'+pname+'" not found among the rpf structure names: '+name_list
end

RETURN
END
