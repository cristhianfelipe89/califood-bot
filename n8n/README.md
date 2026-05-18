# CaliFoodBot — N8N Workflow

This folder contains an N8N workflow (`califood-workflow.json`) that replicates the Flask bot in `routes/webhook_routes.py`. It receives WhatsApp messages from Meta, stores user location in MongoDB, runs the same intent filters, calls OSRM for road distance, generates a reply with OpenAI, and sends the answer back via the WhatsApp Cloud API.

The point of moving this to N8N is operational: when you change the WhatsApp phone number in Meta, you only need to update **one variable** and **one webhook URL**. No redeploys.

---

## 1. Architecture mapping (Python → N8N)

| Flask piece | N8N node |
|---|---|
| `GET /webhook` (Meta verification) | `Webhook Verify (GET)` → `IF Verify Token` → `Respond Challenge` / `Respond 403` |
| `POST /webhook` | `Webhook Incoming (POST)` |
| Parse `entry[0].changes[0].value.messages[0]` | `Parse Message` (Code) |
| `guardar_ubicacion` | `Set Location Fields` → `Mongo Upsert Location` |
| `obtener_ubicacion` | `Mongo Find Location` |
| Intent detection (saludo / ubicacion / etiqueta / zona / cerca / no_sabe) | `Detect Intent` (Code) → `Switch Intent` |
| `listar_restaurantes` | `Mongo Find Restaurantes` |
| `calcular_distancias_reales` (OSRM) + filtros | `OSRM + Filter` (Code) |
| `generar_respuesta_ia` | `OpenAI Chat` (HTTP) → `Compose Final Reply` |
| `enviar_mensaje_whatsapp` | `Send WhatsApp` (HTTP to Graph API) |
| `guardar_conversacion` | `Set Conversation Fields` → `Save Conversation` |

---

## 2. Import the workflow

1. Open `http://localhost:5678/home/workflows`.
2. Click **Add workflow → Import from file** and pick `califood-workflow.json` (copy it from `\\wsl$\...` or use the n8n CLI).
3. The workflow imports inactive. Don't activate it yet — finish step 3 first.

CLI alternative from inside WSL (`crist@HERACOTS:~/n8n$`):

```bash
cp /mnt/c/Users/crist/OneDrive/Documents/GitHub/califood-bot/n8n/califood-workflow.json ~/n8n/
n8n import:workflow --input=$HOME/n8n/califood-workflow.json
```

---

## 3. Configure credentials and env vars

### 3.1 N8N environment variables (set in WSL before starting n8n)

```bash
export VERIFY_TOKEN="miclave_secreta_devrock"
export PHONE_NUMBER_ID="1104699786053226"
export WHATSAPP_TOKEN="EAAa...your-current-meta-token..."
```

Or persist them in `~/.bashrc` / your `n8n` systemd unit / docker-compose `environment:` section. Restart n8n after changing.

### 3.2 N8N credentials (UI → Credentials → New)

| Credential | Type | Where it's used |
|---|---|---|
| **MongoDB** | "MongoDB" | Bind to all four `Mongo *` nodes. Connection string from your `.env`: `mongodb+srv://...mongodb.net/califood`. Database: `califood`. |
| **OpenAI** | "OpenAI API" | Bind to `OpenAI Chat`. Use the `OPENAI_API_KEY` from `.env`. |

After binding, open each MongoDB node, pick the credential, and confirm the collection name (`ubicaciones`, `restaurantes`, `conversaciones`).

> ⚠️ Your `.env` has the WhatsApp token, OpenAI key, and Mongo password committed locally. Rotate them before pushing — Meta and OpenAI revoke leaked keys aggressively.

---

## 4. Expose n8n to Meta

Meta cannot reach `localhost:5678`. Choose one:

**Option A — ngrok (same as the Flask flow):**
```bash
ngrok http 5678
```
Webhook URL becomes: `https://<random>.ngrok-free.app/webhook/wsp`

**Option B — Cloudflare Tunnel (stable URL, free):**
```bash
cloudflared tunnel --url http://localhost:5678
```

The webhook **path** is `wsp` (set in both webhook nodes). The full URL Meta needs is:

```
https://<your-public-host>/webhook/wsp
```

Activate the workflow in the n8n UI before testing — inactive workflows return 404 on the production webhook URL.

---

## 5. Wire it up in Meta

1. Meta Business Suite → **WhatsApp → Configuration → Webhook → Edit**.
2. **Callback URL:** `https://<your-public-host>/webhook/wsp`.
3. **Verify token:** the same string as `VERIFY_TOKEN` in step 3.1.
4. Click **Verify and save**. Meta hits `GET /webhook/wsp?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...`; the workflow's `IF Verify Token` checks the token and returns the challenge.
5. Subscribe to the `messages` field.
6. Send a test message from your phone.

---

## 6. Switching phone numbers (personal → business)

This is the painful part you mentioned. Once the workflow exists, the swap takes ~5 minutes:

1. **Meta Business Manager → WhatsApp Accounts → Phone numbers → Add phone number.** Verify it via SMS / call to the new business line.
2. Once verified, copy its new **Phone number ID** (it's *not* the phone number itself — it's a numeric ID like `1104699786053226`).
3. Generate (or reuse) a **System User token** that has the WhatsApp Business permission for the new WABA. Permanent system-user tokens are strongly preferred over the 24h temporary tokens — otherwise you'll be doing this every day.
4. In WSL, update the env vars:
   ```bash
   export PHONE_NUMBER_ID="<new-id>"
   export WHATSAPP_TOKEN="<new-token>"
   ```
   Restart n8n so the new values are picked up. (Or update them in your docker-compose / systemd unit and `systemctl restart n8n`.)
5. **Webhook URL stays the same** — that's the whole point. In Meta's WhatsApp configuration for the new number, paste the same callback URL and the same verify token, then click Verify.
6. Subscribe the new number to the `messages` field.
7. Send a test message to the new business number.

What used to break:
- Forgetting to subscribe the new number to `messages` → Meta accepts the verification but never POSTs incoming messages.
- Using the old token with the new WABA → 401 from Graph API. Tokens are scoped to a WABA / system user.
- Using the *display phone number* instead of the *phone number ID* in `PHONE_NUMBER_ID` → 400 from Graph API.

---

## 7. Testing without Meta

You can fire a fake Meta payload at the local webhook to validate the flow end-to-end:

```bash
curl -X POST http://localhost:5678/webhook/wsp \
  -H 'Content-Type: application/json' \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "573001112233",
            "text": { "body": "hola" }
          }]
        }
      }]
    }]
  }'
```

For a location test, swap the message body for:
```json
{ "from": "573001112233", "location": { "latitude": 3.451, "longitude": -76.534 } }
```

---

## 8. Known differences vs. the Flask bot

- **Aggregate Restaurantes:** uses the `Item Lists` node to collapse Mongo's many-document output into one array before the OSRM Code node. If your n8n version doesn't have it under that name, replace it with a Code node: `return [{ json: { data: $input.all().map(i => i.json) } }];`.
- **OSRM rate limits:** the public OSRM server (`router.project-osrm.org`) is rate-limited. With more than ~20 restaurants per query you'll want to either self-host OSRM or precompute distances. The Code node loops sequentially to stay polite.
- **Saludo branch:** does not require location, matches the Flask behavior.
- The `Switch Intent` ordering matches the Flask priority: `saludo` > `ubicacion_recibida` > `actualizar_ubicacion` > `pedir_ubicacion` > `consulta`.
