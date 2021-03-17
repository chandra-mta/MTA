PRO FIX_FITS

; need to cut off archive files at some date and start them over if
; data get corrupted

newdat=383788863. ; mar 01,2010

;filelist=['hrmastruts.fits']
;filelist=['acistemp.fits', $
;'aciseleca.fits', $
;'aciselecb.fits', $
;'acismech.fits', $
;'ephtv.fits']
;filelist=['ephtv.fits']
filelist=['hrctemp.fits', $
'hrcelec_i.fits', $
'hrcelec_s.fits', $
'hrcelec_ai.fits', $
'hrcelec_as.fits', $
'hrcelec_off.fits', $
'hrcveto_ai.fits', $
'hrcveto_as.fits', $
'hrcveto_i.fits', $
'hrcveto_s.fits', $
'hrcveto_off.fits', $
;filelist=['hrmatherm.fits', $
;'hrmastruts.fits', $
;'obfwdbulkhead.fits', $
;'precoll.fits']
'simtemp1.fits', $
'simtemp2.fits']

for i=0,n_elements(filelist)-1 do begin
  dat=mrdfits(filelist(i),1)
  b=where(dat.time le newdat)
  mwrfits,dat(b),filelist(i),/create
endfor
end
