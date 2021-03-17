PRO meas_line_angle, part, lam_line, VERBOSE=verbose, $
	CHIPCOORDS=chipcoords, SELP=selp, SELM=selm
;+
; PRO meas_line_angle, part, lam_line, VERBOSE=verbose, $
;	CHIPCOORDS=chipcoords, SELP=selp, SELM=selm
;
; Procedure to use the output of obs_anal that are in
; oa_common to make plots of the events in a specific
; line (or region) in plus and minus orders.
;
; This is useful for measuring the diffraction angle,
; hence the routine's name.
;
; Since effectively monochromatic lines/regions are
; selected, CCD diagnostics can also be performed, e.g.,
; PHA distribution from the events...
;
; REVISIONS
; - - - - -
; 11/01/99 dd Released w/HAK 1.30.
;    ----------------------------------------------------------
;-
@oa_common

; Size of region for selection
reg_size = 10.0 ; pixels
dither_pp = 2.0*8.0*2.0 ; pixels peak-peak

periods = [1.E9, 2000.81, 4001.41, 9912.16]
angles = [0.0, -5.235, 4.725, 0.01]
part_names=['Zero','HEG','MEG','LEG']
angle = angles(part)
period = periods(part)
rcspacing = 8632.48
zo_loc = 256.0

dist = (rcspacing*lam_line/period )/oa_pixel_size

selp = where( (ABS((oa_ax-oa_aveAX)-dist*COS(angle*!DTOR)) $
			LT 0.5*reg_size) AND $
	(ABS((oa_ay-oa_aveAY)-dist*SIN(angle*!DTOR)) $
			LT 0.5*reg_size) )

selm = where( ABS((oa_ax-oa_aveAX) + dist*COS(angle*!DTOR)) $
			LT 0.5*reg_size AND $
	ABS((oa_ay-oa_aveAY) + dist*SIN(angle*!DTOR)) $
			LT 0.5*reg_size )

fpieces = STR_SEP(oa_filename,'/')
last_filename = fpieces(n_elements(fpieces)-1)

title = part_names(part)+' '+STRING(lam_line,FORMAT='(F8.3)')+ $
	' A line,  ' + last_filename

avepX = TOTAL(oa_ax(selp)-oa_aveAX)/n_elements(selp)
chipp = chip_of_dispx(avepX, zo_loc)
avepY = TOTAL(oa_ay(selp)-oa_aveAY)/n_elements(selp)
avepE = TOTAL(oa_Etouse(selp))/n_elements(selp)

avemX = TOTAL(oa_ax(selm)-oa_aveAX)/n_elements(selm)
chipm = chip_of_dispx(avemX, zo_loc)
avemY = TOTAL(oa_ay(selm)-oa_aveAY)/n_elements(selm)
avemE = TOTAL(oa_Etouse(selm))/n_elements(selm)

meas_angle = (avepY - avemY)/(avepX - avemX)
meas_angle = ATAN(meas_angle)/!DTOR

if KEYWORD_SET(VERBOSE) then begin
  print, ''
  print, ' '+title
  print, ''
  print, '    ( '+STRING(!DDHC/lam_line,FORMAT='(F8.4)'),' keV )'
  print, ''
  print, '  Plus-side  Center: ', avepX, avepY
  print, '             Number: ', n_elements(selp)
  print, '    Ave ACIS Energy: ', avepE
  print, '       Energy Ratio: ', avepE/(!DDHC/lam_line)
  print, ''
  print, ' Minus-side  Center: ', avemX, avemY
  print, '             Number: ', n_elements(selm)
  print, '    Ave ACIS Energy: ', avemE
  print, '       Energy Ratio: ', avemE/(!DDHC/lam_line)
  print, ' '
  print, '      Angle: ', meas_angle
  print, '' 
end else begin
  print, chipp+'  '+part_names(part)+'p '+ $
	STRING(lam_line,FORMAT='(F8.3)')+ $
	' A, ' + STRING(!DDHC/lam_line,FORMAT='(F8.4)')+' keV : ', $
	avepX, avepY, n_elements(selp), avepE/(!DDHC/lam_line)
  print, chipm+'  '+part_names(part)+'m '+ $
	STRING(lam_line,FORMAT='(F8.3)')+ $
	' A, ' + STRING(!DDHC/lam_line,FORMAT='(F8.4)')+' keV : ', $
	avemX, avemY, n_elements(selm), avemE/(!DDHC/lam_line)
end


!p.multi=[0,2,2]

plot, oa_ax(selp)-oa_aveAX, oa_ay(selp)-oa_aveAY, PSYM=4, $
	XRANGE=dist*COS(angle*!DTOR)+reg_size*[-0.5,0.5], /XSTYLE, $
	YRANGE=dist*SIN(angle*!DTOR)+reg_size*[-0.5,0.5], /YSTYLE,$
	TITLE=title
oplot, avepX+[-2.0,2.0], avepY+[0.0,0.0]
oplot, avepX+[0.0,0.0], avepY+[-2.0,2.0]

lin_hist, oa_Etouse(selp), 0.0146, bins, counts
plot, bins, counts, $
	XRANGE=(!DDHC/lam_line)*[0.0, 1.5], XSTYLE=1, $
	XTITLE='ACIS Energy (keV)', $
	PSYM=10, TITLE=chipp
oplot, (!DDHC/lam_line)*[1.0,1.0],[0.0,2.0*MAX(counts)], LINESTYLE=1

plot, oa_ax(selm)-oa_aveAX, oa_ay(selm)-oa_aveAY, PSYM=4, $
	XRANGE=-1.0*dist*COS(angle*!DTOR)+reg_size*[-0.5,0.5], /XSTYLE, $
	YRANGE=-1.0*dist*SIN(angle*!DTOR)+reg_size*[-0.5,0.5], /YSTYLE,$
	TITLE=title
oplot, avemX+[-2.0,2.0], avemY+[0.0,0.0]
oplot, avemX+[0.0,0.0], avemY+[-2.0,2.0]

lin_hist, oa_Etouse(selm), 0.0146, bins, counts
plot, bins, counts, $
	XRANGE=(!DDHC/lam_line)*[0.0, 1.5], XSTYLE=1, $
	XTITLE='ACIS Energy (keV)', $
	PSYM=10, TITLE=chipm
oplot, (!DDHC/lam_line)*[1.0,1.0],[0.0,2.0*MAX(counts)], LINESTYLE=1

RETURN
END


