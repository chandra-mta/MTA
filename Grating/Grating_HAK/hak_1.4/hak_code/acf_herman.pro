PRO acf_herman, array, result, err
;+
; PRO acf_herman, array, result, err
;
; "In addition, the line autocorrelation function (ACF) was determined
; for each line and for the entire MEG or HEG spectrum.  The ACF is related
; to the optimum operation point; detection of faint lines is optimized
; when the ACF is maximized."
;   ---------------------------------------------------------------
; 3/31/99 dd Copied from Herman Marshall's web page
;   ---------------------------------------------------------------
;-

n = n_elements(array)
n1 = total(array)
n2 = total(double(array)^2)
n3 = total(double(array)^3)

; "Yo, Herman: how about some parentheses!"
result = n2 / n1 / n1
err = 2. * sqrt(n3) / n1 / n1

return
end