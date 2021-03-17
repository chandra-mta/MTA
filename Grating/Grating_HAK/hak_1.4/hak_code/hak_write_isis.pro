PRO hak_write_isis, filename, bin_lo, bin_hi, counts, stat_err, $
	DATAFROM=datafrom, $
	OBJECT=object, INSTRUMENT=instrument, GRATING=grating, $
	EXPOSURE=exposure, TG_M=tg_m, TG_PART=tg_part, $
	TG_SRCID=tg_srcid, XUNIT=xunit
;+
; PRO hak_write_isis, filename, bin_lo, bin_hi, counts, stat_err, $
;	DATAFROM=datafrom, $
;	OBJECT=object, INSTRUMENT=instrument, GRATING=grating, $
;	EXPOSURE=livetime, TG_M=tg_m, TG_PART=tg_part, $
;	TG_SRCID=tg_srcid, XUNIT=xunit
;
; This procedure writes an ASCII ISIS format spectrum file.
;  ARGUMENTS:
;     filename - file for output
;     bin_lo, bin_hi, counts, stat_err  - arrays of values of spectrum
;  KEYWORDS:
;     DATAFROM - String to indicate the source of the data, e.g., calling
;                routine.
;     OBJECT,etc.  - These are values for the corresponding ISIS 
;                    ASCII format keywords.
; See ISIS Manual and web pages for more information on the
; ISIS format and keywords.
;     --------------------------------------------
;      8/8/99 dd Initial version, for ISIS v0.53
;      9/8/99 dd Change TIME(?) to EXPOSURE
;     02/02/2000 dd Changed tg_src_id to tg_srcid, etc.
;     --------------------------------------------
;-

; Open the output file..
OPENW, iu, filename, /GET

; Write the header with keywords if present...

; intro stuff...
printf, iu, '# ISIS ASCII format Spectrum file'
printf, iu, '# created '+SYSTIME()
printf, iu, '# by hak_write_isis.pro'
if n_elements(DATAFROM) GT 0 then begin
  printf, iu, '# data from '+datafrom
end

; For the keywords use STRCOMPRESS to 
; do conversions to string format from whatever the
; intput format is - this allows caller to use string
; or numeric variables for the keywords, e.g.,
; tg_m could be FIX(1) or "1".
;
printf, iu, '#'
if n_elements(OBJECT) GT 0 then begin
  printf, iu, ';     Object  '+STRCOMPRESS(object)
end
if n_elements(INSTRUMENT) GT 0 then begin
  printf, iu, '; Instrument  '+STRCOMPRESS(instrument)
end
if n_elements(GRATING) GT 0 then begin
  printf, iu, ';    Grating  '+STRCOMPRESS(grating)
end
if n_elements(EXPOSURE) GT 0 then begin
  printf, iu, ';   Exposure  '+STRCOMPRESS(exposure)
end
if n_elements(TG_M) GT 0 then begin
  printf, iu, ';       tg_m  '+STRCOMPRESS(tg_m)
end
if n_elements(TG_PART) GT 0 then begin
  printf, iu, ';    tg_part  '+STRCOMPRESS(tg_part)
end
if n_elements(TG_SRCID) GT 0 then begin
  printf, iu, ';  tg_srcid  '+STRCOMPRESS(tg_srcid)
end
if n_elements(XUNIT) GT 0 then begin
  printf, iu, ';      Xunit  '+STRCOMPRESS(xunit)
end
; all done with header
printf, iu, '#'

; print the spectrum values
for ib=0, n_elements(bin_lo)-1 do begin
  printf, iu, STRCOMPRESS(bin_lo(ib)) + STRCOMPRESS(bin_hi(ib)) + $
	STRCOMPRESS(counts(ib)) + STRCOMPRESS(stat_err(ib))
end
close, iu
free_lun, iu

RETURN
END
