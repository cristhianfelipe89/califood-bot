# 🤖 Instrucciones de Configuración: CaliFoodBot (Versión Telegram)

Este proyecto es un bot gastronómico impulsado por **Flask, MongoDB, OSRM (cálculo de distancias reales) y OpenAI**, integrado directamente con la API de Telegram.

## 1. Crear y activar entorno virtual

Primero, ingresa a la carpeta del proyecto y crea el entorno virtual:

```bash
cd califood-bot
python -m venv venv
```

Actívalo según tu sistema operativo:

* **Windows:**
  ```bash
  .\venv\Scripts\activate
  ```
* **Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 1.1 Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 2. Configurar Variables de Entorno (.env)

Copia el archivo `.env.example`, renómbralo a `.env` y coloca las siguientes variables obligatorias:

* **`TELEGRAM_BOT_TOKEN`** → El token que te entregó @BotFather en Telegram.
* **`OPENAI_API_KEY`** → Tu clave de la API de OpenAI (para generar las respuestas conversacionales).
* **`MONGO_URI`** → Tu cadena de conexión de MongoDB Atlas.
* **`MONGO_DB_NAME`** → El nombre de tu base de datos (ej. `califood`).

*(Nota: La integración anterior con WhatsApp y Meta ha sido depreciada y eliminada por razones de rendimiento, costos y facilidad de despliegue).*

---

## 3. Levantar el Servidor Flask

El proyecto utiliza `Waitress` como servidor de producción local. Para iniciarlo:

```bash
python app.py
```
*(El servidor quedará ejecutándose en el puerto 5000).*

---

## 4. Exponer el servidor (Túneles)

Telegram necesita una URL pública en formato `https` para enviar los mensajes a tu máquina local. Puedes usar cualquiera de estas dos opciones (mantén esta terminal abierta):

**Opción A (Ngrok):**
```bash
ngrok http 5000
```

**Opción B (Cloudflare - Recomendado por estabilidad sin límites de tiempo):**
```bash
cloudflared tunnel --url http://localhost:5000
```

Copia la URL segura (la que empieza con `https://...`) que te arroje la consola.

---

## 5. 🔐 Vincular el Webhook con Telegram (Paso Clave)

Por motivos de seguridad, el servidor rechazará cualquier petición que no incluya el token secreto (`CaliFoodSecreto2026`). Debemos decirle a Telegram cuál es tu nueva URL y darle la "llave" de acceso.

Abre tu navegador web y visita la siguiente URL, reemplazando `<TU_TOKEN_TELEGRAM>` y `<TU_URL_DEL_TUNEL>` con tus datos reales:

```text
[https://api.telegram.org/bot](https://api.telegram.org/bot)<TU_TOKEN_TELEGRAM>/setWebhook?url=<TU_URL_DEL_TUNEL>/webhook&secret_token=CaliFoodSecreto2026&drop_pending_updates=true
```

> **Ejemplo:** `https://api.telegram.org/bot8945005985:AAHz.../setWebhook?url=https://abcd-123.trycloudflare.com/webhook&secret_token=CaliFoodSecreto2026&drop_pending_updates=true`

Si el navegador responde `{"ok":true,"result":true,"description":"Webhook was set"}`, ¡tu bot ya está en línea y listo para recibir mensajes de forma segura!

---

## 🛠️ Scripts y Comandos Útiles

**Para verificar la precisión de coordenadas en la BD:**
```bash
python scripts/verificar_precision.py
```

**Para probar cálculos de OSRM en local (Sin gastar tokens de IA):**
```bash
python scripts/debug_distancias.py
```

**Para generar menús falsos de prueba:**
```bash
python scripts/generate_menus.py
```

**Para saber las librerías instaladas o exportarlas a producción:**
```bash
pip list
pip freeze > requirements.txt
```