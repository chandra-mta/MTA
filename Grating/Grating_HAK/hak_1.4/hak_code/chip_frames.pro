PRO chip_frames
;+
; PRO chip_frames
;
; This procedure looks at the EXPNO values in the structure
; oa_evts in oa_common and creates output and plots for
; each chip showing where EXPNO values are missing.
;
; Using the poisson distribution, an estimate of the number
; of expected number of frames with one or more counts
; is given; the poisson rate is determined from total events over
; MAX(EXPNO)-MIN(EXPNO).  If this estimate agrees with the
; observed number of frames, then there were
; probably no dropped frames.
;
; This is a stand-alone version of the code in obs_anal
; for EXPNO checking...  Run it stand-alone by reading the
; Level 1 event file into the oa_evts common variable:
;
;  hak> oa_evts = mrdfits('acisf120_000N001_evt1.fits',1)
;  hak> chip_frames
;
; - - -
; 1999-11-03 dd original version
;    ------------------------------------------------------
;-
@oa_common

!p.multi=[0,2,6]

print, '       Exposures and Events per Chip (w/selections)'
print, ''
print, '           MIN(EXPNO)  MAX(EXPNO)   TotalEvents   TotalExps  ' + $
	' PoissExps *      Ratio'

for iccd=0,9 do begin
  strccdno = STRING(iccd,FORMAT='(I1)')
  sN = where(oa_evts.ccd_id EQ iccd, nfound)
  if nfound GT 0 then begin
    expno = oa_evts(sN).expno
    uexp = expno(uniq(expno,SORT(expno)))
    ; event rate over all frames
    evts_per_frame = FLOAT(nfound)/FLOAT(MAX(uexp)-MIN(uexp))
    ; poisson distribution for this rate (just 0 rate)
    poiss_dist = poiss_f(evts_per_frame, 0)
    expected_frames = (1.0 - poiss_dist(0))*FLOAT(MAX(uexp)-MIN(uexp))
    expno_ratio = FLOAT(n_elements(uexp))/expected_frames
    print, ' CCD '+strccdno+ $
	' : ',MIN(uexp), MAX(uexp), nfound, n_elements(uexp), $
	expected_frames, expno_ratio

    lin_hist, uexp, 10.0, bins, counts
    plot, bins, counts, PSYM=4, YRANGE=[-1.0,11.0],YSTYLE=1, $
	TITLE='CCD '+STRING(iccd,FORMAT='(I1)') + $
		', ratio = '+STRING(expno_ratio), $
	XTITLE='EXPNO value', YTITLE='N-out-of-10', $
	CHARSIZE=1.5

    lin_hist, expno, 10.0, evtbins, evtcounts
    plot, evtbins, evtcounts, PSYM=4, $
	TITLE='CCD '+STRING(iccd,FORMAT='(I1)') + $
		', Ave event rate = '+ $
		STRING(Float(nfound)/n_elements(uexp), FORMAT='(F8.3)') + $
		' / frame', $
	XTITLE='EXPNO value', YTITLE='Events-per-10-EXPNOs', $
	CHARSIZE=1.5

  end else begin
    print, ' CCD '+strccdno+ ' : '
  end
end
print, ''
print, '    * Expected number of exposures with one or more'
print, '      detected events, assuming no telemetry-limit-dropped'
print, '      exposures for this CCD.'
print, ''

!p.multi=0

RETURN
END
