PRO marx_timing_sim, evts, te_time, ACISIARRAY=acisiarray
;+
; PRO marx_timing_sim, evts[, te_time] [, /ACISIARRAY]
;
; This procedure takes as input and output an event
; structure such as would be created by mrdfits
; reading a level 1 file.  The TIME, CHIPY, TDETY, and DETY
; are modified to include to ACIS effects not in MARX 2.22
; or earlier versions:
;   - TIME is quantized to multiples of the frametime
;   - events arriving during the frame transfer are blured
;     in CHIPY, TDETY, and DETY.
;
; The KEYWORD ACISIARRAY causes the TDETX and DETX to be
; streaked.
;
; - - - - - - - - - - - - - - - - - -
; 8/1/99 dd Original version.
; - - - - - - - - - - - - - - - - - -
;-

; - - - - - - - - - - - - - - - - 
; Parameters
; TE Exposure Time
if n_elements(te_time) EQ 0 then te_time = 3.3
; Frame Transfer Time
; ...force DOUBLEtime
frame_trans_time = DOUBLE(0.040)
; note that the quantization "period" is the sum of these:
period = te_time + frame_trans_time

; - - - - - - - - - - - - - - - - 
; Quantize the TIME to multiples of period:
exact_time = evts.TIME
quant_time = DOUBLE(period * LONG(exact_time/period))
remainder = exact_time - quant_time

evts.TIME = quant_time

; - - - - - - - - - - - - - - - - 
; Now, when the remainder is in te_time to period
; we mess up the TDETY and DETY by a proportional amount...
; ("X" for ACIS-I)
y_streak = ((remainder - te_time) > 0.0) * 1024.0/frame_trans_time

old_chipY = evts.CHIPY
new_chipY = old_chipY + y_streak
; if new_chipY GE 1024 then subtract 1024
new_chipY = new_chipY - FLOAT(new_chipY GE 1024) * 1024

evts.CHIPY = new_chipY

; And modify TDETY and DETY by the same amount:
delta_Y = new_chipY - old_chipY

if KEYWORD_SET(ACISIARRAY) then begin
  ; ACIS-I: streak is in "X"
  evts.TDETX = evts.TDETX + delta_Y
  evts.DETX = evts.DETX + delta_Y
end else begin
  ; ACIS-S: streak is in "Y"
  evts.TDETY = evts.TDETY + delta_Y
  evts.DETY = evts.DETY + delta_Y
end
 
RETURN
END
