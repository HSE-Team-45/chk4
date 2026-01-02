# ML Service (PaddleOCR)

## Run
```bash
cp .env.example .env
## Optional: set OCR_LANG in .env (default: en)
docker compose up --build
```
## Auth
Get admin JWT:
```bash
curl -X POST http://localhost:8000/auth/token \
  -d 'username=admin&password=admin'
```

Use token:
```
Authorization: Bearer <token>
```

## /forward
JSON:
```bash
curl -X POST http://localhost:8000/forward \
  -H 'Content-Type: application/json' \
  -d '{"text": "hello"}'
```

Image (OCR):
```bash
curl -X POST http://localhost:8000/forward \
  -H 'X-Params: {"foo": "bar"}' \
  -F image=@/path/to/image.png
```

## /history
```bash
curl http://localhost:8000/history \
  -H 'Authorization: Bearer <token>'
```

Delete history:
```bash
curl -X DELETE http://localhost:8000/history \
  -H 'Authorization: Bearer <token>' \
  -H 'X-Confirm-Token: delete-me'
```

## /stats
```bash
curl http://localhost:8000/stats \
  -H 'Authorization: Bearer <token>'
```
