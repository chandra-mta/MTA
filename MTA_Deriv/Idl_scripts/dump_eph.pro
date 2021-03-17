pro dump_eph

eph=mrdfits('eph_L1.fits',1)

openw, OUT, "mk_eph_avg.out", /get_lun
for i=0L,n_elements(eph)-1 do begin
  printf, OUT, eph(i).time,eph(i).sce1300L1_avg, $
                          eph(i).scp4gmL1_avg, $
                          eph(i).scp41gmL1_avg, $
                          eph(i).scintL1_avg, $
              format='(E14.8,4(" ",F12.3))'
endfor
free_lun,OUT
end
