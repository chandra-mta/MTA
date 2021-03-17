PRO rpf_put_value, rpf, pname, pvalue, $
	ERROR=error, DESCRIPTION=description, UNIT=unit
;+
; PRO rpf_put_value, rpf, pname, pvalue, $
;	ERROR=error, DESCRIPTION=description, UNIT=unit
;
; This procedure enters the value of a parameter into an rpf structure
; and, optionally, the parameter's error, description, and/or units.
;
; For more information see:  <this_directory>/rpf_description.txt
;     -------------------------------------------------
; 7/3/99 dd
;     -------------------------------------------------
;-

if n_elements(rpf) LE 0 OR n_elements(pname) LE 0 OR $
	n_elements(pvalue) LE 0 then begin
  doc_library, 'rpf_put_value'
  RETURN
end

; is pname one of the parameters?
this_one = where(rpf.name EQ pname, nfound)

if nfound GE 1 then begin
  ; For multiple occurances modify the one with the greatest
  ; index (e.g., most recent, or "last in, first modified"):
  this_one = this_one(nfound-1)
  ; OK, found it, what kind of value are we storing?
  p_size = SIZE(pvalue)
  ; should be a scalar:
  if p_size(0) NE 0 then begin
    size_str = STRING(p_size(0))
    for is=1,n_elements(p_size)-1 do size_str = size_str+STRING(p_size(is))
    MESSAGE, 'pvalue must be a scalar, SIZE(pvalue) = '+size_str
  end
  ; OK, now do it:
  if p_size(1) EQ 7 then begin
    ; StringValue
    rpf(this_one).DataType = 'StringValue'
    rpf(this_one).StringValue = pvalue
    rpf(this_one).ScalarValue = 0.0
    rpf(this_one).Error = 0.0
  end else begin
    ; ScalarValue
    rpf(this_one).DataType = 'ScalarValue'
    rpf(this_one).ScalarValue = pvalue
    rpf(this_one).StringValue = ''
    if n_elements(error) GT 0 then begin
      rpf(this_one).Error = error
    end else begin
      rpf(this_one).Error = 0.0
    end
  end
  if n_elements(description) GT 0 then begin
    rpf(this_one).Description = description
  end
  if n_elements(unit) GT 0 then begin
    rpf(this_one).Unit = unit
  end
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
