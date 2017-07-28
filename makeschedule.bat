call :getts ts

if {%1} == {} (set "dest=%ts%_cscm2017_schedule_pub") ^
else set "dest=%ts%_cscm2017_schedule_inner"

echo %dest%
if {%1} == {} (python reports2latex.py) else  python reports2latex.py 1

call :makeschedule "%dest%.pdf"

if {%1} == {} (call :deltmp cscm2017_schedule)
if {%1} == {} (call :delauto)
exit

goto :eof
:makeone
xelatex %1
copy /Y %1.pdf "%ts%_%1.pdf"
call :deltmp %1

goto :eof
:make
echo \def\hasmap#1{#1} > auto_hasmap.tex
call :makeschedule "%dest%_full.pdf"

goto :eof
:makeschedule
xelatex cscm2017_schedule
zhmakeindex -s zh.ist -z pinyin cscm2017_schedule
xelatex cscm2017_schedule
xelatex cscm2017_schedule
ren cscm2017_schedule.pdf "%1"

goto :eof

:delauto
set "auto=(auto_all_reports.csv, auto_list_abst.tex, auto_list_long.tex, auto_list_short.tex, auto_session.tex)"
for %%i in %auto% do if exist %%i (del %%i)
goto :eof

:deltmp
set "suffix=(aux, idx, ilg, ind, log, out, toc)"
for %%i in %suffix% do if exist %1.%%i (del %1.%%i)
goto :eof

rem get timestamps
:getts
@echo off
set "tmptoday=%date:/=%"
set "tmptoday=%tmptoday:~0,8%"
set "tmptime=%time::=%"
set "tmptime=%tmptime:~0,6%"
set "ts=%tmptoday%%tmptime%"
set "%1=%ts: =0%"
@echo on
goto :eof