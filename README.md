# Lumen · Control de turnos

Sistema de turnos para laboratorio clínico con frontend Angular y API Flask. Incluye cuatro ventanillas, fila FIFO, folios A01, A02… y aviso sonoro al llamar o liberar una atención.

## Pantallas
- `/mesas`: panel del personal con fila de espera, llamado de turnos y control de las cuatro ventanillas.
- `/clientes`: pantalla de recepción para generar un turno y consultar el turno que está siendo llamado.

## Requisitos
- Node.js 20.19+ o 22.12+
- Python 3.10+

## Desarrollo local
1. Instala dependencias del frontend: `npm install`
2. En una terminal, instala Flask y levanta el backend:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   flask --app api.index run --port 5000
   ```
3. En otra terminal ejecuta `npm start -- --proxy-config proxy.conf.json`.
4. Abre `http://localhost:4200`.

Los datos se guardan en memoria y se reinician al volver a iniciar el backend. Vercel ejecuta la API como función sin estado persistente; para uso real con varios trabajadores conviene conectar una base de datos.

## Publicación
El proyecto está configurado para desplegarse en Vercel. Vincula un proyecto en Vercel y ejecuta `vercel --prod`.
