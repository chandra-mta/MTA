PRO DTREND, inlist, SIG=sig
; make trending and derivative plots
; use mta_db (must have /home/brad/IDL in IDL_PATH)
; input:
;     inlist - file containing list of
;              dataseeker msids and smoothing factors (number
;              of days to smooth over)
;           ie.  _elbv_avg 30
;                _elbi_avg 30
;     sig - filter out any data more than sig sigma from mean (default 3)

if (NOT keyword_set(sig)) then sig=3

readcol, inlist, msid, wsmooth, format='A,F'

!p.multi = [0,1,2,0,0]
for i = 0, n_elements(msid)-1 do begin
  data=mta_db_get(ter_cols=string("'"+msid+"'"))
  keys=tag_names(data)
  for j = 1, n_elements(keys)-1 do begin
    m = moment(data.(keys(j)))
    b = where(abs(data.(keys(j)) - m(0)) lt sqrt(m(1))*sig)
    plot, data(b).time, data(b).(keys(j)), psym=1
    if (wsmooth gt 0) then begin
      dv = dsmooth(data(b).time, data(b).(keys(j)), fit=df, w=wsmooth)
    endif else begin
      dv = dsmooth(data(b).time, data(b).(keys(j)), fit=df)
    endelse
    oplot, data(b).time, df
    plot, data(b).time, dv
  endfor ;for j = 1, n_elements(keys)-1 do begin
endfor ;for i = 0, n_elements(msid)-1 do begin

end
