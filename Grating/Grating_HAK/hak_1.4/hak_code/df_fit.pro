PRO df_fit,ngauss,x,y,a,rms, sig,yfit
;+
;PRO df_fit,ngauss,x,y,a,rms, sig,yfit
;
; Perform an N-gaussian fit the the data arrays x, y:
;
;     ngauss = 1,2,3 for number of gaussians'
;     x = x-vector'
;     y = y-vector'
;     a = parameters = height,ctr,disp,...,cont'
;     rms = input rms of data (single value for all y,'
;            OR vector of length y)'
;     sig = output array of parameter uncertainties'
;     yfit = output fit y-vector'
;
; The continuum is a fitted constant times the df_continuum
; common variable; this allows a "shaped" continuum to be fit.
;
;   ----------------------------------------------------------
; 11/30/94 dd Modified for array of rms
; 5/30/96 dd add ngauss=-2 option for ghost line
;   ----------------------------------------------------------
;-

@df_common

; Defaults for df_continuum
if(n_elements(df_continuum) EQ 0) then df_continuum = 0.*x+1.0
if(n_elements(df_continuum) EQ 1) then df_continuum = 0.*x+df_continuum
if(n_elements(df_continuum) NE n_elements(x)) then df_continuum = 0.*x+1.0

IF (n_params() NE 7) THEN BEGIN
    print, '     df_fit,ngauss,x,y,a,rms,sig,yfit'
    print, '     ngauss = 1,2,3 for number of gaussians'
    print, '     x = x-vector'
    print, '     y = y-vector'
    print, '     a = parameters = height,ctr,disp,...,cont'
    print, '     rms = input rms of data (single value for all y,'
    print, '            OR vector of length y)'
    print, '     sig = output array of parameter uncertainties'
    print, '     yfit = output fit y-vector'
    return
ENDIF

if ngauss eq 1 then fname="gauss1"
if ngauss eq 2 then fname="gauss2"
if ngauss eq 3 then fname="gauss3"
if ngauss eq -2 then begin
  fname="df_gaussghost"
  if n_elements(df_ghostH) EQ 0 then df_ghostH = 0.1
  if n_elements(df_ghostC) EQ 0 then df_ghostC = 1.05
  if n_elements(df_ghostS) EQ 0 then df_ghostS = 1.03
end

; save ngauss value
df_ngauss = ngauss

;11/30/94 dd Correct weighting: (e.g. rms = SQRT(y) for root-N ...)
w = 0.*y +(1./(rms^2))	; rms can be a scalar of vector
 
yfit=curvefit_dd(x,y,w,a,sigmaa,function_name=fname)
sig = sigmaa

; if ngauss was -2 then add in the ghost peak to the output
if ngauss EQ -2 then begin
  ga = [df_ghostH, df_ghostC, df_ghostS]
  a = [ a(0:2), ga*a(0:2), a(3)]
  sig = [ sig(0:2), ga*sig(0:2), sig(3)]
end

RETURN
END

