PRO MKWEEKSUM, summary, m, timed

get_lun, hunit
openw, hunit, 'wksum.html'
printf, hunit, '<html>'
printf, hunit, '<title>MTA SIM Monitoring Page</title>'
printf, hunit, '<body TEXT="#FFFFFF" BGCOLOR="#000000" LINK="#FF0000" VLINK="#FFFF22" ALINK="#7500FF">'

printf, hunit, '<center><H1>SIM Movement Times</H1></center>'

printf, hunit, '<br><font size=+3>Weekly Summary</a></font></center>'


k = n_elements(where(timed ne '')) - 1
printf, hunit, '<center>Past week ending ', timed(k), '</center>'
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

; find average without Acis-I to Acis-S moves
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
printf, hunit, '</body></html>'
close, hunit
end
