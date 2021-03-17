; IDL startup file for the HETG Analysis Kit (HAK) software
; Created by hak_create_dist.pro at MIT on Thu May  4 14:39:37 2000
; Created in: /nfs/wiwaxia/d4/ASC/src/hak_1.4
; --------------------------------------------------
DEFSYSV, '!DDVERDATE', 'Thu May  4 14:39:37 2000'
DEFSYSV, '!DDLOCATION', 'HAK Stand-alone'
DEFSYSV, '!DIR', EXISTS = ie
; *** Edit the following path to the ASTROLIB directory: ***
DEFSYSV, '!DDASTRO', !DIR+'/lib_astro/pro'
; *** Edit the following path to the hak_code directory: ***
;DEFSYSV, '!DDHAKCODE', '/nfs/wiwaxia/d4/ASC/src/hak_1.4/hak_code'
DEFSYSV, '!DDHAKCODE', '/home/mta/Gratings/hak_1.4/hak_code'
; *** Edit the following path to the hak_data directory: ***
;DEFSYSV, '!DDHAKDATA', '/nfs/wiwaxia/d4/ASC/src/hak_1.4/hak_data'
DEFSYSV, '!DDHAKDATA', '/home/mta/Gratings/hak_1.4/hak_data'
print, '' 
print, ' - - - - - - - - - - - - - - - - - - - - ' 
print, '       HETG Analysis Kit Software' 
print, '  created on: ' + !DDVERDATE 
print, ' - - - - - - - - - - - - - - - - - - - - ' 
print, '      http://space.mit.edu/HETG/HAK' 
print, ' - - - - - - - - - - - - - - - - - - - - ' 
print, '' 
; Add the HAK code to beginning of the path:
!path = !DDHAKCODE+':' + !path 
print, ' HAK code dir : ' + !DDHAKCODE
print, ' Ref data dir : ' + !DDHAKDATA
print, '' 
print, ' To list the routines available:' 
print, '   hak> $ls '+ !DDHAKCODE
print, ' To get information on a routine, e.g.:' 
print, '   hak> doc_library, ''obs_anal'' ' 
print, '' 
print, ' - - - - - - - - - - - - - - - - - - - - ' 
; Add the astrolibrary to the end of the path: 
full_astro = EXPAND_PATH('+'+!DDASTRO) 
!path=!path+':' + full_astro 
ASTROLIB
; set the prompt and foc_common and we're done...
print, '' 
DEFSYSV, '!DDHC',       12.3985
!prompt = 'hak> ' 
@oa_common ' 
@foc_common ' 
