PRO PRE_PRINT_SQR
;+
; PRO PRE_PRINT_SQR
;
; This procedure sets up the device for postscript
; plots - portrait mode with plot region approx square is set up.
;   ---------------------------------------------------------
;-

; Parameters for a "square" aspect ratio
SET_PLOT, 'PS'
print, ' ... printer setup from routine ...idl/useful/pre_print_sqr.pro'
device, /portrait,font_size = 12, XSIZE=17.8, YSIZE=17.0, $
	YOFFSET=8.4, XOFFSET=2.0

RETURN
END