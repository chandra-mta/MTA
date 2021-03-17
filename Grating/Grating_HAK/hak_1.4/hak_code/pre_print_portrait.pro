PRO PRE_PRINT_portrait
;+
; PRO PRE_PRINT_PORTRAIT
;
; This procedure sets up the device for postscript
; plots - portrait format.
;   ---------------------------------------------------------
;-

; Set parameters for portrait plots...
SET_PLOT, 'PS'
print, ' ... printer setup from routine !DDIDL/useful/pre_print_portrait.pro'
device, /portrait,/inch,font_size = 12, XSIZE=6.5, YSIZE=10.0, $
	YOFFSET=0.5, XOFFSET=1.0

RETURN
END