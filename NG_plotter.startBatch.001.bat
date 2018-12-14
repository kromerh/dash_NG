echo "Killing python processes"
Taskkill /IM python.exe /F
Taskkill /IM python.exe /F
Taskkill /IM python.exe /F
Taskkill /IM python.exe /F
TIMEOUT /T 10 /NOBREAK

echo "Starting NG plotter"
C:\Python34\python.exe M:\hkromer\17_github\NG_plotter.py