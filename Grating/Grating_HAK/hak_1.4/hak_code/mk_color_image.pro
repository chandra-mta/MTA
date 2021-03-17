; Time-stamp: <97/12/26 15:41:38 dph> 
;             MIT Directory: ~dph/h1/ASC/TG/Anal/3color_spec/
;                            /wiwaxia/d4/ASC/lib/IDL
; File: mk_color_image
; Author: D. Huenemoerder
;         Original version: 971226 
;
; (this header is ~dph/libidl/time-stamp-template.el)
; to auto-update the stamp in emacs, put this in your .emacs file:
;      (add-hook 'write-file-hooks 'time-stamp)
;====================================================================

PRO mk_color_image, x, y, xy_bin, color_vector, ONELEVEL=onelevel, $
	image, x_axis, y_axis, rgb_table, LOG_E_COLORS=log_e_colors
;+
; PRO mk_color_image, x, y, xy_bin, color_vector, ONELEVEL=onelevel, $
;	image, x_axis, y_axis, rgb_table, LOG_E_COLORS=log_e_colors
;
; NAME:
; mk_color_image
;
;
; PURPOSE:
;   create an image and color-code it according to the mean of a
;   specified parameter in each x,y bin.
;
;
; CATEGORY:
;   image idsplay
;
;
; CALLING SEQUENCE:
;   mk_color_image, x, y, xy_bin, color_vector, image, x_axis, y_axis, rgb_table
;
; 
; INPUTS:
;   x = [np] =  input vectors to be binned into an image.
;   x = [np] =  input vectors to be binned into an image.
;   xy_bin = [dx,dy] = bin-sizes on x,y for image
;   color_vector = [np] = vector commensurate w/ x,y for calculation
;     of color for x,y bins.
;
;
; OPTIONAL INPUTS:
;    NONE
;
;       
; KEYWORD PARAMETERS:
;    ONELEVEL Sets the fractional intensity that a single-count pixel
;             gets assigned (0.2 is good for printers, 0.5 for screen)
;    /LOG_E_COLORS Fixes the color(keV) mapping going from red to blue
;                 as energy goes 0.1 to 10 keV
;
; OUTPUTS:
;
;   image = [np/xbin,ny/ybin] = x,y binned intensity image
;   x_axis = [np] = x coordinate array for image
;   y_axis = [np] = y coordinate array for image
;   rgb_table = [np,3] = color table, in r,g,b system, encoding
;          <color_vector> in each x,y bin.
;
; OPTIONAL OUTPUTS:
;
;   NONE
;
; COMMON BLOCKS:
;
;  NONE
;
; SIDE EFFECTS:
;
;   NONE
;
; RESTRICTIONS:
;
;   x,y,color_vector must be same lengths and commensurate.
;
;   Saturation is pegged at 1.0.
;   Hue table is set to 0-359.
;
; PROCEDURE:
;   use make_image to form image in x,y, returning axes and
;   reverse_indices.  
;   Use reverse_indices to bin the color_vector into an image.
;   Use x,y image for intensity, use color_vector_image for hue, set
;   saturation to 1, then convert HSV planes to RGB table.
;   Color_quantize to RGB system.
;
;
; EXAMPLE:
;   marx_dir = './marx'
;   yp = read_marx_file(marx_dir+'/ypos.dat')
;   zp = read_marx_file(marx_dir+'/zpos.dat')
;   cvec = read_marx_file(marx_dir+'/energy.dat')
;   mk_color_image, yp, zp,[6,6]*0.024, cvec, /LOG_E_COLORS, ONELEVEL=0.5, $
;     im_out, x_out, y_out, rgb_out
;   window, 2, XSIZE=n_elements(x_out), YSIZE=n_elements(y_out) 
;   tvlct,rgb_out
;   tv,im_out
;
; MODIFICATION HISTORY:
;
;   971226 (dph) original procedure, based on 971212 prototype.
;   980107 (dd) Changed hue range to 0 to 190 degrees (red - blue)
;               and move quickly throught the greens (95-145).
;               Made intensity be log normalized to next-to-max bin,
;               with an offset (ONELEVEL)
;-
   
;;;;;;;;;;;;;;;;;; USAGE string array: ;;;;;;;;;;;;;;;;

u_sarray = [$
     ' PURPOSE:', $
     'mk_color_image, x, y, xy_bin, color_vector, image, x_axis, y_axis, rgb_table', $
     '', $
     'color-code an image according to the mean of a specified parameter in each x,y bin.', $
     'INPUTS:  ', $
     '  x = [np] =  input vectors to be binned into an image.', $
     '  y = [np] =  input vectors to be binned into an image.',$
     '  xy_bin = [dx,dy] = bin-sizes on x,y for image.', $
     '  color_vector = [np] = vector commensurate w/ x,y for calculation of color for x,y bins.', $
     '  ONELEVEL = [optional KEYWORD] = one-count intensity level (0. to 1.)', $
     '  /LOG_E_COLORS = [optional KEYWORD] = fixes keV to color mapping for color_vector', $
     'OUTPUTS:  ', $
     '  image = [(xmax-xmin)/xbin,(ymax-ymin)/ybin] = x,y binned intensity image', $
     '  x_axis = [np] = x coordinate array for image', $
     '  y_axis = [np] = y coordinate array for image', $
     '  rgb_table = [np,3] = color table, in r,g,b system, encoding', $
     '       <color_vector> in each x,y bin.'$
    ]

   np = n_params()
   IF np NE 8 THEN BEGIN
      print, ''
      message, /inf, 'Incorrect number of parameters.'
      print, 'USAGE:  '+ u_sarray, format = '(a)'
      print, ''
      return
   ENDIF
   
   xra = [min(x, max = tmp), tmp]
   yra = [min(y, max = tmp), tmp]
   
   im = make_image(x, y, xra=xra, yra=yra, xbin=xy_bin[0], ybin=xy_bin[1], $
                   xax=x_axis, yax=y_axis, $
                   index_list=idx, reverse_indices=rev_idx)
   ; Report the max and next-to-max counts/pixel in the image
   immax = MAX(im)
   print, ' mk_color_image: max counts/pixel = ', immax
   next_to_max = MAX(im(where(im LT immax)))
   print, ' mk_color_image: next-to-max counts/pixel = ', next_to_max
   
   im_colors = FLOAT(im*0)
   ; color_vector's for ypos,zpos indices used in image:
   if KEYWORD_SET(LOG_E_COLORS) then begin
     ; Color is Logish of energy
     l_colors = ALOG( (1. + color_vector(idx)) < 11.)
   end else begin
     l_colors = color_vector(idx)
   end

   lnz = where(im GT 0)   ;; only need to colorize non-zero intensity image bins
   nlnz = n_elements(lnz)

;   message, /inf, 'Begin making <color_vector> image' ;;;; debug

   FOR ii = 0L, nlnz-1 DO BEGIN  ;;; loop over non-zero image bins

      pixnum = lnz(ii)  ;;; serial bin number

      IF rev_idx(pixnum) NE rev_idx(pixnum+1) THEN BEGIN   
         ;; if there is a contribution (this should always be true
         ;; since we already selected non-zero bins)

         plist = rev_idx( rev_idx(pixnum):rev_idx(pixnum+1)-1 ) ; who contributed?
         
                                ;  IF n_elements(plist) GT 0 THEN
                                ;  BEGIN ; must be true to get here 
         im_colors(pixnum) = TOTAL(FLOAT(l_colors(plist)))/N_ELEMENTS(plist)

      ENDIF ELSE BEGIN
         message,'FATAL error: no contribution to this non-zero bin!'
      ENDELSE
   
   ENDFOR

;   message, /inf, 'Converting color image' ;;;; debug
                                ; make H,S,V planes, then
                                ; color_convert, and color_quan

; HUE
;   im_H = float(im_colors) / max(im_colors) * 359. ; all Hues (0-359).
;dd Just up to ~190: red --> blue (skip purples and back to red)
;   but go through "the greens" more quickly...
;   So scale it 0 to 165, then stretch 95-120 to 95-145 (x2) so 165--> 190
;
;   Optional color=energy_in_keV fixed mapping
if KEYWORD_SET(LOG_E_COLORS) then begin
  maxH = ALOG( 11. )
  minH = 0.0
  im_H = 165.0 * (float(im_colors)-minH) / (maxH-minH)
end else begin
  ; Use the MAX and MIN of im_colors to normalize
  maxH = MAX(im_colors)
  minH = MIN(im_colors(where(im_colors GT 0.0)))
  im_H = 165.0 * (float(im_colors)-minH) / (maxH-minH)
end
  ; Now expand this to 0 to 190
  stretch = 2.*(im_H - 95.)
  stretch = stretch > 0.0
  stretch = stretch < 50.0
  im_H = im_H + stretch

; SATURATION
   im_S = float(im NE 0)        ; "saturation" - make it 1.0 or 0

; INTENSITY                     ; dd's log plus offset
   if 1 EQ 1 then begin
     ; Use offset + normalized Log of counts...
     ;
     ; start with LOG scaling of intensity
     ;  0 counts gives slight negative value
     ;  1 count gives 0.3
     ;  2 counts 0.6
     ;  4 counts 0.9
     ;    ...
     ;  1024 counts 3.3
     ;  etc.
     logim = ALOG10( FLOAT(im) > 0.5 ) + 0.3
     ; log scale the next-to-max also
     lognexttomax = ALOG10( FLOAT(next_to_max) > 0.5 ) + 0.31
     ; Normalize to the next-to-max and
     ; lift all the non-zero ones up a bit so that a single event
     ; will show up 
     ; For printers use ~ 0.2, for screens use 0.5
     IF KEYWORD_SET(ONELEVEL) then begin
       onecountlevel = ((onelevel > 0.) < 1.0)
     end else begin
       onecountlevel = 0.5
     end
     im_V = onecountlevel + (1.-onecountlevel) * (logim/lognexttomax < 1.0)
     ; Put hard zeros at the zero counts locations
     zerocounts = where(logim LT 0.0, nwhere)
     if nwhere GT 0 then im_V(zerocounts) = 0.0
   end else begin
     im_V = float(im)/max(im)     ; "value" - the intensity; 0.0-1.0
     thresh = max(im_V)           ;
     im_V = float(im < thresh) / thresh ; "value" - the intensity; 0.0-1.0
                                ;this clips out a single large spike
                                ;which dominates the intensity scale.
   end

   color_convert, im_H, im_S, im_V, im_r, im_g, im_b, /hsv ; returns r,g,b images.
   imtrue=[ [[im_r]],[[im_g]],[[im_b]]]  

   image = color_quan(imtrue, 3, r, g, b, /dither, colors = 224) ; convert to 8-bit.
   
   rgb_table = [ [r], [g], [b]]


END
   
