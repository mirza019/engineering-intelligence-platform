.PHONY: data api frontend test up
data:
	python scripts/generate_synthetic_data.py
api:
	uvicorn backend.app.main:app --reload
frontend:
	cd frontend && npm run dev
test:
	pytest && cd frontend && npm test
up:
	docker compose up --build
