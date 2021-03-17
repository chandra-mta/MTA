;
;--- this is a control idl script to run tscpos, move all plots to the main area
;--- and update html pages.
;
;---  first run tscpos.pro
;
success = tscpos(/trend)
if (n_elements(success) eq 0) then success = [1, 1]
;
;--- move files to web site
;
if (success(1) eq 0) then spawn, "mv -f tren*.gif /data/mta/www/mta_sim/Trend"
if (success(0) eq 0) then spawn, "mv -f *.gif /data/mta/www/mta_sim"
if (success(0) eq 0) then spawn, "mv -f tscpos.out /data/mta/www/mta_sim"
;
;--- update update date
;
if (success(0) eq 0) then spawn, "cp /data/mta/www/mta_sim/index.html xtmpindex"
if (success(0) eq 0) then spawn, "mv -f /data/mta/www/mta_sim/index.html /data/mta/www/mta_sim/index.old"
if (success(0) eq 0) then spawn, "/bin/sed '1,/SUMMARY START/s/^/xxx/' xtmpindex | grep '^xxx' | /bin/sed 's/^xxx//' > index.html"
if (success(0) eq 0) then spawn, "cat sum.html >> index.html"
if (success(0) eq 0) then spawn, "/bin/sed '/SUMMARY END/,/LAST UPDATE START/s/^/xxx/' xtmpindex | grep '^xxx' | /bin/sed 's/^xxx//' >> index.html"
if (success(0) eq 0) then spawn, "date >> index.html"
if (success(0) eq 0) then spawn, "/bin/sed '/LAST UPDATE END/,$s/^/xxx/' xtmpindex | grep '^xxx' | /bin/sed 's/^xxx//' >> index.html"

if (success(1) eq 0) then spawn, "cp /data/mta/www/mta_sim/Trend/index.html xtmptrend"
if (success(1) eq 0) then spawn, "/bin/sed '1,/LAST UPDATE START/s/^/xxx/' xtmptrend | grep '^xxx' | /bin/sed 's/^xxx//' > trend.html"
if (success(1) eq 0) then spawn, "date >> trend.html"
if (success(1) eq 0) then spawn, "/bin/sed '/LAST UPDATE END/,$s/^/xxx/' xtmptrend | grep '^xxx' | /bin/sed 's/^xxx//' >> trend.html"

if (success(0) eq 0) then spawn, "rm -f xtmpindex sum.html"
if (success(1) eq 0) then spawn, "rm -f xtmptrend"
if (success(0) eq 0) then spawn, "mv -f index.html /data/mta/www/mta_sim"
if (success(0) eq 0) then spawn, "mv -f wksum.html /data/mta/www/mta_sim"
if (success(1) eq 0) then spawn, "mv -f trend.html /data/mta/www/mta_sim/Trend/index.html"

exit
