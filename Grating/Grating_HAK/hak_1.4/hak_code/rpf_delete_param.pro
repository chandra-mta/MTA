PRO rpf_delete_param, rpf, pname, ndeleted
;+
; PRO rpf_delete_param, rpf, pname, ndeleted
;
; This procedure removes all occurances of a parameter from
; an rpf structure.  If this action would result in an
; empty structure, the structure returned is the
; one-parameter structure created by rpf_create.
;
; For more information see:  <this_directory>/rpf_description.txt
;     -------------------------------------------------
; 7/3/99 dd
;     -------------------------------------------------
;-

if n_elements(rpf) LE 0 OR n_elements(pname) LE 0 then begin
  doc_library, 'rpf_delete_param'
  RETURN
end

; Find the parameter
these = where(rpf.Name EQ pname, nfound)

if nfound GE 1 then begin
  ; OK, found the parameter...
  ; we'll get rid of all of them...
  ndeleted=nfound
  ; Will it's deletion create an empty structure?
  if nfound EQ n_elements(rpf) then begin
    rpf_create, rpf
  end else begin
    ; keep all the non-matching ones
    those = where(rpf.Name NE pname)
    rpf = rpf(those)
  end
end else begin
  ndeleted=0
end

RETURN
END
