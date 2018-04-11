@Echo Off

if not "%minimized%"=="" goto :minimized
set minimized=true
start /min cmd /C "%~dpnx0"
goto :EOF
:minimized

cd C:\Users\tynanpmatthews\Desktop\TwitterClone
python manage.py runserver