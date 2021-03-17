PRO DTREND_OTG

rdb_in = "/data/mta/www/mta_otg/OTG_summary.rdb"

; constants
speryr=31536000
sperday=86400

; need own copy of readcol to read 29 cols, real readcol allows 25
readcol, rdb_in, $
  DIRN,GRATING,START_TIME,START_VCDU,STOP_TIME,STOP_VCDU, $
  N_MOVES,N_LONG,T_LONG,N_SHORT,i4HILSA,i4HRLSA,i4HILSB,i4HRLSB, $
  f4HILSA,f4HRLSA,f4HILSB,f4HRLSB,i4HPOSARO,i4HPOSBRO,f4HPOSARO,f4HPOSBRO, $
  EMF_MIN_LONG,EMF_AVG_LONG,EMF_MAX_LONG,EMF_MIN_SHORT,EMF_AVG_SHORT, $
  EMF_MAX_SHORT,OBC_ERRS, $
  format='A,A,A,F,A,F,F,F,F,F,A,A,A,A,A,A,A,A,F,F,F,F,F,F,F,F,F,F,F', $
  skipline=2
 
print,"Hi dtend_otg" ; dbug

h_in = where(dirn eq 'INSR' and grating eq 'HETG')
h_re = where(dirn eq 'RETR' and grating eq 'HETG')
l_in = where(dirn eq 'INSR' and grating eq 'LETG')
l_re = where(dirn eq 'RETR' and grating eq 'LETG')

yr = strmid(start_time,0,4)
doy = strmid(start_time,4,3)
hr = strmid(start_time,8,2)
min = strmid(start_time,10,2)
sec = strmid(start_time,12,2)

time = cxtime(yr+":"+doy+":"+hr+":"+min+":"+sec, 'doy','sec')

li = {litab, time:0.0, N_MOVES_LI_AVG: 0, N_LONG_LI_AVG:0, T_LONG_LI_AVG:0.0, $
          N_SHORT_LI_AVG:0, $
          i4HPOSARO_LI_AVG:0.0, i4HPOSBRO_LI_AVG:0.0, $
          f4HPOSARO_LI_AVG:0.0,f4HPOSBRO_LI_AVG:0.0, $
          EMF_MIN_LONG_LI_AVG:0.0,EMF_AVG_LONG_LI_AVG:0.0, $
          EMF_MAX_LONG_LI_AVG:0.0, $
          EMF_MIN_SHORT_LI_AVG:0.0,EMF_AVG_SHORT_LI_AVG:0.0, $
          EMF_MAX_SHORT_LI_AVG:0.0, $
          OBC_ERRS_LI_AVG:0}
lr = {lrtab, time:0.0, N_MOVES_LR_AVG: 0, N_LONG_LR_AVG:0, T_LONG_LR_AVG:0.0, $
          N_SHORT_LR_AVG:0, $
          i4HPOSARO_LR_AVG:0.0, i4HPOSBRO_LR_AVG:0.0, $
          f4HPOSARO_LR_AVG:0.0,f4HPOSBRO_LR_AVG:0.0, $
          EMF_MIN_LONG_LR_AVG:0.0,EMF_AVG_LONG_LR_AVG:0.0, $
          EMF_MAX_LONG_LR_AVG:0.0, $
          EMF_MIN_SHORT_LR_AVG:0.0,EMF_AVG_SHORT_LR_AVG:0.0, $
          EMF_MAX_SHORT_LR_AVG:0.0, $
          OBC_ERRS_LR_AVG:0}

; don't include short move info for hetg moves
hi = {hitab, time:0.0, N_LONG_HI_AVG:0, T_LONG_HI_AVG:0.0, $
          i4HPOSARO_HI_AVG:0.0, i4HPOSBRO_HI_AVG:0.0, $
          f4HPOSARO_HI_AVG:0.0,f4HPOSBRO_HI_AVG:0.0, $
          EMF_MIN_LONG_HI_AVG:0.0,EMF_AVG_LONG_HI_AVG:0.0, $
          EMF_MAX_LONG_HI_AVG:0.0, $
          OBC_ERRS_HI_AVG:0}
hr = {hrtab, time:0.0, N_LONG_HR_AVG:0, T_LONG_HR_AVG:0.0, $
          i4HPOSARO_HR_AVG:0.0, i4HPOSBRO_HR_AVG:0.0, $
          f4HPOSARO_HR_AVG:0.0,f4HPOSBRO_HR_AVG:0.0, $
          EMF_MIN_LONG_HR_AVG:0.0,EMF_AVG_LONG_HR_AVG:0.0, $
          EMF_MAX_LONG_HR_AVG:0.0, $
          OBC_ERRS_HR_AVG:0}

hetg_in = replicate({hitab}, n_elements(h_in))
hetg_re = replicate({hrtab}, n_elements(h_re))
letg_in = replicate({litab}, n_elements(l_in))
letg_re = replicate({lrtab}, n_elements(l_re))

letg_in.time = time(l_in)
letg_in.N_MOVES_LI_AVG = N_MOVES(l_in)
letg_in.N_LONG_LI_AVG = N_LONG(l_in)
letg_in.T_LONG_LI_AVG = T_LONG(l_in)
letg_in.N_SHORT_LI_AVG = N_SHORT(l_in)
letg_in.i4HPOSARO_LI_AVG = i4HPOSARO(l_in)
letg_in.i4HPOSBRO_LI_AVG = i4HPOSBRO(l_in)
letg_in.f4HPOSARO_LI_AVG = f4HPOSARO(l_in)
letg_in.f4HPOSBRO_LI_AVG = f4HPOSBRO(l_in)
letg_in.EMF_MIN_LONG_LI_AVG = EMF_MIN_LONG(l_in)
letg_in.EMF_AVG_LONG_LI_AVG = EMF_AVG_LONG(l_in)
letg_in.EMF_MAX_LONG_LI_AVG = EMF_MAX_LONG(l_in)
letg_in.EMF_MIN_SHORT_LI_AVG = EMF_MIN_SHORT(l_in)
letg_in.EMF_AVG_SHORT_LI_AVG = EMF_AVG_SHORT(l_in)
letg_in.EMF_MAX_SHORT_LI_AVG = EMF_MAX_SHORT(l_in)
letg_in.OBC_ERRS_LI_AVG = OBC_ERRS(l_in)

letg_re.time = time(l_re)
letg_re.N_MOVES_LR_AVG = N_MOVES(l_re)
letg_re.N_LONG_LR_AVG = N_LONG(l_re)
letg_re.T_LONG_LR_AVG = T_LONG(l_re)
letg_re.N_SHORT_LR_AVG = N_SHORT(l_re)
letg_re.i4HPOSARO_LR_AVG = i4HPOSARO(l_re)
letg_re.i4HPOSBRO_LR_AVG = i4HPOSBRO(l_re)
letg_re.f4HPOSARO_LR_AVG = f4HPOSARO(l_re)
letg_re.f4HPOSBRO_LR_AVG = f4HPOSBRO(l_re)
letg_re.EMF_MIN_LONG_LR_AVG = EMF_MIN_LONG(l_re)
letg_re.EMF_AVG_LONG_LR_AVG = EMF_AVG_LONG(l_re)
letg_re.EMF_MAX_LONG_LR_AVG = EMF_MAX_LONG(l_re)
letg_re.EMF_MIN_SHORT_LR_AVG = EMF_MIN_SHORT(l_re)
letg_re.EMF_AVG_SHORT_LR_AVG = EMF_AVG_SHORT(l_re)
letg_re.EMF_MAX_SHORT_LR_AVG = EMF_MAX_SHORT(l_re)
letg_re.OBC_ERRS_LR_AVG = OBC_ERRS(l_re)

hetg_in.time = time(h_in)
hetg_in.N_LONG_HI_AVG = N_LONG(h_in)
hetg_in.T_LONG_HI_AVG = T_LONG(h_in)
hetg_in.i4HPOSARO_HI_AVG = i4HPOSARO(h_in)
hetg_in.i4HPOSBRO_HI_AVG = i4HPOSBRO(h_in)
hetg_in.f4HPOSARO_HI_AVG = f4HPOSARO(h_in)
hetg_in.f4HPOSBRO_HI_AVG = f4HPOSBRO(h_in)
hetg_in.EMF_MIN_LONG_HI_AVG = EMF_MIN_LONG(h_in)
hetg_in.EMF_AVG_LONG_HI_AVG = EMF_AVG_LONG(h_in)
hetg_in.EMF_MAX_LONG_HI_AVG = EMF_MAX_LONG(h_in)
hetg_in.OBC_ERRS_HI_AVG = OBC_ERRS(h_in)

hetg_re.time = time(h_re)
hetg_re.N_LONG_HR_AVG = N_LONG(h_re)
hetg_re.T_LONG_HR_AVG = T_LONG(h_re)
hetg_re.i4HPOSARO_HR_AVG = i4HPOSARO(h_re)
hetg_re.i4HPOSBRO_HR_AVG = i4HPOSBRO(h_re)
hetg_re.f4HPOSARO_HR_AVG = f4HPOSARO(h_re)
hetg_re.f4HPOSBRO_HR_AVG = f4HPOSBRO(h_re)
hetg_re.EMF_MIN_LONG_HR_AVG = EMF_MIN_LONG(h_re)
hetg_re.EMF_AVG_LONG_HR_AVG = EMF_AVG_LONG(h_re)
hetg_re.EMF_MAX_LONG_HR_AVG = EMF_MAX_LONG(h_re)
hetg_re.OBC_ERRS_HR_AVG = OBC_ERRS(h_re)

; write out fits files
mwrfits, letg_in, 'letg_in.fits', /create
mwrfits, letg_re, 'letg_re.fits', /create
mwrfits, hetg_in, 'hetg_in.fits', /create
mwrfits, hetg_re, 'hetg_re.fits', /create

end
