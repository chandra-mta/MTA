PRO rpf_add_param, rpf, pname, pvalue, $
	ERROR=error, DESCRIPTION=description, UNIT=unit
;+
; PRO rpf_add_param, rpf, pname, pvalue, $
;	ERROR=error, DESCRIPTION=description, UNIT=unit
;
; This procedure appends a new parameter to an rpf structure.
; The parameter's value may be set
; and, optionally, the parameter's error, description, and/or units.
;
; For more information see:  <this_directory>/rpf_description.txt
;     -------------------------------------------------
; 7/3/99 dd
;     -------------------------------------------------
;-

if n_elements(rpf) LE 0 OR n_elements(pname) LE 0 then begin
  doc_library, 'rpf_add_param'
  RETURN
end

; Add another parameter to the array structure:
rpf = [rpf, rpf(0)]
this_one = n_elements(rpf)-1
rpf(this_one).Name = pname
rpf(this_one).DataType = 'None'
rpf(this_one).StringValue = ''
rpf(this_one).ScalarValue = 0.0
rpf(this_one).Error = 0.0
rpf(this_one).Description = ''
rpf(this_one).Unit = ''

if n_elements(pvalue) GE 1 then begin
  ; OK, what kind of value are we storing?
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
end

RETURN
END
