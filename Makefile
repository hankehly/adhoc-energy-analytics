mlflow_server:
	source .venv/bin/activate && mlflow server \
		--host 127.0.0.1 \
		--port 8080 \
		--backend-store-uri sqlite:///mlflow.db \
		--default-artifact-root ./mlruns