PRO dd_load_ct, SHOW = show, RED=red, GREEN=green, BLUE=blue, $
	OTHER_MAP=other_map
;+
;PRO dd_load_ct, SHOW = show, RED=red, GREEN=green, BLUE=blue, $
;	OTHER_MAP=other_map
;
; Load a nice color table to go from red to blue in a continous way
; The /OTHER_MAP keyword selects another (better) mapping.
;   ------------------------------------------------------------
; 1999-02-06 Modified for slightly different mapping...
; 1999-05-30 Improved "8-bit" color output:  make .ps of it to check...
;   ------------------------------------------------------------
;-

; testing it:
; setup ps output
;   SET_PLOT, 'PS'
;   device, filename='idl.ps',/landscape,/bold,font_size = 14, /COLOR
; compile, run, and make .gif from .ps:
;   .run dd_load_ct
;   dd_load_ct, /SH, /OTH
;   device, /close
;   $ps2gif idl.ps
;   $xv idl.gif 
; - - -
red = intarr(256)
green = intarr(256)
blue = intarr(256)

path = fltarr(3,256)

other_mapping = KEYWORD_SET(OTHER_MAP)

; ~Red to Yellow (3-96)
if other_mapping then begin
  start = [1.0,0.0,0.]
  stop = [1.0,0.7,0.]
end else begin
  start = [1.0,0.3,0.]
  stop = [1.,1.,0.]
end
steps = indgen(94)
; steps goes from 0-->1
steps = steps/FLOAT(n_elements(steps)-1)
steps = (steps)^0.75
for is=0,n_elements(steps)-1 do path(*,3+is) = (1.-steps(is))*start + $
	steps(is)*stop

; Yellow to Green (97-150)
if other_mapping then begin
  ;start = [1.0,0.7,0.]
  ;stop = [0.5,1.,0.]
  ; 5/30/99:
  start = [1.0,0.7,0.]
  stop = [0.11,1.,0.]
end else begin
  start = [1.0,1.,0.]
  stop = [0.5,1.,0.]
end
steps = indgen(54)
; steps goes from 0-->1
steps = steps/FLOAT(n_elements(steps)-1)
for is=0,n_elements(steps)-1 do path(*,97+is) = (1.-steps(is))*start + $
	steps(is)*stop

; Green to Cyan (151-234)
if other_mapping then begin
  ;start = [0.0,1.0,0.5]
  ;stop = [0.,1.,0.9]
  start = [0.0,1.0,0.11]
  stop = [0.,1.,0.9]
end else begin
  start = [0.0,1.0,0.5]
  stop = [0.,1.,0.9]
end
steps = indgen(84)
; steps goes from 0-->1
steps = steps/FLOAT(n_elements(steps)-1)
for is=0,n_elements(steps)-1 do path(*,151+is) = (1.-steps(is))*start + $
	steps(is)*stop

; Cyan to White (235-254)
if other_mapping then begin
  ;start = [0.3,0.99,0.9]
  ;stop = [0.90,0.99,0.90]
  start = [0.0,1.0,0.9]
  stop = [0.5,1.0,1.0]
end else begin
  start = [0.3,0.99,0.9]
  stop = [0.90,0.99,0.90]
end
steps = indgen(20)
; steps goes from 0-->1
steps = steps/FLOAT(n_elements(steps)-1)
steps = steps^0.75
for is=0,n_elements(steps)-1 do path(*,235+is) = (1.-steps(is))*start + $
	steps(is)*stop

; add some others
; 0=black, 1 = white, 255 = white
path(*,0) = [0.,0.,0.]
path(*,1) = [1.,1.,1.]
path(*,2) = [0.,0.,0.5]
path(*,255) = [1.,1.,1.]

; change from path to RGB
red = FIX(path(0,*)*255)
green = FIX(path(1,*)*255)
blue = FIX(path(2,*)*255)

tvlct, red, green , blue

if KEYWORD_SET(SHOW) then begin
  ; Check the number of colors...
  if !d.n_colors EQ 16777216 then begin
    ; 24 bit color
    y = indgen(256)
    plot, y, /NODATA, BACK=red(2) + 256L * (green(2) + 256L * blue(2)), $
	COLOR=red(1) + 256L * (green(1) + 256L * blue(1)), $
	TITLE = '24 Bit Color', $
	YRANGE = [0.,350.], YSTYLE=1, XRANGE=[0.,260.], XSTYLE=1
    for ip=3,254 do begin
      fullcolor = red(ip) + 256L * (green(ip) + 256L * blue(ip))
      for iband = 0, 20 do begin
        oplot, [ip],[y(ip)]+ 4*iband,COLOR=fullcolor, PSYM=4
      end
      oplot, [ip],[red(ip)],COLOR=255, PSYM=4
      oplot, [ip],[green(ip)],COLOR=256L*255, PSYM=6
      oplot, [ip],[blue(ip)],COLOR=255*256L*256L, PSYM=7
    end
  end else begin
    y = indgen(256)
    plot, y, /NODATA, BACK=2, COLOR=1, TITLE = '8 Bit Color', $
	YRANGE = [0.,350.], YSTYLE=1, XRANGE=[0.,260.], XSTYLE=1
    for ip=3,254 do begin
      for iband = 0, 20 do begin
        oplot, [ip],[y(ip)]+ 4*iband,COLOR=ip,PSYM=4
      end
      oplot, [ip],[red(ip)],COLOR=5, PSYM=4
      oplot, [ip],[green(ip)],COLOR=170, PSYM=6
      oplot, [ip],[blue(ip)],COLOR=230, PSYM=7
    end
  end
end

RETURN
END
