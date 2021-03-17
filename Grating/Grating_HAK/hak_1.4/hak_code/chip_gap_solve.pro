;+
; NAME:
;	chip_gap_solve
;
; chip_gap_solve.pro
;
; run from IDL command line with:
;
;   hak> @chip_gap_solve
;
; This script calculates the changes to the ACIS-S chips locations
; based on measurements of lines in the HEG and MEG spectra;
; e.g., in Capella and HR 1099 calibration observations.
;
; - - - - - -
; 11/1/99 dd
; 3/15/00 dd Add data from Capella obsid 57 observation.
;    ----------------------------------------------------------
;-

; LINES USED
; - - - - - - 
; The rows of the matrix (below) are for these Grating/Energies:
;
; MEG 1.8, MEG 1.47, MEG 1.35, MEG 1.02, MEG 828, MEG 653
;
; HEG 1.8, HEG 1.47, HEG 1.35, HEG 1.02, HEG 828
;
; corresponding names with wavelengths and chips covered:
meas_names = ['MEG/6.6 S2-..', 'MEG/8.4 S2-..', 'MEG/9.2 S2-S4', $
	'MEG/12. S2-S4', 'MEG/15. S1-S4', 'MEG/19. S1-S4', $
	'HEG/6.6 S2-S4', 'HEG/8.4 S1-S4', 'HEG/9.2 S1-S4', $
	'HEG/12. S1-S5', 'HEG/15. S0-S5']


; DATA SETS
; - - - - -
; Measured plus and minus order wavelengths:
; - - -
; one-line description of the data
data_desc = 'HAK (wide bins) Capella-1103 CXCDS_Sky + ' + $
	'HAK-No-offset analysis, 1/19/00 dd'
; Energies are pasted here from HAK output lists (in keV);
; then converted to wavelength.
minus = [1.86430,1.47183,1.35174,1.02173,0.825539,0.653389, $
	1.86470,1.47220,1.35197,1.02182,0.825624  ]
plus =  [1.86409,1.47207,1.35191,1.02183,0.825640,0.653448, $
	1.86367,1.47144,1.35137,1.02140,0.825345  ]
; - - -
; one-line description of the data
;;data_desc = 'HAK (wide bins) Capella-1318 CXCDS_Sky + ' + $
;;	'HAK-No-offset analysis, 10/8/99b dd'
; Energies are pasted here from HAK output lists (in keV);
; then converted to wavelength.
;;minus = [1.86477,1.47181,1.35197,1.02180,0.825558,0.653412, $
;;	1.86447,1.47185,1.35196,1.02178,0.825587 ]
;;plus =  [1.86393,1.47166,1.35174,1.02185,0.825581,0.653454, $
;;	1.86331,1.47130,1.35139,1.02139,0.825312 ]
; - - -
; one-line description of the data
;;data_desc = 'HAK (wide bins) Capella-57 CXCDS_Sky + ' + $
;;	'HAK-No-offset analysis, 3/8/00 dd'
; Energies are pasted here from HAK output lists (in keV);
; then converted to wavelength.
;;minus = [1.86417,1.47194,1.35199,1.02188,0.825508,0.653410, $
;;	1.86429,1.47169,1.35164,1.02157,0.825471  ]
;;plus =  [1.86376,1.47199,1.35142,1.02164,0.825601,0.653439 , $
;;	1.86392,1.47159,1.35154,1.02146,0.825387  ]
; - - - - -
	; convert to wavelength
plus = !DDHC/plus
minus = !DDHC/minus


; MATRIX
; - - - - -
; Setup a matrix which relates gap sizes to plus-minus order
; wavelength errors.  In addition, an MEG-HEG zero-order offset
; in dispersion direction is included in the matrix.
;
; The MEG and HEG zero-orders may be offset from each
; other along the dispersion direction; their actual
; offsets w.r.t. the full zero-order is given by a fraction
; of the total MEG-HEG separation:
;
;       |-----|----------|
;      MEG   Ave.       HEG
;     "zero"           "zero"
;
; weighted by low energy HRMA area ratio: HEG=1.0, MEG=2.15
; and 0.5 to 2. keV zero-order effic ratio: HEG=0.5, MEG=1.0
denom = 1.0*0.5 + 2.15*1.0
heg_delta_frac = 2.15*1.0/denom
meg_delta_frac = 1.0*0.5/denom

; rows of the matrix:
; MEG lines (see below):
r1 = [0.0, 0.0, 1.0, 0.0, 0.0, -2.0*meg_delta_frac]
r2 = [0.0, 0.0, 1.0, 0.0, 0.0, -2.0*meg_delta_frac]
r3 = [0.0, 0.0, 1.0, -1., 0.0, -2.0*meg_delta_frac]
r4 = [0.0, 0.0, 1.0, -1., 0.0, -2.0*meg_delta_frac]
r5 = [0.0, 1.0, 1.0, -1., 0.0, -2.0*meg_delta_frac]
r6 = [0.0, 1.0, 1.0, -1., 0.0, -2.0*meg_delta_frac]

; HEG lines (see below):
r7 = [0.0, 0.0, 1.0, -1., 0.0, 2.0*heg_delta_frac]
r8 = [0.0, 1.0, 1.0, -1., 0.0, 2.0*heg_delta_frac]
r9 = [0.0, 1.0, 1.0, -1., 0.0, 2.0*heg_delta_frac]
r10 = [0.0, 1.0, 1.0, -1., -1., 2.0*heg_delta_frac]
r11 = [1.0, 1.0, 1.0, -1., -1., 2.0*heg_delta_frac]

; the matrix
a = [   [r1], $
	[r2], $
	[r3], $
	[r4], $
	[r5], $
	[r6], $

	[r7], $
	[r8], $
	[r9], $
	[r10], $
	[r11] ]


; PROCESSING
; - - - -
print, ''
print, ' chip_gap_solve output  '+SYSTIME()
print, ''
print, ' Measured lines (Spectrum/Wavelength):'
print, meas_names
print, ''
print, ' Data: '+data_desc
print, ''
print, ' Minus-side wavelengths (MEG, HEG):'
print, minus
print, ' Plus-side wavelengths (MEG, HEG):'
print, plus
print, ''

; Conversion from wavelength to pixels:
mA = 89.89
hA = 179.77
pix_per_A = [mA, mA, mA, mA, mA, mA, hA, hA, hA, hA, hA]
mO = -0.08
hO = 0.36
offsets = [mO, mO, mO, mO, mO, mO, hO, hO, hO, hO, hO]

; Measured plus-minus differences in pixels:
b = (plus - minus) * pix_per_A
print, ' Pixel differences plus - minus :'
print, ''
print, b
print, ''

print, ' - - - - - '
print, ' solve matrix equation'
; Find the solution to the matrix equation
svdc, a, w,u,v
sol = svsol(u,w,v, b)
print, ' - - - - - '

print, ' Resulting chip gap values: '
print, sol(0:4)
print, ''
print, ' and HEG-MEG offset value: ', sol(5), ' pixels'
print, '   ( HEG, MEG offset : ', heg_delta_frac*sol(5), $
	-1.0*meg_delta_frac*sol(5), ' )'
print, ''

; Compare the solution results with the measured differences
calc = 0.0*b
for ib=0,n_elements(b)-1 do calc(ib) = TOTAL(a(*,ib)*sol)

print, ' Comparing measurements and best fit values:'
print, ''
print, '   Plus - Minus Differences (pixels)'
print, 'Spec/Wav./chips       Measured       Fit     Difference'
for ib=0,n_elements(b)-1 do print, meas_names(ib), $
	' : ', b(ib), calc(ib), STRING(b(ib)-calc(ib), FORMAT='(F11.3)')

print, ''
print, ' Resulting (additional) chip offsets in TDETX:'
print, ' S0 : ', -1.0*TOTAL(sol(0:2))
print, ' S1 : ', -1.0*TOTAL(sol(1:2))
print, ' S2 : ', -1.0*TOTAL(sol(2))
print, ' S3 :     0'
print, ' S4 : ', TOTAL(sol(3))
print, ' S5 : ', TOTAL(sol(3:4))
print, ''

; - - - end - - -

