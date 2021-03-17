PRO MIN_PITCH_TEMP_WK
; this is a first version to find the minimum temperature at a given pitch
wk_start=cxtime('2010-08-16T00:00:00','cal','sec')
wk_end=cxtime('2010-08-23T00:00:00','cal','sec')

p_range=[45,60,75,90,110,130,145]

files= ["mups"]

for ifile=0,n_elements(files)-1 do begin
  filename="att_"+files(ifile)+"_wk.fits"
  openw,ounit,files(ifile)+"_min_wk.dat",/get_lun
  dat=mrdfits(filename,1)

  b=where(dat.time ge wk_start and dat.time le wk_end,bnum)
  if (bnum gt 0) then dat=dat(b)
  tnames=tag_names(dat)
  for i=1,n_elements(tnames)-1 do begin
    for j=0,n_elements(p_range)-2 do begin
      b=where(dat.pt_suncent_ang ge p_range(j) and dat.pt_suncent_ang le p_range(j+1),bnum)
      if (bnum gt 0) then begin
        printf,ounit,tnames(i),min(dat(b).(i))
      endif
    endfor
  endfor
  free_lun,ounit
endfor

end
