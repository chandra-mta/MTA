FUNCTION chip_of_dispx, dispx, zo_loc
;+
; FUNCTION chip_of_dispx, dispx, zo_loc
;
; Returns the name of the S-array chip which
; is dispx pixels from the aim point.  The
; aim point is at zo_loc pixels from S2-S3 gap.
; (Uses approximate values, so not accurate
;  at gaps...)
;    ----------------------------------------------------------
;-

chip_names = ['S0','S1','S2','S3','S4','S5']
if n_elements(zo_loc) EQ 0 then zo_loc = 256.0  ; pixels from S3 gap

froms3s2 = dispx + zo_loc
if froms3s2 GT 0.0 then begin
  iname = 3 + FIX(froms3s2 /(1024.0 + 18.0))
end else begin
  iname = 2 - FIX(-1.0*froms3s2 /(1024.0 + 18.0))
end

this_chip = chip_names( (iname >0) < 5)

RETURN, this_chip
END
