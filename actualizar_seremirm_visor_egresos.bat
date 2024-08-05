@echo off
REM Ejecutar el script de Python
python "C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\GIE\IEEH-REM20\IEEH - Dashboar de seguimiento\ieeh_descarga_datos.py"

REM Navegar al directorio del repositorio
cd "C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\GIE\IEEH-REM20\IEEH - Dashboar de seguimiento"

REM Agregar todos los cambios al commit
git add .

REM Crear un commit con un mensaje
git commit -m "Actualización automática de datos y commit"

REM Hacer push de los cambios al repositorio remoto
git push
