FUNCTION DTREND_READ, in, data, loop_in, LOOP_OUT=loop_out, LABEL=label, $
                      SMOOTH=smooth, LOG_SCALE=log_scale, $
                      GIFROOT=gifroot, SYMB=symb
; this function reads in the data for trended
; input:
; in - the name of a fits file to read
; loop_in - which iteration are we on (the whole point here is
;                                      the some trending requires 
;                                      various filters and several
;                                      passes through the data)
; output:
; returns structure used by dtrend
; loop_out - named variable to return total number of iterations
;            required for in category
; label - named variable to return iteration description (for titles in html)
; smooth - return dsmooth smoothing factor
; log_scale - set to 1 if y axis should be log
; gifroot - if the same tagnames are used through more than one loop
;           you need gifroot to return a label to append to the output
;           plot gif file so other gifs are not overwritten
;
; usually it's one simple mrdfits iteration, but the reason for this function
; is to handle special processing
;
; BDS 28.Mar 2002

; Contents:
;    gratgen ephkey ephrate hrcelec_i hrcelec_s hrcelec_off hrcveto
;    spcelec
;   SCI cpix

; gratgen
if (in eq 'gratgen.fits') then begin
  loop_out = 11
  smooth=30
  symb=1
  case loop_in of
    1: begin
        label=""
        data = mrdfits(in,1)
        return, data
       end
    2: begin
        label="HETG Inserted"
        b=where(data.x4hposaro_avg lt 20,num)
        if (num gt 1) then begin
          a = {grat2, time:0.0,x4hposaro_avg2:0.0,x4hposbro_avg2:0.0}
          data1 = replicate({grat2}, num)
          data1.time = data(b).time
          data1.x4hposaro_avg2 = data(b).x4hposaro_avg
          data1.x4hposbro_avg2 = data(b).x4hposbro_avg
          return, data1
        endif
       end
    3: begin
        label="HETG Retracted"
        b=where(data.x4hposaro_avg gt 60,num)
        if (num gt 1) then begin
          a = {grat3, time:0.0,x4hposaro_avg3:0.0,x4hposbro_avg3:0.0}
          data1 = replicate({grat3}, num)
          data1.time = data(b).time
          data1.x4hposaro_avg3 = data(b).x4hposaro_avg
          data1.x4hposbro_avg3 = data(b).x4hposbro_avg
          return, data1
        endif
       end
    4: begin
        label="LETG Inserted"
        b=where(data.x4lposaro_avg lt 20,num)
        if (num gt 1) then begin
          a = {grat4, time:0.0,x4lposaro_avg4:0.0,x4lposbro_avg4:0.0}
          data1 = replicate({grat4}, num)
          data1.time = data(b).time
          data1.x4lposaro_avg4 = data(b).x4lposaro_avg
          data1.x4lposbro_avg4 = data(b).x4lposbro_avg
          return, data1
        endif
       end
    5: begin
        label="LETG Retracted"
        b=where(data.x4lposaro_avg gt 60,num)
        if (num gt 1) then begin
          a = {grat5, time:0.0,x4lposaro_avg5:0.0,x4lposbro_avg5:0.0}
          data1 = replicate({grat5}, num)
          data1.time = data(b).time
          data1.x4lposaro_avg5 = data(b).x4lposaro_avg
          data1.x4lposbro_avg5 = data(b).x4lposbro_avg
          return, data1
        endif
       end
    6: begin
        label="Gratings At Rest"
        b=where(data.x4mp5av_avg lt 1,num)
        if (num gt 1) then begin
          a = {grat6, time:0.0,x4mp28av_avg6:0.0,x4mp28bv_avg6:0.0, $
                    x4mp5av_avg6:0.0,x4mp5bv_avg6:0.0}
          data1 = replicate({grat6}, num)
          data1.time = data(b).time
          data1.x4mp28av_avg6 = data(b).x4mp28av_avg
          data1.x4mp28bv_avg6 = data(b).x4mp28bv_avg
          data1.x4mp5av_avg6 = data(b).x4mp5av_avg
          data1.x4mp5bv_avg6 = data(b).x4mp5bv_avg
          return, data1
        endif
       end
    7: begin
        label="Gratings In Motion"
        b=where(data.x4mp28av_avg gt 3 and data.x4mp5av_avg gt 3,num)
        if (num gt 1) then begin
          a = {grat7, time:0.0,x4mp28av_avg7:0.0,x4mp28bv_avg7:0.0, $
                  x4mp5av_avg7:0.0,x4mp5bv_avg7:0.0}
          data1 = replicate({grat7}, num)
          data1.time = data(b).time
          data1.x4mp28av_avg7 = data(b).x4mp28av_avg
          data1.x4mp28bv_avg7 = data(b).x4mp28bv_avg
          data1.x4mp5av_avg7 = data(b).x4mp5av_avg
          data1.x4mp5bv_avg7 = data(b).x4mp5bv_avg
          return, data1
        endif
       end
    8: begin
        dtrend_otg
        label="HETG Insertions"
        smooth=180
        data1=mrdfits('hetg_in.fits',1)
        return, data1
       end  
    9: begin
        label="HETG Retractions"
        smooth=180
        data1=mrdfits('hetg_re.fits',1)
        return, data1
       end  
    10: begin
        label="LETG Insertions"
        smooth=180
        data1=mrdfits('letg_in.fits',1)
        return, data1
       end  
    11: begin
        label="LETG Retractions"
        smooth=180
        data1=mrdfits('letg_re.fits',1)
        return, data1
       end  
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif ; if (in eq 'gratgen.fits') then begin

; ephkey
if (in eq 'ephkey.fits') then begin
  loop_out =3 
  log_scale=1
  case loop_in of
    1: begin
        label=""
        data=mrdfits(in,1)
        return, data
       end
    2: begin
        label="Quiescent Radiation (SCE150 < 1e4)"
        b=where(data.SCE150_AVG lt 10000,num)
        if (num gt 1) then begin
          a={ephkey1,time:0.0,scct0_avg2:0.0,sce1300_avg2:0.0,sce150_avg2:0.0, $
                  sce300_avg2:0.0,sce3000_avg2:0.0,sch25gm_avg2:0.0, $
                  sch41gm_avg2:0.0,sch4gm_avg2:0.0,sch8gm_avg2:0.0, $
                  scint_avg2:0.0,scp25gm_avg2:0.0,scp41gm_avg2:0.0, $
                  scp4gm_avg2:0.0,scp8gm_avg2:0.0}
          data1 = replicate({ephkey1}, num)
          data1.time=data(b).time
          data1.scct0_avg2=data(b).scct0_avg
          data1.sce1300_avg2=data(b).sce1300_avg
          data1.sce150_avg2=data(b).sce150_avg
          data1.sce300_avg2=data(b).sce300_avg
          data1.sce3000_avg2=data(b).sce3000_avg
          data1.sch25gm_avg2=data(b).sch25gm_avg
          data1.sch41gm_avg2=data(b).sch41gm_avg
          data1.sch4gm_avg2=data(b).sch4gm_avg
          data1.sch8gm_avg2=data(b).sch8gm_avg
          data1.scint_avg2=data(b).scint_avg
          data1.scp25gm_avg2=data(b).scp25gm_avg
          data1.scp41gm_avg2=data(b).scp41gm_avg
          data1.scp4gm_avg2=data(b).scp4gm_avg
          data1.scp8gm_avg2=data(b).scp8gm_avg
          return, data1
        endif 
       end
    3: begin
        label="High Radiation (SCE150 > 1e4)"
        b=where(data.SCE150_AVG gt 10000,num)
        if (num gt 1) then begin
          a={ephkey2,time:0.0,scct0_avg3:0.0,sce1300_avg3:0.0,sce150_avg3:0.0, $
                  sce300_avg3:0.0,sce3000_avg3:0.0,sch25gm_avg3:0.0, $
                  sch41gm_avg3:0.0,sch4gm_avg3:0.0,sch8gm_avg3:0.0, $
                  scint_avg3:0.0,scp25gm_avg3:0.0,scp41gm_avg3:0.0, $
                  scp4gm_avg3:0.0,scp8gm_avg3:0.0}
          data1 = replicate({ephkey2}, num)
          data1.time=data(b).time
          data1.scct0_avg3=data(b).scct0_avg
          data1.sce1300_avg3=data(b).sce1300_avg
          data1.sce150_avg3=data(b).sce150_avg
          data1.sce300_avg3=data(b).sce300_avg
          data1.sce3000_avg3=data(b).sce3000_avg
          data1.sch25gm_avg3=data(b).sch25gm_avg
          data1.sch41gm_avg3=data(b).sch41gm_avg
          data1.sch4gm_avg3=data(b).sch4gm_avg
          data1.sch8gm_avg3=data(b).sch8gm_avg
          data1.scint_avg3=data(b).scint_avg
          data1.scp25gm_avg3=data(b).scp25gm_avg
          data1.scp41gm_avg3=data(b).scp41gm_avg
          data1.scp4gm_avg3=data(b).scp4gm_avg
          data1.scp8gm_avg3=data(b).scp8gm_avg
          return, data1
        endif
       end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif; if (in eq 'ephkey.fits') then begin

; ephrate
if (in eq 'ephrate.fits') then begin
  loop_out =3 
  log_scale=1
  smooth=90
  case loop_in of
    1: begin
        label=""
        data=mrdfits(in,1)
        return, data
       end
    2: begin
        label="Quiescent Radiation (SCA00 < 1e4)"
        b=where(data.SCA00_AVG lt 10000,num)
        if (num gt 1) then begin
          a={ephrate1,time:0.0,sca00_avg2:0.0, sca01_avg2:0.0, sca02_avg2:0.0, $
                  sca03_avg2:0.0, sca04_avg2:0.0, sca05_avg2:0.0, $
                  scb00_avg2:0.0, scb01_avg2:0.0, scb02_avg2:0.0, $
                  scb04_avg2:0.0, scb05_avg2:0.0, scc0_avg2:0.0, $
                  scct1_avg2:0.0, scct2_avg2:0.0, scct3_avg2:0.0, $
                  scct4_avg2:0.0, scct5_avg2:0.0, scd0_avg2:0.0, $
                  sce0_avg2:0.0, scf0_avg2:0.0, scg0_avg2:0.0, $
                  sch25gr_avg2:0.0, sch25s1_avg2:0.0, sch25s23_avg2:0.0, $
                  sch41gr_avg2:0.0, sch41s1_avg2:0.0, sch41s23_avg2:0.0, $
                  sch4gr_avg2:0.0, sch4s1_avg2:0.0, sch4s23_avg2:0.0, $
                  sch8gr_avg2:0.0, sch8s1_avg2:0.0, sch8s23_avg2:0.0, $
                  scp25gr_avg2:0.0, scp25s_avg2:0.0, scp41gr_avg2:0.0, $
                  scp41s_avg2:0.0, scp4gr_avg2:0.0, scp4s_avg2:0.0, $
                  scp8gr_avg2:0.0, scp8s_avg2:0.0}
          data1 = replicate({ephrate1}, num)
          data1.time=data(b).time
          data1.sca00_avg2=data(b).sca00_avg
          data1.sca01_avg2=data(b).sca01_avg
          data1.sca02_avg2=data(b).sca02_avg
          data1.sca03_avg2=data(b).sca03_avg
          data1.sca04_avg2=data(b).sca04_avg
          data1.sca05_avg2=data(b).sca05_avg
          data1.scb00_avg2=data(b).scb00_avg
          data1.scb01_avg2=data(b).scb01_avg
          data1.scb02_avg2=data(b).scb02_avg
          data1.scb04_avg2=data(b).scb04_avg
          data1.scb05_avg2=data(b).scb05_avg
          data1.scc0_avg2=data(b).scc0_avg
          data1.scct1_avg2=data(b).scct1_avg
          data1.scct2_avg2=data(b).scct2_avg
          data1.scct3_avg2=data(b).scct3_avg
          data1.scct4_avg2=data(b).scct4_avg
          data1.scct5_avg2=data(b).scct5_avg
          data1.scd0_avg2=data(b).scd0_avg
          data1.sce0_avg2=data(b).sce0_avg
          data1.scf0_avg2=data(b).scf0_avg
          data1.scg0_avg2=data(b).scg0_avg
          data1.sch25gr_avg2=data(b).sch25gr_avg
          data1.sch25s1_avg2=data(b).sch25s1_avg
          data1.sch25s23_avg2=data(b).sch25s23_avg
          data1.sch41gr_avg2=data(b).sch41gr_avg
          data1.sch41s1_avg2=data(b).sch41s1_avg
          data1.sch41s23_avg2=data(b).sch41s23_avg
          data1.sch4gr_avg2=data(b).sch4gr_avg
          data1.sch4s1_avg2=data(b).sch4s1_avg
          data1.sch4s23_avg2=data(b).sch4s23_avg
          data1.sch8gr_avg2=data(b).sch8gr_avg
          data1.sch8s1_avg2=data(b).sch8s1_avg
          data1.sch8s23_avg2=data(b).sch8s23_avg
          data1.scp25gr_avg2=data(b).scp25gr_avg
          data1.scp25s_avg2=data(b).scp25s_avg
          data1.scp41gr_avg2=data(b).scp41gr_avg
          data1.scp41s_avg2=data(b).scp41s_avg
          data1.scp4gr_avg2=data(b).scp4gr_avg
          data1.scp4s_avg2=data(b).scp4s_avg
          data1.scp8gr_avg2=data(b).scp8gr_avg
          data1.scp8s_avg2=data(b).scp8s_avg
          return, data1
        endif 
       end
    3: begin
        label="High Radiation (SCA00 > 1e4)"
        b=where(data.SCA00_AVG gt 10000,num)
        if (num gt 1) then begin
          a={ephrate2,time:0.0,sca00_avg3:0.0, sca01_avg3:0.0, sca02_avg3:0.0, $
                  sca03_avg3:0.0, sca04_avg3:0.0, sca05_avg3:0.0, $
                  scb00_avg3:0.0, scb01_avg3:0.0, scb02_avg3:0.0, $
                  scb04_avg3:0.0, scb05_avg3:0.0, scc0_avg3:0.0, $
                  scct1_avg3:0.0, scct2_avg3:0.0, scct3_avg3:0.0, $
                  scct4_avg3:0.0, scct5_avg3:0.0, scd0_avg3:0.0, $
                  sce0_avg3:0.0, scf0_avg3:0.0, scg0_avg3:0.0, $
                  sch25gr_avg3:0.0, sch25s1_avg3:0.0, sch25s23_avg3:0.0, $
                  sch41gr_avg3:0.0, sch41s1_avg3:0.0, sch41s23_avg3:0.0, $
                  sch4gr_avg3:0.0, sch4s1_avg3:0.0, sch4s23_avg3:0.0, $
                  sch8gr_avg3:0.0, sch8s1_avg3:0.0, sch8s23_avg3:0.0, $
                  scp25gr_avg3:0.0, scp25s_avg3:0.0, scp41gr_avg3:0.0, $
                  scp41s_avg3:0.0, scp4gr_avg3:0.0, scp4s_avg3:0.0, $
                  scp8gr_avg3:0.0, scp8s_avg3:0.0}
          data1 = replicate({ephrate2}, num)
          data1.time=data(b).time
          data1.sca00_avg3=data(b).sca00_avg
          data1.sca01_avg3=data(b).sca01_avg
          data1.sca02_avg3=data(b).sca02_avg
          data1.sca03_avg3=data(b).sca03_avg
          data1.sca04_avg3=data(b).sca04_avg
          data1.sca05_avg3=data(b).sca05_avg
          data1.scb00_avg3=data(b).scb00_avg
          data1.scb01_avg3=data(b).scb01_avg
          data1.scb02_avg3=data(b).scb02_avg
          data1.scb04_avg3=data(b).scb04_avg
          data1.scb05_avg3=data(b).scb05_avg
          data1.scc0_avg3=data(b).scc0_avg
          data1.scct1_avg3=data(b).scct1_avg
          data1.scct2_avg3=data(b).scct2_avg
          data1.scct3_avg3=data(b).scct3_avg
          data1.scct4_avg3=data(b).scct4_avg
          data1.scct5_avg3=data(b).scct5_avg
          data1.scd0_avg3=data(b).scd0_avg
          data1.sce0_avg3=data(b).sce0_avg
          data1.scf0_avg3=data(b).scf0_avg
          data1.scg0_avg3=data(b).scg0_avg
          data1.sch25gr_avg3=data(b).sch25gr_avg
          data1.sch25s1_avg3=data(b).sch25s1_avg
          data1.sch25s23_avg3=data(b).sch25s23_avg
          data1.sch41gr_avg3=data(b).sch41gr_avg
          data1.sch41s1_avg3=data(b).sch41s1_avg
          data1.sch41s23_avg3=data(b).sch41s23_avg
          data1.sch4gr_avg3=data(b).sch4gr_avg
          data1.sch4s1_avg3=data(b).sch4s1_avg
          data1.sch4s23_avg3=data(b).sch4s23_avg
          data1.sch8gr_avg3=data(b).sch8gr_avg
          data1.sch8s1_avg3=data(b).sch8s1_avg
          data1.sch8s23_avg3=data(b).sch8s23_avg
          data1.scp25gr_avg3=data(b).scp25gr_avg
          data1.scp25s_avg3=data(b).scp25s_avg
          data1.scp41gr_avg3=data(b).scp41gr_avg
          data1.scp41s_avg3=data(b).scp41s_avg
          data1.scp4gr_avg3=data(b).scp4gr_avg
          data1.scp4s_avg3=data(b).scp4s_avg
          data1.scp8gr_avg3=data(b).scp8gr_avg
          return, data1
        endif
       end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif; if (in eq 'ephrate.fits') then begin

if (in eq 'hrcveto.fits') then begin
  ; hrcveto files must be created correctly to begin with
  ; require hrcveto_hi, for example where si=HRC-I and CORADMEN=ENAB
  ;  also hrcveto_ai, hrcveto_as, and hrcveto_hs
  ;  also hrcveto_rad where CORADMEN=DISA
  loop_out=3 
  log_scale=0
  smooth=30
  case loop_in of
    1: begin
        label="<a name=hrci_on>HRC-I in use</a>"
        symb=2
        a=mrdfits('hrcveto_i.fits',1)
        t2={hrcv1a,time:0.0,shevart_avg1a:0.0,tlevart_avg1a:0.0, $
                  vlevart_avg1a:0.0,tot_valid_avg1a:0.0}
        data1 = replicate({hrcv1a}, n_elements(a))
        data1.time=a.time
        data1.shevart_avg1a=a.shevart_avg
        data1.tlevart_avg1a=a.tlevart_avg
        data1.vlevart_avg1a=a.vlevart_avg
        data1.tot_valid_avg1a=a.tlevart_avg-a.vlevart_avg
        return, data1
       end
    2: begin
        label="<a name=hrcs_on>HRC-S in use</a>"
        symb=2
        a=mrdfits('hrcveto_s.fits',1)
        t2={hrcv1b,time:0.0,shevart_avg1b:0.0,tlevart_avg1b:0.0, $
                  vlevart_avg1b:0.0,tot_valid_avg1b:0.0}
        data1 = replicate({hrcv1b}, n_elements(a))
        data1.time=a.time
        data1.shevart_avg1b=a.shevart_avg
        data1.tlevart_avg1b=a.tlevart_avg
        data1.vlevart_avg1b=a.vlevart_avg
        data1.tot_valid_avg1b=a.tlevart_avg-a.vlevart_avg
        return, data1
       end
    3: begin
        label="<a name=hrc_off>HRC not in use</a>"
        a=mrdfits('hrcveto_ai.fits',1)
        b=mrdfits('hrcveto_as.fits',1)
        c=mrdfits('hrcveto_off.fits',1)
        t2={hrcv2,time:0.0,shevart_avg2:0.0,tlevart_avg2:0.0, $
                  vlevart_avg2:0.0,tot_valid_avg2:0.0}
        data1 = replicate({hrcv2}, n_elements(a)+n_elements(b)+n_elements(c))
        data1.time=[a.time,b.time,c.time]
        data1.shevart_avg2=[a.shevart_avg,b.shevart_avg,c.shevart_avg]
        data1.tlevart_avg2=[a.tlevart_avg,b.tlevart_avg,c.tlevart_avg]
        data1.vlevart_avg2=[a.vlevart_avg,b.vlevart_avg,c.vlevart_avg]
        data1.tot_valid_avg2=data1.tlevart_avg2-data1.vlevart_avg2
        data1=data1(uniq(data1.time,sort(data1.time)))
        return, data1
       end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif; if (in eq 'hrcveto.fits') then begin

if (in eq 'hrcelec_i.fits') then begin
  ; require hrcveto_i, where si=HRC-I and CORADMEN=ENAB
  loop_out=1 
  log_scale=0
  smooth=30
  symb=2
  case loop_in of
    1: begin
        label="<a name=hrci_on>HRC-I in use</a>"
        gifroot="A"
        data1=mrdfits('hrcelec_i.fits',1)
        return, data1
       end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif; if (in eq 'hrcelec_i.fits') then begin

if (in eq 'hrcelec_s.fits') then begin
  ; require hrcveto_s, where si=HRC-S and CORADMEN=ENAB
  loop_out=1 
  log_scale=0
  smooth=30
  symb=2
  case loop_in of
    1: begin
        label="<a name=hrcs_on>HRC-S in use</a>"
        gifroot="B"
        data1=mrdfits('hrcelec_s.fits',1)
        return, data1
       end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif; if (in eq 'hrcelec_s.fits') then begin

if (in eq 'hrcelec_off.fits') then begin
  ; require hrcveto_ai, where si=ACIS-I and CORADMEN=ENAB
  ;         hrcveto_as, where si=ACIS-S and CORADMEN=ENAB
  ;         hrcveto_off, where CORADMEN=DISA
  loop_out=1 
  log_scale=0
  smooth=30
  case loop_in of
    1: begin
        label="<a name=hrc_off>HRC not in use</a>"
        gifroot="C"
        a=mrdfits('hrcelec_ai.fits',1)
        b=mrdfits('hrcelec_as.fits',1)
        c=mrdfits('hrcelec_off.fits',1)
        t2={hrce2,time:0.0, $
              x2detart_avg:0.0, x2detbrt_avg:0.0, calpalv_avg:0.0, $
              cbhuast_avg:0.0, cbhvast_avg:0.0, cbluast_avg:0.0, $
              cblvast_avg:0.0, fcpuast_avg:0.0, fcpvast_avg:0.0, $
              hvpsstat_avg:0.0, imbpast_avg:0.0, imhblv_avg:0.0, $
              imhvlv_avg:0.0, imtpast_avg:0.0, lldialv_avg:0.0, $
              mlswenbl_avg:0.0, mlswstat_avg:0.0, mtrcmndr_avg:0.0, $
              mtritmp_avg:0.0, mtrselct_avg:0.0, mtrstatr_avg:0.0, $
              n15cast_avg:0.0, p15cast_avg:0.0, p24cast_avg:0.0, $
              rsrfalv_avg:0.0, s1hvlv_avg:0.0, s1hvst_avg:0.0, $
              s2hvlv_avg:0.0, s2hvst_avg:0.0, scidpren_avg:0.0, $
              scthast_avg:0.0, spbpast_avg:0.0, sphblv_avg:0.0, $
              sphvlv_avg:0.0, sptpast_avg:0.0, wdthast_avg:0.0}
        data1 = replicate({hrce2}, n_elements(a)+n_elements(b)+n_elements(c))
        data1.time=[a.time,b.time,c.time]
        data1.x2detart_avg=[a.x2detart_avg, b.x2detart_avg, c.x2detart_avg]
        data1.x2detbrt_avg=[a.x2detbrt_avg, b.x2detbrt_avg, c.x2detbrt_avg]
        data1.calpalv_avg=[a.calpalv_avg, b.calpalv_avg, c.calpalv_avg]
        data1.cbhuast_avg=[a.cbhuast_avg, b.cbhuast_avg, c.cbhuast_avg]
        data1.cbhvast_avg=[a.cbhvast_avg, b.cbhvast_avg, c.cbhvast_avg]
        data1.cbluast_avg=[a.cbluast_avg, b.cbluast_avg, c.cbluast_avg]
        data1.cblvast_avg=[a.cblvast_avg, b.cblvast_avg, c.cblvast_avg]
        data1.fcpuast_avg=[a.fcpuast_avg, b.fcpuast_avg, c.fcpuast_avg]
        data1.fcpvast_avg=[a.fcpvast_avg, b.fcpvast_avg, c.fcpvast_avg]
        data1.hvpsstat_avg=[a.hvpsstat_avg, b.hvpsstat_avg, c.hvpsstat_avg]
        data1.imbpast_avg=[a.imbpast_avg, b.imbpast_avg, c.imbpast_avg]
        data1.imhblv_avg=[a.imhblv_avg, b.imhblv_avg, c.imhblv_avg]
        data1.imhvlv_avg=[a.imhvlv_avg, b.imhvlv_avg, c.imhvlv_avg]
        data1.imtpast_avg=[a.imtpast_avg, b.imtpast_avg, c.imtpast_avg]
        data1.lldialv_avg=[a.lldialv_avg, b.lldialv_avg, c.lldialv_avg]
        data1.mlswenbl_avg=[a.mlswenbl_avg, b.mlswenbl_avg, c.mlswenbl_avg]
        data1.mlswstat_avg=[a.mlswstat_avg, b.mlswstat_avg, c.mlswstat_avg]
        data1.mtrcmndr_avg=[a.mtrcmndr_avg, b.mtrcmndr_avg, c.mtrcmndr_avg]
        data1.mtritmp_avg=[a.mtritmp_avg, b.mtritmp_avg, c.mtritmp_avg]
        data1.mtrselct_avg=[a.mtrselct_avg, b.mtrselct_avg, c.mtrselct_avg]
        data1.mtrstatr_avg=[a.mtrstatr_avg, b.mtrstatr_avg, c.mtrstatr_avg]
        data1.n15cast_avg=[a.n15cast_avg, b.n15cast_avg, c.n15cast_avg]
        data1.p15cast_avg=[a.p15cast_avg, b.p15cast_avg, c.p15cast_avg]
        data1.p24cast_avg=[a.p24cast_avg, b.p24cast_avg, c.p24cast_avg]
        data1.rsrfalv_avg=[a.rsrfalv_avg, b.rsrfalv_avg, c.rsrfalv_avg]
        data1.s1hvlv_avg=[a.s1hvlv_avg, b.s1hvlv_avg, c.s1hvlv_avg]
        data1.s1hvst_avg=[a.s1hvst_avg, b.s1hvst_avg, c.s1hvst_avg]
        data1.s2hvlv_avg=[a.s2hvlv_avg, b.s2hvlv_avg, c.s2hvlv_avg]
        data1.s2hvst_avg=[a.s2hvst_avg, b.s2hvst_avg, c.s2hvst_avg]
        data1.scidpren_avg=[a.scidpren_avg, b.scidpren_avg, c.scidpren_avg]
        data1.scthast_avg=[a.scthast_avg, b.scthast_avg, c.scthast_avg]
        data1.spbpast_avg=[a.spbpast_avg, b.spbpast_avg, c.spbpast_avg]
        data1.sphblv_avg=[a.sphblv_avg, b.sphblv_avg, c.sphblv_avg]
        data1.sphvlv_avg=[a.sphvlv_avg, b.sphvlv_avg, c.sphvlv_avg]
        data1.sptpast_avg=[a.sptpast_avg, b.sptpast_avg, c.sptpast_avg]
        data1.wdthast_avg=[a.wdthast_avg, b.wdthast_avg, c.wdthast_avg]
        data1=data1(uniq(data1.time,sort(data1.time)))
        return, data1
       end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif; if (in eq 'hrcelec_off.fits') then begin

if (in eq 'spcelec.fits') then begin
  loop_out=2 
  log_scale=0
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('spcelec.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('elbi_low.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'spcelec.fits') then begin

if (in eq 'cpix') then begin
  cpdir='/data/mta/www/mta_acis_sci_run/Corner_pix'
  loop_out=4 
  log_scale=0
  smooth=30
  symb=2
  case loop_in of
    1: begin
        label="<a name=ccd2>CCD2</a>"
        cpfile='I2cp.dat'
        cp1={cpt1,time:0.0,faint_avg:!VALUES.F_NAN, $
                           vfaint_avg:!VALUES.F_NAN, $
                           afaint_avg:!VALUES.F_NAN}
        gifroot='2'
       end
    2: begin
        label="<a name=ccd3>CCD3</a>"
        cpfile='I3cp.dat'
        gifroot='3'
       end
    3: begin
        label="<a name=ccd6>CCD6</a>"
        cpfile='S2cp.dat'
        gifroot='6'
       end
    4: begin
        label="<a name=ccd7>CCD7</a>"
        cpfile='S3cp.dat'
        gifroot='7'
       end
  endcase
  readcol,cpdir+'/'+cpfile,time,x,cent,x,x,type, $
        format='F,F,F,F,F,A'
  data1 = replicate({cpt1}, n_elements(time))
  data1.time=time
  a=where(type eq 'FAINT')
  b=where(type ne 'FAINT')
  data1(a).faint_avg=cent(a)
  data1(b).faint_avg=sqrt(-1)  ; make those NaN
  a=where(type eq 'VFAINT')
  b=where(type ne 'VFAINT')
  data1(a).vfaint_avg=cent(a)
  data1(b).vfaint_avg=sqrt(-1)  ; make those NaN
  a=where(type eq 'AFAINT')
  b=where(type ne 'AFAINT')
  data1(a).afaint_avg=cent(a)
  data1(b).afaint_avg=sqrt(-1)  ; make those NaN
  ;print,cent(1:10) ;debugg
  ;print,type(1:10) ;debugg
  data1=data1(sort(data1.time))
  return, data1
endif ; if (in eq 'cpix.fits') then begin

if (in eq 'compaciscent.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Computed ACIS Thermal"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ; if (in eq 'compaciscent.fits') then begin

if (in eq 'compacispwr.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Computed ACIS Electronics"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ; if (in eq 'compacispwr.fits') then begin

if (in eq 'compephkey.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Computed EPHIN Key Rates L1"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(3) ne -99)), cols=[0,3,5,7,9])
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ; if (in eq 'compephkey.fits') then begin

if (in eq 'compsimoffsetb.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Computed SIM Thermal"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ; if (in eq 'compsimoffsetb.fits') then begin

if (in eq 'compgradkodak.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Computed HRMA Gradients"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ; if (in eq 'compgradkodak.fits') then begin

; GRAD
if (in eq 'gradablk.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients OBA AFT Bulkhead"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradablk.fits') then begin
if (in eq 'gradahet.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients HRMA AFT Heater Plt."
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradahet.fits') then begin
if (in eq 'gradaincyl.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients OBA AFT Inner Cyl."
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradaincyl.fits') then begin
if (in eq 'gradcap.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients HRMA CAP"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradcap.fits') then begin
if (in eq 'gradfap.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients HRMA FAP"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradfap.fits') then begin
if (in eq 'gradfblk.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients OBA FWD Bulkhead"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradfblk.fits') then begin
if (in eq 'gradhcone.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients OBA Cone"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradhcone.fits') then begin
if (in eq 'gradhhflex.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients HRMA H-Flexure"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradhhflex.fits') then begin
if (in eq 'gradhpflex.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients HRMA P-Flexure"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradhpflex.fits') then begin
if (in eq 'gradhstrut.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients HRMA Struts"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradhstrut.fits') then begin
if (in eq 'gradocyl.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients HSA Outer Cylinder"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradocyl.fits') then begin
if (in eq 'gradpcolb.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients HRMA PreCol. Baffle Plt."
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradpcolb.fits') then begin
if (in eq 'gradperi.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients Periscope"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradperi.fits') then begin
if (in eq 'gradsstrut.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients Spacecraft Struts"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradsstrut.fits') then begin
if (in eq 'gradtfte.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients TFTE"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=data1.time*86400+31536000
        return, data1
       end
  endcase
endif ;if (in eq 'gradtfte.fits') then begin

if (in eq 'sc_main_temp.fits') then begin
  loop_out = 2
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('sc_main_temp1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('sc_main_temp2.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'sc_main_temp.fits') then begin

if (in eq 'spceleca.fits') then begin
  loop_out = 2
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('spceleca1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('spceleca2.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'spceleca.fits') then begin

if (in eq 'spcelecb.fits') then begin
  loop_out = 2
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('spcelecb1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('spcelecb2.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'spcelecb.fits') then begin

if (in eq 'obaheaters.fits') then begin
  loop_out = 2
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('obaheaters1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('obaheaters2.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'sc_main_temp.fits') then begin

if (in eq 'hrmaheaters.fits') then begin
  loop_out = 2
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('hrmaheaters1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('hrmaheaters2.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'sc_main_temp.fits') then begin

if (in eq 'cti') then begin
  loop_out = 10
  case loop_in of
    1: begin
        label="MnKa CCD 0 detrended"
        file='mn_ccd0_det'
        gifroot='mn0'
        cti1={ctit1,time:0.0,node0_avg:!VALUES.F_NAN, $
              node1_avg:!VALUES.F_NAN,node2_avg:!VALUES.F_NAN, $
              node3_avg:!VALUES.F_NAN}
       end
    2: begin
        label="MnKa CCD 1 detrended"
        file='mn_ccd1_det'
        gifroot='mn1'
       end
    3: begin
        label="MnKa CCD 2 detrended"
        file='mn_ccd2_det'
        gifroot='mn2'
       end
    4: begin
        label="MnKa CCD 3 detrended"
        file='mn_ccd3_det'
        gifroot='mn3'
       end
    5: begin
        label="MnKa CCD 4 detrended"
        file='mn_ccd4_det'
        gifroot='mn4'
       end
    6: begin
        label="MnKa CCD 5"
        file='mn_ccd5'
        gifroot='mn5'
       end
    7: begin
        label="MnKa CCD 6 detrended"
        file='mn_ccd6_det'
        gifroot='mn6'
       end
    8: begin
        label="MnKa CCD 7"
        file='mn_ccd7'
        gifroot='mn7'
       end
    9: begin
        label="MnKa CCD 8 detrended"
        file='mn_ccd8_det'
        gifroot='mn8'
       end
    10: begin
        label="MnKa CCD 9 detrended"
        file='mn_ccd9_det'
        gifroot='mn9'
       end
  endcase
  readcol, '/data/mta/Script/CTI/Data/'+file, $
           date,n0,n1,n2,n3,x,x,x, format='A,A,A,A,A,A,A,A'
  num=n_elements(date)
  n0val=fltarr(num)
  n1val=fltarr(num)
  n2val=fltarr(num)
  n3val=fltarr(num)
  for i=0, num-1 do begin
    tmp=strsplit(n0(i),"+",/extract)
    n0val(i)=tmp(0)
    tmp=strsplit(n1(i),"+",/extract)
    n1val(i)=tmp(0)
    tmp=strsplit(n2(i),"+",/extract)
    n2val(i)=tmp(0)
    tmp=strsplit(n3(i),"+",/extract)
    n3val(i)=tmp(0)
  endfor
  data1=replicate({ctit1},num)
  data1.time=cxtime(date,'cal','sec')
  data1.node0_avg=n0val
  data1.node1_avg=n1val
  data1.node2_avg=n2val
  data1.node3_avg=n3val
  return, data1
endif ; if (in eq 'cti') then begin

loop_out = 1
if (keyword_set(smooth)) then begin
  if (smooth lt 0) then smooth=30
endif
label=""
data=mrdfits(in,1)
return, data

end
