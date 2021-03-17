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

; temporary runs of compgradkodak
if (in eq 'hrma2006.fits') then begin
  loop_out = 1
  gifroot='2006'
  label='2006'
  data = mrdfits(in,1)
  return, data
endif ; 
if (in eq 'hrma2006_6mo.fits') then begin
  loop_out = 1
  gifroot='2006b'
  label="Jul - Dec 2006"
  data = mrdfits(in,1)
  return, data
endif ; 
if (in eq 'hrma2006_3mo.fits') then begin
  loop_out = 1
  gifroot='2006c'
  label='Aug - Nov 2006'
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'hrma_comp_ohr.fits') then begin
  loop_out = 1
  gifroot='C'
  label=''
  data = mrdfits(in,1)
  return, data
endif ; if (in eq ' hrma_comp_ohr.fits') then begin
if (in eq 'hrma_comp_oob.fits') then begin
  loop_out = 1
  gifroot='C'
  label=''
  data = mrdfits(in,1)
  return, data
endif ; if (in eq ' hrma_comp_oob.fits') then begin

if (in eq 'sim_eq.fits') then begin
  loop_out = 1
  gifroot='S'
  label='Equilibrium Temperatures'
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'acis_eq.fits') then begin
  loop_out=7 
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('acis_eq.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('acis2_eq.fits',1)
        return, data1
       end
    3: begin
        label=""
        data1=mrdfits('acis3_eq.fits',1)
        return, data1
       end
    4: begin
        label=""
        data1=mrdfits('acis4_eq.fits',1)
        return, data1
       end
    5: begin
        label=""
        data1=mrdfits('acis5_eq.fits',1)
        return, data1
       end
    6: begin
        label=""
        data1=mrdfits('acis6_eq.fits',1)
        return, data1
       end
    7: begin
        label=""
        data1=mrdfits('acis9_eq.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'acis_eq.fits') then begin
if (in eq 'acis_eq_100k.fits') then begin
  loop_out=7 
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('acis_eq_100k.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('acis2_eq_100k.fits',1)
        return, data1
       end
    3: begin
        label=""
        data1=mrdfits('acis3_eq_100k.fits',1)
        return, data1
       end
    4: begin
        label=""
        data1=mrdfits('acis4_eq_100k.fits',1)
        return, data1
       end
    5: begin
        label=""
        data1=mrdfits('acis5_eq_100k.fits',1)
        return, data1
       end
    6: begin
        label=""
        data1=mrdfits('acis6_eq_100k.fits',1)
        return, data1
       end
    7: begin
        label=""
        data1=mrdfits('acis9_eq_100k.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'acis_eq.fits') then begin

; acistemp_sa (acis temps separated by solor angle
if (in eq 'acistemp_sa.fits') then begin
  loop_out=3
  case loop_in of
    1: begin
         label="deg 45 < Sun angle < 60"
         gifroot="SA1"
         data = mrdfits(in,1)
         b = where(data.pt_suncent_ang ge 45 and data.pt_suncent_ang le 60)
         return, data(b)
       end
    2: begin
         label="deg 75 < Sun angle < 105"
         gifroot="SA2"
         data = mrdfits(in,1)
         b = where(data.pt_suncent_ang gt 75 and data.pt_suncent_ang le 105)
         return, data(b)
       end
    3: begin
         label="Sun angle > 165 deg"
         gifroot="SA3"
         data = mrdfits(in,1)
         b = where(data.pt_suncent_ang ge 165)
         return, data(b)
       end
    ;1: begin
    ;     label="deg 45 < Solar angle < 60"
    ;     gifroot="SA1"
    ;     data = mrdfits(in,1)
    ;     b = where(data.AOSARES1 ge 45 and data.AOSARES1 le 60)
    ;     return, data(b)
    ;   end
    ;2: begin
    ;     label="deg 60 < Solar angle < 105"
    ;     gifroot="SA2"
    ;     b = where(data.AOSARES1 gt 60 and data.AOSARES1 le 105)
    ;     return, data(b)
    ;   end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif ; if (in eq 'acistemp_sa.fits') then begin
       
; sun angle vs. acis temp
if (in eq 'acistemp_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'acistemp_att.fits') then begin

; altitude vs. acis temp
if (in eq 'acistemp_alt.fits') then begin
  loop_out = 1
  gifroot="L"
  label="vs. Altitude"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'acistemp_att.fits') then begin

; sun angle vs. dea temp
if (in eq 'deahk_temp_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'acistemp_att.fits') then begin

; altitude vs. dea temp
if (in eq 'deahk_temp_alt.fits') then begin
  loop_out = 1
  gifroot="L"
  label="vs. Altitude"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'acistemp_att.fits') then begin

; sun angle vs. ephin temp
if (in eq 'ephtv_att.fits') then begin
  loop_out = 1
  gifroot="P"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'ephtv_att.fits') then begin
if (in eq 'ephtv_F_att.fits') then begin
  loop_out = 1
  gifroot="P"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'ephtv_att.fits') then begin
if (in eq 'pcadtemp_att_F.fits') then begin
  loop_out = 1
  gifroot="P"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'ephtv_att.fits') then begin
if (in eq 'pcadftsgrad_att_F.fits') then begin
  loop_out = 1
  gifroot="P"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'ephtv_att.fits') then begin

if (in eq 'sc_anc_temp_F_att.fits') then begin
  loop_out = 2
  smooth=30
  gifroot="P"
  label="vs. Sun Angle"
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('sc_anc_temp1_F_att.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('sc_anc_temp2_F_att.fits',1)
        return, data1
       end
  endcase
endif

; ephin rates vs. ephin rates
if (in eq 'ephkey_rad1.fits') then begin
  loop_out = 1
  gifroot="R1"
  label="vs. E1300"
  data = mrdfits("ephkey.fits",1)
  return, data
endif ; if (in eq 'ephkey_rad.fits') then begin
if (in eq 'ephkey_rad2.fits') then begin
  loop_out = 1
  gifroot="R2"
  label="vs. P4GM"
  data = mrdfits("ephkey.fits",1)
  return, data
endif
if (in eq 'ephkey_rad3.fits') then begin
  loop_out = 1
  gifroot="R3"
  label="vs. P41GM"
  data = mrdfits("ephkey.fits",1)
  return, data
endif ; if (in eq 'ephkey_rad.fits') then begin
if (in eq 'ephkey_rad1_2001.fits') then begin
  loop_out = 1
  gifroot="R1_2001"
  label="vs. E1300"
  data = mrdfits("ephkey.fits",1)
  b=where(data.time ge 94694463. and data.time le 126230463.)
  return, data(b)
endif ; if (in eq 'ephkey_rad.fits') then begin
if (in eq 'ephkey_rad2_2001.fits') then begin
  loop_out = 1
  gifroot="R2_2001"
  label="vs. P4GM"
  data = mrdfits("ephkey.fits",1)
  b=where(data.time ge 94694463. and data.time le 126230463.)
endif
if (in eq 'ephkey_rad3_2001.fits') then begin
  loop_out = 1
  gifroot="R3_2001"
  label="vs. P41GM"
  data = mrdfits("ephkey.fits",1)
  b=where(data.time ge 94694463. and data.time le 126230463.)
  return, data(b)
endif ; if (in eq 'ephkey_rad.fits') then begin
if (in eq 'ephkey_rad1_2004.fits') then begin
  loop_out = 1
  gifroot="R1_2004"
  label="vs. E1300"
  data = mrdfits("ephkey.fits",1)
  b=where(data.time ge 189302463. and data.time le 220924863.)
  return, data(b)
endif ; if (in eq 'ephkey_rad.fits') then begin
if (in eq 'ephkey_rad2_2004.fits') then begin
  loop_out = 1
  gifroot="R2_2004"
  label="vs. P4GM"
  data = mrdfits("ephkey.fits",1)
  b=where(data.time ge 189302463. and data.time le 220924863.)
  return, data(b)
endif ; if (in eq 'ephkey_rad.fits') then begin
if (in eq 'ephkey_rad3_2004.fits') then begin
  loop_out = 1
  gifroot="R3_2004"
  label="vs. P41GM"
  data = mrdfits("ephkey.fits",1)
  b=where(data.time ge 189302463. and data.time le 220924863.)
  return, data(b)
endif ; if (in eq 'ephkey_rad.fits') then begin

; sun angle vs. hrc temp
if (in eq 'hrctemp_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'hrctemp_att.fits') then begin

if (in eq 'batt_temp_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'hrctemp_att.fits') then begin

if (in eq 'pcadftsgrad_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'hrctemp_att.fits') then begin

; sun angle vs. pcad temp
; sun angle vs. mups temp
if (in eq 'mups_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'hrctemp_att.fits') then begin

; sun angle vs. pcad temp
if (in eq 'pcadtemp_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'hrctemp_att.fits') then begin

; sun angle vs. pcad temp
if (in eq 'pcad_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; if (in eq 'hrctemp_att.fits') then begin

; sun angle vs. sim temp
if (in eq 'simtemp_att.fits') then begin
  ;loop_out = 3
  loop_out = 2
  gifroot="T"
  label="vs. Sun Angle"
  case loop_in of 
  1: begin
      data = mrdfits('simtemp1_att.fits',1)
      return, data
     end
  2: begin
      data = mrdfits('simtemp2_att.fits',1)
      return, data
     end
  3: begin
      data = mrdfits('simtempaux_att.fits',1)
      return, data
     end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif ; if (in eq 'simtemp_att.fits') then begin

; altitude vs. sim temp
if (in eq 'simtemp_alt.fits') then begin
  ;loop_out = 3
  loop_out = 2
  gifroot="L"
  label="vs. Altitude"
  case loop_in of 
  1: begin
      data = mrdfits('simtemp1_alt.fits',1)
      return, data
     end
  2: begin
      data = mrdfits('simtemp2_alt.fits',1)
      return, data
     end
  3: begin
      data = mrdfits('simtempaux_alt.fits',1)
      return, data
     end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif ; if (in eq 'simtemp_alt.fits') then begin

; sun angle vs. hrma temp
if (in eq 'hrmatherm_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'hrmatherm_alt.fits') then begin
  loop_out = 1
  gifroot="L"
  label="vs. Altitude"
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'hrmastruts_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'hrmastruts_alt.fits') then begin
  loop_out = 1
  gifroot="L"
  label="vs. Altitude"
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'obfwdbulkhead_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'obfwdbulkhead_alt.fits') then begin
  loop_out = 1
  gifroot="L"
  label="vs. Altitude"
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'precoll_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'precoll_alt.fits') then begin
  loop_out = 1
  gifroot="L"
  label="vs. Altitude"
  data = mrdfits(in,1)
  return, data
endif ; 

; ephtvkey ( trend eph rate vs temp)
if (in eq 'ephtvkey.fits') then begin
  loop_out = 2
  gifroot="T"
  case loop_in of 
  1: begin
      log_scale=1
      label="Count rates vs. Temperature"
      data = mrdfits('ephtvkey1.fits',1)
      b=where(data.tephin_avg gt 260)
      return, data(b)
     end
  2: begin
      log_scale=0
      label="Electronics vs. Temperature"
      data = mrdfits('ephtvkey2.fits',1)
      b=where(data.tephin_avg gt 260)
      return, data(b)
     end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif ; if (in eq 'ephtvkey.fits') then begin

; gratgen
if (in eq 'gratgen.fits') then begin
  loop_out = 11
  smooth=30
  symb=1
  case loop_in of
    1: begin
        label=""
        data = mrdfits(in,1)
        ; operation of gratings changed, so don't use EMF readings
        ;  before June 2000 for long term trending
        b=where(data.time lt cxtime(315,'met','sec'))
        data(b).X4MP28AV_AVG='NaN'
        data(b).X4MP28BV_AVG='NaN'
        data(b).X4MP5AV_AVG='NaN'
        data(b).X4MP5BV_AVG='NaN'
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
        b=where(data.x4mp28av_avg gt 0 and data.x4mp5av_avg gt 0,num)
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

if (in eq 'ephhk.fits') then begin
  loop_out=2 
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('ephhk1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('ephhk2.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'ephhk.fits') then begin

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
  ;loop_out =3 
  loop_out =1   ; remove hi and lo rad filters, no longer apply 02/26/09 bds
  log_scale=1
  smooth=90
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('ephrate1.fits',1)
        data2=mrdfits('ephrate2.fits',1)
        a={ephrate,time:0.0,sca00_avg:0.0, sca01_avg:0.0, sca02_avg:0.0, $
                sca03_avg:0.0, sca04_avg:0.0, sca05_avg:0.0, $
                scb00_avg:0.0, scb01_avg:0.0, scb02_avg:0.0, $
                scb04_avg:0.0, scb05_avg:0.0, scc0_avg:0.0, $
                scct1_avg:0.0, scct2_avg:0.0, scct3_avg:0.0, $
                scct4_avg:0.0, scct5_avg:0.0, scd0_avg:0.0, $
                sce0_avg:0.0, scf0_avg:0.0, scg0_avg:0.0, $
                sch25gr_avg:0.0, sch25s1_avg:0.0, sch25s23_avg:0.0, $
                sch41gr_avg:0.0, sch41s1_avg:0.0, sch41s23_avg:0.0, $
                sch4gr_avg:0.0, sch4s1_avg:0.0, sch4s23_avg:0.0, $
                sch8gr_avg:0.0, sch8s1_avg:0.0, sch8s23_avg:0.0, $
                scp25gr_avg:0.0, scp25s_avg:0.0, scp41gr_avg:0.0, $
                scp41s_avg:0.0, scp4gr_avg:0.0, scp4s_avg:0.0, $
                scp8gr_avg:0.0, scp8s_avg:0.0}
        data = replicate({ephrate}, n_elements(data1))
        data.time=data1.time
        data.sca00_avg=data1.sca00_avg
        data.sca01_avg=data1.sca01_avg
        data.sca02_avg=data1.sca02_avg
        data.sca03_avg=data1.sca03_avg
        data.sca04_avg=data1.sca04_avg
        data.sca05_avg=data1.sca05_avg
        data.scb00_avg=data1.scb00_avg
        data.scb01_avg=data1.scb01_avg
        data.scb02_avg=data1.scb02_avg
        data.scb04_avg=data1.scb04_avg
        data.scb05_avg=data1.scb05_avg
        data.scc0_avg=data1.scc0_avg
        data.scct1_avg=data1.scct1_avg
        data.scct2_avg=data1.scct2_avg
        data.scct3_avg=data1.scct3_avg
        data.scct4_avg=data1.scct4_avg
        data.scct5_avg=data1.scct5_avg
        data.scd0_avg=data1.scd0_avg
        data.sce0_avg=data1.sce0_avg
        data.scf0_avg=data1.scf0_avg
        data.scg0_avg=data1.scg0_avg
        data.sch25gr_avg=data1.sch25gr_avg
        data.sch25s1_avg=data2.sch25s1_avg
        data.sch25s23_avg=data2.sch25s23_avg
        data.sch41gr_avg=data2.sch41gr_avg
        data.sch41s1_avg=data2.sch41s1_avg
        data.sch41s23_avg=data2.sch41s23_avg
        data.sch4gr_avg=data2.sch4gr_avg
        data.sch4s1_avg=data2.sch4s1_avg
        data.sch4s23_avg=data2.sch4s23_avg
        data.sch8gr_avg=data2.sch8gr_avg
        data.sch8s1_avg=data2.sch8s1_avg
        data.sch8s23_avg=data2.sch8s23_avg
        data.scp25gr_avg=data2.scp25gr_avg
        data.scp25s_avg=data2.scp25s_avg
        data.scp41gr_avg=data2.scp41gr_avg
        data.scp41s_avg=data2.scp41s_avg
        data.scp4gr_avg=data2.scp4gr_avg
        data.scp4s_avg=data2.scp4s_avg
        data.scp8gr_avg=data2.scp8gr_avg
        data.scp8s_avg=data2.scp8s_avg
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

if (in eq 'hrcveto_ephx.fits') then begin
  loop_out=1
  log_scale=0
  smooth=30
  case loop_in of
    1: begin
        label="<a name=hrc_out>EPHIN rates vs. "+ $
               "HRC not in focal plane shield rate</a>"
        a=mrdfits('hrcveto_ai_eph.fits',1)
        b=mrdfits('hrcveto_as_eph.fits',1)
        t2={hrcv3,time:0.0,shevart_avgSHD:0.0, $
            sce1300_avgSHD:0.0,scint_avgSHD:0.0, $
            scp41gm_avgSHD:0.0,scp4gm_avgSHD:0.0}
        data1 = replicate({hrcv3}, n_elements(a)+n_elements(b))
        data1.time=[a.time,b.time]
        data1.shevart_avgSHD=[a.shevart_avg,b.shevart_avg]
        af=where(data1.shevart_avgSHD le 0,num)
        if (num gt 0) then data1(af).shevart_avgSHD="NaN"
        data1.sce1300_avgSHD=[a.e1300l1_avg,b.e1300l1_avg]
        data1.scint_avgSHD=[a.scintl1_avg,b.scintl1_avg]
        data1.scp41gm_avgSHD=[a.p41gml1_avg,b.p41gml1_avg]
        data1.scp4gm_avgSHD=[a.p4gml1_avg,b.p4gml1_avg]
        data1=data1(uniq(data1.time,sort(data1.time)))
        return, data1
      end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif; if (in eq 'hrcveto_ephx.fits') then begin

if (in eq 'hrcveto_eph.fits') then begin
  loop_out=1
  log_scale=0
  smooth=30
  case loop_in of
    1: begin
        label="<a name=hrc_out>EPHIN rates vs. "+ $
               "HRC not in focal plane shield rate</a>"
        a=mrdfits('hrcveto_ai_eph.fits',1)
        b=mrdfits('hrcveto_as_eph.fits',1)
        t2={hrceph,time:0.0,shevart_avgSHD:0.0, $
            sce1300_avgSHD:0.0,scint_avgSHD:0.0, $
            scp41gm_avgSHD:0.0,scp4gm_avgSHD:0.0}
        data1 = replicate({hrceph}, n_elements(a)+n_elements(b))
        data1.time=[a.time,b.time]
        data1.shevart_avgSHD=[a.shevart_avg,b.shevart_avg]
        af=where(data1.shevart_avgSHD le 0,num)
        if (num gt 0) then data1(af).shevart_avgSHD="NaN"
        data1.sce1300_avgSHD=[a.sce1300l1_avg,b.sce1300l1_avg]
        data1.scint_avgSHD=[a.scintl1_avg,b.scintl1_avg]
        data1.scp41gm_avgSHD=[a.scp41gml1_avg,b.scp41gml1_avg]
        data1.scp4gm_avgSHD=[a.scp4gml1_avg,b.scp4gml1_avg]
        data1=data1(uniq(data1.time,sort(data1.time)))
        b=where(data1.shevart_avgSHD lt 2.4e4,num)
        if (num gt 0) then data1=data1(b)
        return, data1
      end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif; if (in eq 'hrcveto_eph.fits') then begin

if (in eq 'hrcveto_eph2.fits') then begin
  loop_out=1
  log_scale=0
  smooth=30
  case loop_in of
    1: begin
        label="<a name=hrc_out>EPHIN rates vs. "+ $
               "HRC not in focal plane shield rate</a>"
        a=mrdfits('hrcveto_ai_eph.fits',1)
        b=mrdfits('hrcveto_as_eph.fits',1)
        t2={hrcv3,time:0.0,shevart_avgSHD:0.0, $
            sce1300_avgSHD:0.0,sce150_avgSHD:0.0, $
            sce3000_avgSHD:0.0,sce300_avgSHD:0.0, $
            sch25gm_avgSHD:0.0,sch41gm_avgSHD:0.0, $
            sch4gm_avgSHD:0.0,sch8gm_avgSHD:0.0, $
            scint_avgSHD:0.0, $
            scp25gm_avgSHD:0.0,scp41gm_avgSHD:0.0, $
            scp4gm_avgSHD:0.0,scp8gm_avgSHD:0.0}
        data1 = replicate({hrcv3}, n_elements(a)+n_elements(b))
        data1.time=[a.time,b.time]
        data1.shevart_avgSHD=[a.shevart_avg,b.shevart_avg]
        af=where(data1.shevart_avgSHD le 0,num)
        if (num gt 0) then data1(af).shevart_avgSHD="NaN"
        data1.sce1300_avgSHD=[a.sce1300l1_avg,b.sce1300l1_avg]
        data1.sce150_avgSHD=[a.sce150l1_avg,b.sce150l1_avg]
        data1.sce3000_avgSHD=[a.sce3000l1_avg,b.sce3000l1_avg]
        data1.sce300_avgSHD=[a.sce300l1_avg,b.sce300l1_avg]
        data1.sch25gm_avgSHD=[a.sch25gml1_avg,b.sch25gml1_avg]
        data1.sch41gm_avgSHD=[a.sch41gml1_avg,b.sch41gml1_avg]
        data1.sch4gm_avgSHD=[a.sch4gml1_avg,b.sch4gml1_avg]
        data1.sch8gm_avgSHD=[a.sch8gml1_avg,b.sch8gml1_avg]
        data1.scint_avgSHD=[a.scintl1_avg,b.scintl1_avg]
        data1.scp25gm_avgSHD=[a.scp25gml1_avg,b.scp25gml1_avg]
        data1.scp41gm_avgSHD=[a.scp41gml1_avg,b.scp41gml1_avg]
        data1.scp4gm_avgSHD=[a.scp4gml1_avg,b.scp4gml1_avg]
        data1.scp8gm_avgSHD=[a.scp8gml1_avg,b.scp8gml1_avg]
        data1=data1(uniq(data1.time,sort(data1.time)))
        return, data1
      end
    else: print, "dtrend_read ERROR", in, loop_in 
  endcase ; case loop_in of
endif; if (in eq 'hrcveto_eph2.fits') then begin

if (in eq 'hrcveto.fits') then begin
  ; hrcveto files must be created correctly to begin with
  ; require hrcveto_hi, for example where si=HRC-I and CORADMEN=ENAB
  ;  also hrcveto_ai, hrcveto_as, and hrcveto_hs
  ;  also hrcveto_rad where CORADMEN=DISA
  loop_out=4
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
    4: begin
        label="<a name=hrc_out>HRC not in focal plane</a>"
        a=mrdfits('hrcveto_ai.fits',1)
        b=mrdfits('hrcveto_as.fits',1)
        t2={hrcv3,time:0.0,shevart_avg3:0.0,tlevart_avg3:0.0, $
                  vlevart_avg3:0.0,tot_valid_avg3:0.0}
        data1 = replicate({hrcv3}, n_elements(a)+n_elements(b))
        data1.time=[a.time,b.time]
        af=where(a.shevart_avg le 1,num)
        if (num gt 0) then a(af).shevart_avg="NaN"
        bf=where(b.shevart_avg le 1,num)
        if (num gt 0) then b(bf).shevart_avg="NaN"
        data1.shevart_avg3=[a.shevart_avg,b.shevart_avg]
        af=where(a.tlevart_avg le 1,num)
        if (num gt 0) then a(af).tlevart_avg="NaN"
        bf=where(b.tlevart_avg le 1,num)
        if (num gt 0) then b(bf).tlevart_avg="NaN"
        data1.tlevart_avg3=[a.tlevart_avg,b.tlevart_avg]
        af=where(a.vlevart_avg le 1,num)
        if (num gt 0) then a(af).vlevart_avg="NaN"
        bf=where(b.vlevart_avg le 1,num)
        if (num gt 0) then b(bf).vlevart_avg="NaN"
        data1.vlevart_avg3=[a.vlevart_avg,b.vlevart_avg]
        data1.tot_valid_avg3=data1.tlevart_avg3-data1.vlevart_avg3
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
  ;loop_out=3 
  loop_out=2 
  log_scale=0
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('spcelec1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('spcelec2.fits',1)
        return, data1
       end
    ;3: begin
    ;    label=""
    ;    ;data1=mrdfits('elbi_low.fits',1)
    ;    data1=elbi_low_read()
    ;    return, data1
    ;   end
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
        data1.time=data1.time*86400L+31536000L
        return, data1
       end
  endcase
endif ; if (in eq 'compaciscent.fits') then begin

if (in eq 'compaciscent_c.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Computed ACIS Thermal"
        d1=mrdfits('acistemp.fits',1)
        a= {acisc, time:0.0,x1CBATC_AVG: 0.0, x1CBBTC_AVG: 0.0, x1CRATC_AVG: 0.0, x1CRBTC_AVG: 0.0, x1DACTBTC_AVG: 0.0, x1DEAMZTC_AVG: 0.0, x1DPAMYTC_AVG: 0.0, x1DPAMZTC_AVG: 0.0, x1OAHATC_AVG: 0.0, x1OAHBTC_AVG: 0.0, x1PDEAATC_AVG: 0.0, x1PDEABTC_AVG: 0.0, x1PIN1ATC_AVG: 0.0, x1WRATC_AVG: 0.0, x1WRBTC_AVG: 0.0}
        data = replicate({acisc}, n_elements(d1))
        data.time=d1.time
        data.x1CBATC_AVG = d1.x1CBAT_AVG  - 273.15
        data.x1CBBTC_AVG = d1.x1CBBT_AVG  - 273.15
        data.x1CRATC_AVG = d1.x1CRAT_AVG  - 273.15
        data.x1CRBTC_AVG = d1.x1CRBT_AVG  - 273.15
        data.x1DACTBTC_AVG = d1.x1DACTBT_AVG  - 273.15
        data.x1DEAMZTC_AVG = d1.x1DEAMZT_AVG  - 273.15
        data.x1DPAMYTC_AVG = d1.x1DPAMYT_AVG  - 273.15
        data.x1DPAMZTC_AVG = d1.x1DPAMZT_AVG  - 273.15
        data.x1OAHATC_AVG = d1.x1OAHAT_AVG  - 273.15
        data.x1OAHBTC_AVG = d1.x1OAHBT_AVG  - 273.15
        data.x1PDEAATC_AVG = d1.x1PDEAAT_AVG  - 273.15
        data.x1PDEABTC_AVG = d1.x1PDEABT_AVG  - 273.15
        data.x1PIN1ATC_AVG = d1.x1PIN1AT_AVG  - 273.15
        data.x1WRATC_AVG = d1.x1WRAT_AVG  - 273.15
        data.x1WRBTC_AVG= d1.x1WRBT_AVG - 273.15
        return, data
       end
  endcase
endif ; if (in eq 'compaciscent_c.fits') then begin

if (in eq 'compacispwr.fits') then begin
;if (in eq 'xxcompacispwr.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Computed ACIS Electronics"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99 and d1._1dppwra_avg gt 35 and d1._1dppwrb_avg gt 30)))
        ;data1=d1(where(d1.(1) ne -99))
        data1.time=long(data1.time)*86400L+31536000L
        return, data1
       end
  endcase
endif ; if (in eq 'compacispwr.fits') then begin

if (in eq 'compacispwr_c.fits') then begin
  loop_out = 2
  smooth=90
  case loop_in of
    1: begin
        label="Computed ACIS Electronics Side A"
        d1=mrdfits('aciseleca.fits',1)
        a = {acisa, time:0.0,x1DPPWRA_AVG:0.0}
        data = replicate({acisa}, n_elements(d1))
        data.time=d1.time
        data.x1DPPWRA_AVG=d1.x1DP28AVO_AVG*d1.x1DPICACU_AVG
        return,data
       end
    2: begin
        label="Computed ACIS Electronics Side B"
        d1=mrdfits('aciselecb.fits',1)
        a = {acisb, time:0.0,x1DPPWRB_AVG:0.0}
        data = replicate({acisb}, n_elements(d1))
        data.time=d1.time
        data.x1DPPWRB_AVG=d1.x1DP28BVO_AVG*d1.x1DPICBCU_AVG
        return,data
       end
  endcase
endif

if (in eq 'compephkey.fits') then begin
  loop_out = 2
  smooth=90
  case loop_in of
    1: begin
        label="Computed EPHIN Key Rates L1"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(3) ne -99)), cols=[0,3,5,7,9])
        ;data1=float_struct(d1(where(d1.(3) ne -99)))
        data1.time=data1.time*86400+31536000.
        print,min(data1.(1)),max(data1.(1))
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('eph_L1.fits',1)
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
        data1.time=data1.time*86400+31536000.
        return, data1
       end
  endcase
endif ; if (in eq 'compsimoffsetb.fits') then begin

if (in eq 'compsimoffsetb_c.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Computed SIM Thermal"
        d1=mrdfits('simtemp2.fits',1)
        a= {flexc, time:0.0,FLEXADIF_AVG: 0.0, FLEXBDIF_AVG: 0.0, FLEXCDIF_AVG: 0.0}
        data=replicate({flexc}, n_elements(d1))
        data.time=d1.time
        data.FLEXADIF_AVG=d1.FLEXATEMP_AVG-d1.FLEXATSET_AVG
        data.FLEXBDIF_AVG=d1.FLEXBTEMP_AVG-d1.FLEXBTSET_AVG
        data.FLEXCDIF_AVG=d1.FLEXCTEMP_AVG-d1.FLEXCTSET_AVG
        return, data
       end
  endcase
endif

if (in eq 'compgradkodak.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Computed HRMA Gradients"
        d1=mrdfits(in,1,/dscale)
        data1=float_struct(d1(where(d1.(1) ne -99)))
        data1.time=long(data1.time)*86400L+31536000L
        ; skip this period of low hrmaavg
        b=where(data1.hrmaavg_avg lt 300,bnum)
        if (bnum gt 0) then data1(b).hrmaavg_avg=-99
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
if (in eq 'gradcap_c.fits') then begin
  loop_out = 1
  smooth=90
  case loop_in of
    1: begin
        label="Gradients HRMA CAP"
        d1=mrdfits('hrmaheaters1.fits',1)
        d2=mrdfits('hrmaheaters2.fits',1)
        d3=mrdfits('hrmaheaters3.fits',1)
        d4=mrdfits('hrmaheaters4.fits',1)
        a= {gradc, time:0.0, HCAPGRD1_AVG:0.0, HCAPGRD2_AVG:0.0, HCAPGRD3_AVG:0.0, HCAPGRD4_AVG:0.0, HCAPGRD5_AVG:0.0, HCAPGRD6_AVG:0.0, HCAPGRD7_AVG:0.0, HCAPGRD8_AVG:0.0}
        data = replicate({acisc}, n_elements(d1))
        data.time=d1.time
        data.HCAPGRD1_AVG=d4.OHRTHR52_AVG-d2.OHRTHR31_AVG
        data.HCAPGRD2_AVG=d4.OHRTHR52_AVG-d4.OHRTHR53_AVG
        data.HCAPGRD3_AVG=d2.OHRTHR31_AVG-d3.OHRTHR33_AVG
        data.HCAPGRD4_AVG=d2.OHRTHR31_AVG-d4.OHRTHR53_AVG
        data.HCAPGRD5_AVG=d3.OHRTHR33_AVG-d1.OHRTHR08_AVG
        data.HCAPGRD6_AVG=d3.OHRTHR33_AVG-d1.OHRTHR09_AVG
        data.HCAPGRD7_AVG=d1.OHRTHR08_AVG-d2.OHRTHR31_AVG
        data.HCAPGRD8_AVG=d1.OHRTHR08_AVG-d4.OHRTHR54_AVG
        return, data
       end
  endcase
endif ;if (in eq 'gradcap_c.fits') then begin
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

if (in eq 'sc_anc_temp_att.fits') then begin
  loop_out = 2
  smooth=30
  gifroot="T"
  label="vs. Sun Angle"
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('sc_anc_temp1_att.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('sc_anc_temp2_att.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'sc_main_temp.fits') then begin

if (in eq 'sc_main_temp_att.fits') then begin
  loop_out = 4
  gifroot="T"
  label="vs. Sun Angle"
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('sc_main_temp1a_att.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('sc_main_temp1b_att.fits',1)
        return, data1
       end
    3: begin
        label=""
        data1=mrdfits('sc_main_temp2a_att.fits',1)
        return, data1
       end
    4: begin
        label=""
        data1=mrdfits('sc_main_temp2b_att.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'sc_main_temp.fits') then begin

if (in eq 'sc_main_temp.fits') then begin
  loop_out = 4
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('sc_main_temp1a.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('sc_main_temp1b.fits',1)
        return, data1
       end
    3: begin
        label=""
        data1=mrdfits('sc_main_temp2a.fits',1)
        return, data1
       end
    4: begin
        label=""
        data1=mrdfits('sc_main_temp2b.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'sc_main_temp.fits') then begin

if (in eq 'spceleca.fits') then begin
  loop_out = 3
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('spceleca1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('spceleca2a.fits',1)
        return, data1
       end
    3: begin
        label=""
        data1=mrdfits('spceleca2b.fits',1)
        b=where(data1.ctxapwr_avg lt 36)
        data1(b).ctxapwr_avg=-99
        b=where(data1.ctxav_avg lt 3.5)
        data1(b).ctxav_avg=-99
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
        b=where(data1.ctxbpwr_avg lt 36)
        data1(b).ctxbpwr_avg=-99
        b=where(data1.ctxbv_avg lt 3.5)
        data1(b).ctxbv_avg=-99
        return, data1
       end
  endcase
endif ; if (in eq 'spcelecb.fits') then begin

if (in eq 'pcadgrate.fits') then begin
  loop_out = 2
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('pcadgrate1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('pcadgrate2.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'pcadgrate.fits') then begin

if (in eq 'simtemp.fits') then begin
  ;loop_out = 3
  loop_out = 2
  ;smooth=30
  smooth=365
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('simtemp1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('simtemp2.fits',1)
        return, data1
       end
    3: begin
        label=""
        ; old data1=mrdfits('simtempaux.fits',1)
        ;rdfloat,'/data/mta/DataSeeker/data/repository/db_sim.rdb', $
        ;        time,x,x3famtrat,x,x3fapsat,x,x3faseaat,x,x3smotoc,x, $
        ;        x3smotstl,x,x3trmtrat,x,skipline=2
        rdfloat,'/data/mta/DataSeeker/data/repository/db_sim.rdb', $
                time,x,x3famtrat,x,x3fapsat,x,x3faseaat,x,x3trmtrat,x, $
                x3smotoc,x,x3smotstl,x,skipline=2
        a = {simt, time:0.0, x3FAMTRAT_avg:0.0, x3FAPSAT_avg:0.0, $
                             x3FASEAAT_avg:0.0, x3SMOTOC_avg:0.0, $
                             x3SMOTSTL_avg:0.0, x3TRMTRAT_avg:0.0}
        data1 = replicate({simt}, n_elements(time))
        data1.time = time
        data1.x3FAMTRAT_avg= x3famtrat 
        data1.x3FAPSAT_avg= x3fapsat
        data1.x3FASEAAT_avg= x3faseaat
        data1.x3SMOTOC_avg= x3smotoc
        data1.x3SMOTSTL_avg= x3smotstl
        data1.x3TRMTRAT_avg= x3trmtrat
        mwrfits,data1,'simtempaux.fits',/create
        return, data1
       end
  endcase
endif ; if (in eq 'simtemp.fits') then begin

if (in eq 'sc_anc_temp_F.fits') then begin
  loop_out = 2
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('sc_anc_temp1_F.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('sc_anc_temp2_F.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'sc_anc_temp.fits') then begin

if (in eq 'sc_anc_temp.fits') then begin
  loop_out = 2
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('sc_anc_temp1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('sc_anc_temp2.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'sc_anc_temp.fits') then begin

if (in eq 'obaheaters.fits') then begin
  loop_out = 4
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
    3: begin
        label=""
        data1=mrdfits('obaheaters3.fits',1)
        return, data1
       end
    4: begin
        label=""
        data1=mrdfits('obaheaters4.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'obaheaters.fits') then begin

if (in eq 'obaheaters_att.fits') then begin
  loop_out = 4
  smooth=30
  gifroot="T"
  label="vs. Sun Angle"
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('obaheaters1_att.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('obaheaters2_att.fits',1)
        return, data1
       end
    3: begin
        label=""
        data1=mrdfits('obaheaters3_att.fits',1)
        return, data1
       end
    4: begin
        label=""
        data1=mrdfits('obaheaters4_att.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'obaheaters.fits') then begin

if (in eq 'obaheaters_alt.fits') then begin
  loop_out = 4
  smooth=30
  gifroot="L"
  label="vs. Altitude"
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('obaheaters1_alt.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('obaheaters2_alt.fits',1)
        return, data1
       end
    3: begin
        label=""
        data1=mrdfits('obaheaters3_alt.fits',1)
        return, data1
       end
    4: begin
        label=""
        data1=mrdfits('obaheaters4_alt.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'obaheaters.fits') then begin

if (in eq 'hrmaheaters.fits') then begin
  loop_out = 4
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
    3: begin
        label=""
        data1=mrdfits('hrmaheaters3.fits',1)
        return, data1
       end
    4: begin
        label=""
        data1=mrdfits('hrmaheaters4.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'hrmaheaters.fits') then begin

if (in eq 'hrmaheaters_att.fits') then begin
  loop_out = 4
  smooth=30
  gifroot="T"
  label="vs. Sun Angle"
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('hrmaheaters1_att.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('hrmaheaters2_att.fits',1)
        return, data1
       end
    3: begin
        label=""
        data1=mrdfits('hrmaheaters3_att.fits',1)
        return, data1
       end
    4: begin
        label=""
        data1=mrdfits('hrmaheaters4_att.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'obaheaters.fits') then begin

if (in eq 'hrmaheaters_alt.fits') then begin
  loop_out = 4
  smooth=30
  gifroot="L"
  label="vs. Altitude"
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('hrmaheaters1_alt.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('hrmaheaters2_alt.fits',1)
        return, data1
       end
    3: begin
        label=""
        data1=mrdfits('hrmaheaters3_alt.fits',1)
        return, data1
       end
    4: begin
        label=""
        data1=mrdfits('hrmaheaters4_alt.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'obaheaters.fits') then begin

if (in eq 'hrmagrad_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'hrmagrad_alt.fits') then begin
  loop_out = 1
  gifroot="L"
  label="vs. Altitude"
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'obagrad_att.fits') then begin
  loop_out = 1
  gifroot="T"
  label="vs. Sun Angle"
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'obagrad_alt.fits') then begin
  loop_out = 1
  gifroot="L"
  label="vs. Altitude"
  data = mrdfits(in,1)
  return, data
endif ; 

if (in eq 'mups.fits') then begin
  loop_out = 3
  smooth=30
  case loop_in of
    1: begin
        label=""
        ;data1=mrdfits('mups_1.fits',1)
        data1=mrdfits('ds_mups1_psi.fits',1)
        data1=mrdfits('mups1.fits',1)
        ;data1=mups_read('mups_1')
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('mups_2a.fits',1)
        ;data1=mrdfits('mups2.fits',1)
        ;data1=mups_read('mups_2')
        return, data1
       end
    3: begin
        label=""
        data1=mrdfits('mups_2b.fits',1)
        return, data1
       end
    ;3: begin
    ;    label="MUPS PCAD"
    ;    ;data1=mrdfits('mups_2b.fits',1)
    ;    data1=mups_read('mups_pcad')
    ;    return, data1
    ;   end
    ;4: begin
    ;    label="MUPS PROP"
    ;    ;data1=mrdfits('mups_pcad1.fits',1)
    ;    data1=mups_read('mups_prop')
    ;    return, data1
    ;   end
  endcase
endif ; if (in eq 'mups.fits') then begin

if (in eq 'mups_old.fits') then begin
  loop_out = 7
  smooth=30
  case loop_in of
    1: begin
        label=""
        data1=mrdfits('mups_1.fits',1)
        return, data1
       end
    2: begin
        label=""
        data1=mrdfits('mups_2a.fits',1)
        return, data1
       end
    3: begin
        label=""
        data1=mrdfits('mups_2b.fits',1)
        return, data1
       end
    4: begin
        label=""
        data1=mrdfits('mups_pcad1.fits',1)
        return, data1
       end
    5: begin
        label=""
        data1=mrdfits('mups_pcad2.fits',1)
        return, data1
       end
    6: begin
        label=""
        data1=mrdfits('mups_prop1.fits',1)
        return, data1
       end
    7: begin
        label=""
        data1=mrdfits('mups_prop2.fits',1)
        return, data1
       end
  endcase
endif ; if (in eq 'mups_old.fits') then begin

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
