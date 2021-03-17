PRO PRE_PRINT_LANDSCAPE
;+
; PRO PRE_PRINT_LANDSCAPE
;
; This procedure sets up the device for postscript
; plots - landscape format.
;   ---------------------------------------------------------
; 4/19/91 - dd
;-

SET_PLOT, 'PS'
print, ' ... printer setup from routine ~dd/idl/useful/pre_print_landscape.pro'
device,/LANDSCAPE, font_size = 12

RETURN
END