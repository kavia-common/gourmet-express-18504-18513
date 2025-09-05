# gourmet-express-18504-18513

Backend service: food_backend_api (FastAPI)

Quickstart:
1) cd food_backend_api
2) cp .env.example .env
3) python -m venv .venv && source .venv/bin/activate
4) pip install -r requirements.txt
5) uvicorn src.api.main:app --reload

Key endpoints:
- GET /            -> Health check
- POST /auth/register
- POST /auth/login (OAuth2PasswordRequestForm fields: username=email, password)
- GET /auth/me
- GET /profiles/me, PUT /profiles/me
- GET /restaurants, GET /restaurants/{id}
- GET /menus/restaurant/{restaurant_id}, GET /menus/{item_id}
- POST /orders, GET /orders, GET /orders/{id}, GET /orders/{id}/status, GET /orders/{id}/track?step=0..4
- POST /payments/initiate, POST /payments/verify
- POST /notifications/subscribe, POST /notifications/send

Notes:
- In-memory storage only; replace repositories with real DB integration later.
- JWT secret and expiry configured via .env.