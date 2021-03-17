PRO plot_errors, x_left, x_center, x_right, y_low, y_high
;+
; PRO plot_errors, x_left, x_center, x_right, y_low, y_high
;
; This procedure adds error bars to a plot of the form:
;
;            ---   <-- Y high
;             |
;             |
;            ---   <-- Y low
;
;           / | \
; X--> left cent  right
;
;-
FOR ie = 0, n_elements(x_left)-1 DO BEGIN
  xl = x_left(ie)
  xr = x_right(ie)
  xc = x_center(ie)
  yl = y_low(ie)
  yh = y_high(ie)
  oplot, [xl, xr], [yl, yl]
  oplot, [xl, xr], [yh, yh]
  oplot, [xc, xc], [yl, yh]
END

RETURN
END
