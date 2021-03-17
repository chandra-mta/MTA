PRO MAX_PITCH_TEMP
; this is a first version to find the maximum temperature at a given pitch
wk_start=cxtime('2009-04-13T00:00:00','cal','sec')
wk_end=cxtime('2009-04-20T00:00:00','cal','sec')

p_range=[60,75,90,110,130,145]

files= ["acistemp", $
        "batt_temp", $
        "deahk_temp", $
        "ephtv_F", $
        "ephtv", $
        "hrctemp", $
        "mups", $
        "pcadftsgrad", $
        "pcadtemp", $
        "sc_anc_temp1_F", $
        "sc_anc_temp1", $
        "sc_anc_temp2_F", $
        "sc_anc_temp2", $
        "sc_main_temp1a", $
        "sc_main_temp1b", $
        "sc_main_temp2a", $
        "sc_main_temp2b", $
        "simtemp1", $
        "simtemp2", $
        "simtempaux", $
        "precoll", $
        "obfwdbulkhead", $
        "hrmastruts", $
        "hrmatherm", $
        "hrmaheaters1", $
        "hrmaheaters2", $
        "hrmaheaters3", $
        "hrmaheaters4", $
        "obaheaters1", $
        "obaheaters2", $
        "obaheaters3", $
        "obaheaters4"]

for ifile=0,n_elements(files)-1 do begin
  filename=files(ifile)+"_att.fits"
  openw,ounit,files(ifile)+"_pitch_wk.dat",/get_lun
  dat=mrdfits(filename,1)

  b=where(dat.time ge wk_start and dat.time le wk_end,bnum)
  if (bnum gt 0) then dat=dat(b)
  tnames=tag_names(dat)
  for i=1,n_elements(tnames)-1 do begin
    for j=0,n_elements(p_range)-2 do begin
      b=where(dat.pt_suncent_ang ge p_range(j) and dat.pt_suncent_ang le p_range(j+1),bnum)
      if (bnum gt 0) then begin
        printf,ounit,tnames(i),max(dat(b).(i))
      endif
    endfor
  endfor
  free_lun,ounit
endfor

end
