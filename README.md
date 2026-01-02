# LabTrust (Django) — Landing + Product + Checkout Starter

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open:
- Home: http://127.0.0.1:8000/
- Product: http://127.0.0.1:8000/products/peptide-a/
- Checkout: http://127.0.0.1:8000/checkout/

## Notes
- Cart is client-side (localStorage) for demo UI.
- Replace DEMO_PRODUCTS in store/views.py with real DB models or API.
- Wire checkout to Stripe/PaymentIntent in Django when ready.
