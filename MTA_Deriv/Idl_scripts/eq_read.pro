FUNCTION EQ_READ, froot
; special read sim_eq data from rdb files

if (froot eq 'sim_eq') then begin
  readcol,'/data/mta4/SIM/obsid_sim_all.out', $
      eq_time,obsid_t, $
      obs_time, $
      boxtemp_avg, famtrtemp_avg, $
      psutemp_avg, tscmtrtemp_avg, $
      x3FASEAAT_AVG, x3TRMTRAT_AVG, $
      obs_att,obs_alt, $
      obs_etot, $
      obs_ra,obs_dec,obs_roll,obs_simode, $
      format='f,f,f,f,f,f,f,f,f,f,f,f,f,f,f,a', skipline=1

  m1 = {eq1, time:eq_time(0), $
      boxtemp_avg:0.0, famtrtemp_avg:0.0, $
      psutemp_avg:0.0, tscmtrtemp_avg:0.0, $
      x3FASEAAT_AVG:0.0, x3TRMTRAT_AVG:0.0}
  b=where(eq_time gt 0, bnum)
  data1 = replicate({eq1}, bnum)
  data1.time=eq_time(b)
  data1.boxtemp_avg= boxtemp_avg(b)
  data1.famtrtemp_avg= famtrtemp_avg(b)
  data1.psutemp_avg= psutemp_avg(b)
  data1.tscmtrtemp_avg= tscmtrtemp_avg(b)
  data1.x3FASEAAT_AVG= x3FASEAAT_AVG(b)
  data1.x3TRMTRAT_AVG= x3TRMTRAT_AVG(b)
  data1=data1(uniq(data1.time,sort(data1.time)))
  mwrfits,data1,'sim_eq.fits',/create
  return, data1
endif ; if (froot eq 'mups_1') then begin

end
