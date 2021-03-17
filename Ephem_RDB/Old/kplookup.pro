PRO KPLOOKUP, infile
; add kp column to dephem.dat file so we can figure CRM region
; 03/18, no kp data is available for mar 01,2002 - mar 11,2002
;   add this data to archive at end of mar 2002

kp_cur = '/data/mta4/proj/rac/ops/KP/k_index_data'

rdfloat, infile, sarr,px,py,pz,vx,vy,vz,$
                     fyarr,mon,day,hr, $
                     minute,second

year = fix(fyarr)-fix(fyarr/100)*100
cdate=year*10000L+mon*100+day
ctime=hr*10000+minute*100+second
num = n_elements(year)
kp = fltarr(num)
breakdate=070316

; read in lookup tables ****************
b = where(cdate lt breakdate or cdate gt 990000, nold)
if (nold gt 0) then $ ; read in archive
  readcol, kp_arc, date, h0,h3,h6,h9, $
                         h12,h15,h18,h21, format='L,A,A,A,A,A,A,A,A'
b = where(cdate ge breakdate, nnew)
if (nnew gt 0) then begin ; read in current
  readcol, kp_cur,  csec,ckp, format='F,F'
;  b = where(cyr ge 2002, n)
;  if (n gt 0) then begin
;    cyr=cyr(b)
;    cmo=cmo(b)
;    cda=cda(b)
;    ctm=string(ctm(b))
;    ckp=ckp(b)
;    xsec=strcompress(string(fix(cyr))+"-"+string(fix(cmo))+"-"+ $
;                 string(fix(cda))+"T"+ $
;                  strmid(ctm,0,2)+":"+strmid(ctm,2,2) + $
;;                  strmid(ctm,4,2),/remove_all)
;                  ":00",/remove_all)
;    ;print,ctm
;    ;print, xsec
;    csec=cxtime(xsec,'cal','sec')
;  endif ; if (n gt 0) then begin
endif ; if (nnew gt 0) then begin ; read in current

; lookup kp *************
for i = 0L, num - 1 do begin
  kp(i) = 10
  if (cdate(i) lt breakdate or cdate(i) gt 990000) then begin ; look in archive
    b = where(date eq cdate(i),nb)
    if (nb gt 0) then begin
      print,"hr ",hr(i)
      case 1 of
        (hr(i) ge 0) and (hr(i) lt 3): val = h0(b)
        (hr(i) ge 3) and (hr(i) lt 6): val = h3(b)
        (hr(i) ge 6) and (hr(i) lt 9): val = h6(b)
        (hr(i) ge 9) and (hr(i) lt 12): val = h9(b)
        (hr(i) ge 12) and (hr(i) lt 15): val = h12(b)
        (hr(i) ge 15) and (hr(i) lt 18): val = h15(b)
        (hr(i) ge 18) and (hr(i) lt 21): val = h18(b)
        ;(hr(i) ge 21) and (hr(i) lt 24): val = h21(b)
        (hr(i) ge 21): val = h21(b)
      endcase
      kp(i) = float(strmid(val(0),0,1))
      p = strmid(val(0),1,1)
      case p of
        'o': kp(i) = kp(i) + 0.0
        '-': kp(i) = kp(i) - 0.3
        '+': kp(i) = kp(i) + 0.3
      endcase
      if (i lt 10) then print, year(i), cdate(i), hr(i), val, kp(i) ;debug
    endif ; if (nb gt 0) then begin
  
  endif else begin ; look in current data
    b = where(csec lt sarr(i),n)
    if (n gt 0) then kp(i) = ckp(b(n-1))
  endelse
endfor ; for i = 0, num - 1 do begin
outfile = infile+'0'
openw,olun,outfile,/get_lun
for j=0L,num-1 do begin
  printf,olun, sarr(j),px(j),py(j),pz(j),vx(j),vy(j),vz(j),$
               fyarr(j),mon(j),day(j),hr(j), $
               minute(j),second(j),kp(j), $
    format='(7d16.3,f12.6,5(i3),f6.2)'
endfor

end
