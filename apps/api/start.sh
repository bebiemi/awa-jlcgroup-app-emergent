export PYTHONPATH=/app/backend/src:$PYTHONPATH
cd /app/backend && /root/.venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
