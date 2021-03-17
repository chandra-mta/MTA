PRO FIT_TEMP, x ,a, f,pder
f=(a[0]*x+a[1])*sin(a[2]*x)+(a[3]*x+a[4])

;If the procedure is called with four parameters, calculate the
;partial derivatives.  - these are wrong
  IF N_PARAMS() GE 4 THEN begin
    a0pder=(a[0]*x*cos(a[2]*x))+(a[0]*sin(a[2]*x))
    a1pder=(a[1]*cos(a[2]*x))+(sin(a[2]*x))
    a2pder=sin(a[2]*x)
    a3pder=a[3]
    a4pder=1
    pder= [a0pder,a1pder,a2pder,a3pder,a4pder, [replicate(1.0, N_ELEMENTS(X))]]
  endif ;IF N_PARAMS() GE 4 THEN begin
end
