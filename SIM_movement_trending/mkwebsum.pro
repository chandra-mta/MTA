PRO MKWEBSUM, summary, timed, m, tsc, fa, pwm

get_lun, hunit
openw, hunit, 'sum.html'

printf, hunit, '<center><table border>'
printf, hunit, '<TR><TH Align="left"><FONT Size="">Mnemonic  </FONT></TH>'
printf, hunit, '  <TH Align="left"><FONT Size="">Description  </FONT></TH>'
printf, hunit, '  <TH Align="left"><FONT Size="">Contents </FONT></TH>'
printf, hunit, '  <TH Align="right"><FONT Size="" >min </FONT></TH>'
printf, hunit, '  <TH Align="right"><FONT Size="" >max </FONT></TH>'
printf, hunit, '  <TH Align="right"><FONT Size="" >count </FONT></TH></TR>'
printf, hunit, '<tr><td align=right><a href="http://asc.harvard.edu/mta_days/mta_sim/tscpos.html">3TSCPOS</a></td>'
printf, hunit, '<td align=left>TSC Position (z-axis)</td>'
printf, hunit, '<td align=left>TSC Position and SI Positions for entire mission</td>'
printf, hunit, '<td align=right>', min(tsc), '</td>'
printf, hunit, '<td align=right>', max(tsc), '</td>'
printf, hunit, '<td align=right>', n_elements(tsc), '</td></tr>'
printf, hunit, '<tr><td align=right><a href="http://asc.harvard.edu/mta_days/mta_sim/fapos.html">3FAPOS</a></td>'
printf, hunit, '<td align=left>FA Position (x-axis)</td>'
printf, hunit, '<td align=left>FA Position for entire mission</td>'
printf, hunit, '<td align=right>', min(fa), '</td>'
printf, hunit, '<td align=right>', max(fa), '</td>'
printf, hunit, '<td align=right>', n_elements(fa), '</td></tr>'
printf, hunit, '<tr><td align=right><a href="http://asc.harvard.edu/mta_days/mta_sim/mrmmxmv.html">3MRMMXMV</a></td>'
printf, hunit, '<td align=left>Max Pulse Width Modulation (last move)</td>'
printf, hunit, '<td align=left>MPWM</td>'
printf, hunit, '<td align=right>', min(pwm), '</td>'
printf, hunit, '<td align=right>', max(pwm), '</td>'
printf, hunit, '<td align=right>', n_elements(pwm), '</td></tr>'
printf, hunit, '</table>'

printf, hunit, '<br></br>'
printf, hunit, '<a href="daily.html">Past 24 hours</a>'
printf, hunit, '&nbsp&nbsp&nbsp&nbsp'
printf, hunit, '<a href="weekly.html">Past 7 days</a>'
printf, hunit, '<br><hr><br>'
printf, hunit, '<center><H1>SIM Movement Times</H1></center>'

printf, hunit, '<br><font size=+3><a href="http://asc.harvard.edu/mta_days/mta_sim/tscpos.out">Summary</a></font></center>'


k = n_elements(where(timed ne '')) - 1
printf, hunit, '<center>', timed(0), ' to ', timed(k), '</center>'
printf, hunit, '<center><table>'
printf, hunit, '<tr ALIGN=CENTER VALIGN=CENTER>'
printf, hunit, '<td>From</td>'
printf, hunit, '<td>To</td>'
printf, hunit, '<td># Obs</td>'
printf, hunit, '<td>Time/step</td>'
printf, hunit, '<td>Ave Time</td>'
printf, hunit, '<td>Std dev</td>'
printf, hunit, '</tr>'

totalnobs = 0
totaltperstep = 0
for i = 0, m do begin
  printf, hunit, '<tr ALIGN=CENTER VALIGN=CENTER>'
  printf, hunit, '<td>', summary(i).startd, '</td>'
  printf, hunit, '<td>', summary(i).stopd, '</td>'
  printf, hunit, '<td>', summary(i).nobs, '</td>'
  printf, hunit, '<td>', summary(i).tperstep, '</td>'
  printf, hunit, '<td>', summary(i).avet, '</td>'
  printf, hunit, '<td>', summary(i).sdev, '</td>'
  printf, hunit, '</tr>'
  totalnobs = totalnobs + summary(i).nobs
  totaltperstep = totaltperstep + (summary(i).nobs * summary(i).tperstep)
endfor

; totals
printf, hunit, '<tr ALIGN=CENTER VALIGN=CENTER>'
printf, hunit, '<td></td>'
printf, hunit, '<td>Total</td>'
printf, hunit, '<td>', totalnobs, '</td>'
printf, hunit, '<td>', totaltperstep/totalnobs, '</td>'
printf, hunit, '<td></td>'
printf, hunit, '<td></td>'
printf, hunit, '</tr>'

; find average with Acis-I to Acis-S moves
totalnobs = 0
totaltperstep = 0
for i = 1, 2 do begin
  totalnobs = totalnobs + summary(i).nobs
  totaltperstep = totaltperstep + (summary(i).nobs * summary(i).tperstep)
endfor
for i = 4, m do begin
  totalnobs = totalnobs + summary(i).nobs
  totaltperstep = totaltperstep + (summary(i).nobs * summary(i).tperstep)
endfor

; totals
printf, hunit, '<tr ALIGN=CENTER VALIGN=CENTER>'
printf, hunit, '<td></td>'
printf, hunit, '<td></td>'
printf, hunit, '<td></td>'
printf, hunit, '<td>', totaltperstep/totalnobs, '</td>'
printf, hunit, '<td>(excluding moves between Acis-S and Acis-I)</td>'
printf, hunit, '<td></td>'
printf, hunit, '</tr>'

printf, hunit, '</table></center>'
close, hunit
end
printf, hunit, '</table></center>'
close, hunit
end
