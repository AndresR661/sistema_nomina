Este es un sistema de nomina con el proposito de gestionar, calcular y controlar el pago de los empleados de una empresa de forma correcta, automática y legal.

Activador de entorno virtual
-Primero ir a PowerShell y colocar este codigo  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser  para dar los permisos de ejecutar scripts locales,
luego colocar el siguiente codigo en la terminal del proyecto de VS Studio  .\venv\Scripts\activate

Montar el proyecto en la web con ngrok
-Primero descarga ngrok con el enlace https://ngrok.com/download/windows luego entra en la terminal de ngrok y coloca  .\ngrok.exe authtoken 3A8XEEmQ6eBQ4mLSwCS0iuDALlU_48MqhbV7ps85e6UK4yHhX  luego  .\ngrok.exe http 5000  Ya estaria listo para arrancar el proyecto

Arrancar Proyecto Python
-Colocar el codigo  .\venv\Scripts\python.exe run.py  en la terminal del proyecto de VS estudio

Acceso URL de la Pagina
https://toccara-ulnar-unlugubriously.ngrok-free.dev

Actualizar repositorio
-Cada vez que quieras actualizar el repositorio de GitHub debes ejecutar estos comandos en la terminal de VS Studio donde esta el proyecto

git add .

git commit -m "cambio"

git push
