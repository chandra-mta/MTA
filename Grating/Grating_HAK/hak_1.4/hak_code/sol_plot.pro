PRO sol_plot, sol_file, FRAME_TIME=frame_time, RAND_AMP=rand_amp, $
	PIXEL_SIZE=pixel_size, FTIME_MIN=ftime_min, FTIME_MAX=ftime_max, $
	TITLE_IN=title_in
;+
; PRO sol_plot, sol_file, FRAME_TIME=frame_time, RAND_AMP=rand_amp, $
;	PIXEL_SIZE=pixel_size, FTIME_MIN=ftime_min, FTIME_MAX=ftime_max, $
;	TITLE_IN=title_in
;
; Plot the aspect solution mod one-pixel to see induced sub-structure
; and effects of randomization.
;
; sol_file is an "osol" or "asol" aspect solution file.
;
;      ---------------------------------
; Initial version 8/26/99 dd
;      ---------------------------------
;-

if n_elements(sol_file) LE 0 then begin
  doc_library, 'sol_plot'
  RETURN
end

if n_elements(pixel_size) LE 0 then pixel_size = 0.024 ; mm
if n_elements(frame_time) LE 0 then frame_time = 3.3 ; sec
if n_elements(rand_amp) LE 0 then rand_amp = 0.5   ; pixel
if n_elements(ftime_min) LE 0 then ftime_min = 0.0
if n_elements(ftime_max) LE 0 then ftime_max = -1.0 ; all the time
if n_elements(title_in) LE 0 then title_in = 'Aspect Solution'

; Read in the aspect solution
sol = mrdfits(sol_file,1)
; show the tags (column) names
print, tag_names(sol)

; Create the time within the file
start_time = MIN(sol.time)
ftime = sol.time - start_time

; Plot the things we care about
!p.multi=[0,1,5]
plot, ftime, sol.RA
plot, ftime, sol.DEC
plot, ftime, sol.ROLL
plot, ftime, sol.DY
plot, ftime, sol.DZ
wait, 2.0
;;lklkl

print, ''
print, ' Solution file: '+sol_file
print, ''
print, ' Start time = ', start_time
print, ' Time span = ', MAX(ftime)
print, ' Solution delta-t = ', ftime(1)-ftime(0)
print, ''
print, ' pixel_size = ', pixel_size
print, ' frame_time = ', frame_time
print, ' rand_amp = ', rand_amp
print, ' ftime_min = ', ftime_min
print, ' ftime_max = ', ftime_max
print, ''
print, ' Selected time range =', ftime_min, ftime_max
print, ''

; Select a time range
if ftime_max LT 0.0 then ftime_max = MAX(ftime)
sel = where(ftime GT ftime_min AND ftime LT ftime_max)
sol = sol(sel)
ftime = sol.time - MIN(sol.time)

RAave = TOTAL(sol.RA)/n_elements(sel)
DECave = TOTAL(sol.DEC)/n_elements(sel)
ROLLave = TOTAL(sol.ROLL)/n_elements(sel)

print, ' Average values:'
print, '   RA ave = ', RAave
print, '   DEC ave = ', DECave
print, '   ROLL ave = ', ROLLave


RAtouse = sol.RA - RAave
DECtouse = sol.DEC - DECave
DYtouse = sol.DY
DZtouse = sol.DZ

; convert RA and DEC to mm in focal plane
fl = 10061.62 ; mm
DECtouse = fl * DECtouse*!DTOR
RAtouse = fl*COS(DECave*!DTOR) * RAtouse*!DTOR

; Rotate by "- ROLLave" degrees to be in detector coord.s
if n_elements(rot_angle) EQ 0 then rot_angle = -1.0 * ROLLave
print, ''
print, ' rot_angle = ',rot_angle
print, ''
sinr = SIN(!DTOR*rot_angle)
cosr = COS(!DTOR*rot_angle)
RAr = cosr*(RAtouse) - sinr*(DECtouse)
DECr = sinr*(RAtouse) + cosr*(DECtouse)

; and add in the DY and DZ motions
RAr = RAr + DYtouse
DECr = DECr + DZtouse

; Values are in mm in detector system now.
;;plot, RAr, DECr, PSYM=3, $
;;	TITLE='Aspect Solution in Dectector Coord.s', $
;;	XTITLE='Y_Chandra (mm)', YTITLE='Z_Chandra (mm)', $
;;	CHARSIZE = thischarsize

; Pick the times for events to arrive
etime = frame_time*FLOAT( lindgen(FIX(MAX(ftime)/frame_time)) )
print, ''
print, ' Total events = ', n_elements(etime)
print, ''

RAe = INTERPOL_SORT(RAr, ftime, etime)
DECe = INTERPOL_SORT(DECr, ftime, etime)

; Use the event values in following
RAr = RAe
DECr = DECe

!p.multi=[0,2,2]
thischarsize = 1.2

; Convert to pixels
Xmotion = RAr/pixel_size
Ymotion = DECr/pixel_size

; Offset by min value so all are positive
mXmotion = Xmotion - FIX(min(Xmotion))+1.5
mYmotion = Ymotion - FIX(min(Ymotion))+1.5

plot, mXmotion, mYmotion, PSYM=3, $
	TITLE=title_in, $
	XTITLE='Y_Chandra (pixel)', YTITLE='Z_Chandra (pixel)', $
	CHARSIZE = thischarsize

; Form the value mod one pixel
mXmotion = mXmotion - FIX(mXmotion)
mYmotion = mYmotion - FIX(mYmotion)

; Plot it
plot, mXmotion, mYmotion, PSYM=3, $
	TITLE='Events mod One Pixel ('+ $
		STRING(pixel_size,FORMAT='(F5.3)')+' mm)', $
	XTITLE='Y_Chandra (pixel)', YTITLE='Z_Chandra (pixel)', $
	CHARSIZE = thischarsize, $
	XRANGE=[0.0, 1.0], YRANGE=[0.0, 1.0], $
	XSTYLE=1, YSTYLE=1

; Plot 3x3 pixels to help see pattern repeat
plot, mXmotion, mYmotion, PSYM=3, $
	TITLE='mod One Pixel: 3x3 pixels', $
	XTITLE='Y_Chandra (pixel)', YTITLE='Z_Chandra (pixel)', $
	CHARSIZE = thischarsize, $
	XRANGE=[-0.5, 3.5], YRANGE=[-0.5, 3.5], $
	XSTYLE=1, YSTYLE=1
; plot the other 8 "pixels":
xoff = [1.0,2.0,0.0,1.0,2.0,0.0,1.0,2.0]
yoff = [0.0,0.0,1.0,1.0,1.0,2.0,2.0,2.0]
for ip=0,n_elements(xoff)-1 do begin
  oplot, mXmotion+xoff(ip), mYmotion+yoff(ip), PSYM=3
end

; add randomization
rXmotion = mXmotion + rand_amp*2.0*(RANDOMU(SEED,n_elements(mXmotion)) - 0.5)
rYmotion = mYmotion + rand_amp*2.0*(RANDOMU(SEED,n_elements(mYmotion)) - 0.5)

plot, rXmotion, rYmotion, PSYM=3, $
	TITLE='3x3 pixels plus Randomization (+/-'+$
		STRING(rand_amp,FORMAT='(F4.2)')+')', $
	XTITLE='Y_Chandra (pixel)', YTITLE='Z_Chandra (pixel)', $
	CHARSIZE = thischarsize, $
	XRANGE=[-0.5, 3.5], YRANGE=[-0.5, 3.5], $
	XSTYLE=1, YSTYLE=1
; plot the other 8 "pixels":
xoff = [1.0,2.0,0.0,1.0,2.0,0.0,1.0,2.0]
yoff = [0.0,0.0,1.0,1.0,1.0,2.0,2.0,2.0]
for ip=0,n_elements(xoff)-1 do begin
  rXmotion = mXmotion + rand_amp*2.0*(RANDOMU(SEED,n_elements(mXmotion)) - 0.5)
  rYmotion = mYmotion + rand_amp*2.0*(RANDOMU(SEED,n_elements(mYmotion)) - 0.5)
  oplot, rXmotion+xoff(ip), rYmotion+yoff(ip), PSYM=3
end

if 1 EQ 0 then begin
; Projection of a single pixel to the X and Y axes
lin_hist, rXmotion, 0.05, bins, counts
plot, bins, counts, PSYM=10, $
	XRANGE=[-0.5,1.5], XSTYLE=1, $
	TITLE='Y One-pixel 1-D Projection', $
	XTITLE='Y_Chandra (pixel)', $
	YTITLE='counts/bin', $
	CHARSIZE = thischarsize

lin_hist, rYmotion, 0.05, bins, counts
plot, bins, counts, PSYM=10, $
	XRANGE=[-0.5,1.5], XSTYLE=1, $
	TITLE='Z One-pixel 1-D Projection', $
	XTITLE='Z_Chandra (pixel)', $
	YTITLE='counts/bin', $
	CHARSIZE = thischarsize
end

RETURN
END





