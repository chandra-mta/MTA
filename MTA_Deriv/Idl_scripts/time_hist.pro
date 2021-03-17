FUNCTION TIME_HIST, time, val, $
          MIN=min, BINSIZE=binsize, NORMALIZE=normalize, $
          MAX_INT=max_int
; return "cumulative time histogram"
; eg. histogram of TEPHIN vs. time
; - time = time array
; - val = array to histogram against time
; optional parameters:
;   - min = minimum data value to include
;   - binsize = width of hist bins
;   - normalize = return time percentages instead of absolute secs.   
;   - max_int = maximum interval (sec) between data data points to include
;               (to avoid counting large data gaps)
;
; 16. Jan 2003 BDS

max_i=n_elements(val)-2 ; don't use last element 
                        ;  (don't know its duration)

if (NOT keyword_set(min)) then min=fix(min(val(0:max_i)))
max=max(val(0:max_i))
if (NOT keyword_set(binsize)) then binsize=fix((max-min)/10)
if (NOT keyword_set(max_int)) then max_int=max(time)-min(time)

n_bins = fix((max-min)/binsize)+1
if (n_bins le 0) then return, [0]
hist = fltarr(n_bins)
j=0 ; hist indexer
for i=min, max, binsize do begin
  b=where(val(0:max_i) ge i and val(0:max_i) lt i+binsize,num)
  if (num gt 0) then begin
    span=time(b+1)-time(b)
    bspan=where(span le max_int,nspan) ; watch out for large data gaps
    if (nspan gt 0) then hist(j)=total(span(bspan))
  endif ;if (num gt 0) then begin
  j=j+1
endfor ; for i=min, max-binsize, binsize do begin

if (keyword_set(normalize)) then begin
  return, hist/total(hist)
endif else begin
  return, hist
endelse

end
