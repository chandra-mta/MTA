FUNCTION approx_equal, A, B, fraction
;+
; FUNCTION approx_equal, A, B, fraction
;
; Returns a value/array the size of A with 1 where A is within
; 1+/-"fraction" of B, and 0 where it is not.
;   ----------------------------------------------------------
; 6/24/95 dd
;   ----------------------------------------------------------
;-
if n_elements(fraction) EQ 0 then fraction = 0.05

about_equal = 0 + FIX(0*A)

where_about = where(ABS(A-B) LE fraction*ABS(B), n_about)

if n_about GE 1 then about_equal(where_about) = 1

RETURN, about_equal
END
