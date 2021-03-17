PRO	gauss1,X,A,F,PDER
;+
; PRO	gauss1,X,A,F,PDER
;
; NAME:
;	gauss1
;
; PURPOSE:
;	EVALUATE THE SUM OF A GAUSSIAN AND A  0th ORDER POLYNOMIAL
;	AND OPTIONALLY RETURN THE VALUE OF IT'S PARTIAL DERIVATIVES.
;	NORMALLY, THIS FUNCTION IS USED BY CURVEFIT TO FIT THE
;	SUM OF A LINE AND A VARYING BACKGROUND TO ACTUAL DATA.
;
; CATEGORY:
;	E2 - CURVE AND SURFACE FITTING.
; CALLING SEQUENCE:
;	FUNCT,X,A,F,PDER
; INPUTS:
;	X = VALUES OF INDEPENDENT VARIABLE.
;	A = PARAMETERS OF EQUATION DESCRIBED BELOW.
; OUTPUTS:
;	F = VALUE OF FUNCTION AT EACH X(I).
;
; OPTIONAL OUTPUT PARAMETERS:
;	PDER = (N_ELEMENTS(X),4) ARRAY CONTAINING THE
;		PARTIAL DERIVATIVES.  P(I,J) = DERIVATIVE
;		AT ITH POINT W/RESPECT TO JTH PARAMETER.
; COMMON BLOCKS:
;	NONE.
; SIDE EFFECTS:
;	NONE.
; RESTRICTIONS:
;	NONE.
; PROCEDURE:
;	F = A(0)*EXP(-Z^2/2) + A(3)
;	Z = (X-A(1))/A(2)
; MODIFICATION HISTORY:
;	WRITTEN, DMS, RSI, SEPT, 1982.
;	Modified, DMS, Oct 1990.  Avoids divide by 0 if A(2) is 0.
;	Added to Gauss_fit, when the variable function name to
;		Curve_fit was implemented.  DMS, Nov, 1990.
;
;	copied from gaussfit.pro, mod to gaussian + constant (dph aug93)
;	added continuum shape to the fit (still one parameter) (dd oct 94)
;    ---------------------------------------------------------
;-
@df_common


	ON_ERROR,2                        ;Return to caller if an error occurs
	lgauss,x,a,f,pder 
	f = f + A(3)*df_continuum; FUNCTIONS.

	IF N_PARAMS(0) LE 3 THEN RETURN ;NEED PARTIAL?
	PDER = [[pder],[df_continuum]] ;YES, MAKE ARRAY.
	RETURN
END
