include .env

$(eval export $(shell sed -ne 's/ *#.*$$//; /./ s/=.*$$// p' .env))

PYTHONPATH := $(shell pwd)/src

install: # Create a local Poetry virtual environment and install all required Python dependencies.
	poetry env use 3.11
	poetry install --sync --with feature_pipeline --without superlinked_rag

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# ======================================
# ------- Docker Infrastructure --------
# ======================================

local-start: # Build and start your local Docker infrastructure.
	docker compose -f docker-compose.yml up --build -d
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5  # Give some time for PostgreSQL to start
	@docker exec llm-twin-postgres pg_isready -U postgres -d postgres || (echo "PostgreSQL is not ready yet. Waiting longer..." && sleep 10)
	@echo "Infrastructure started successfully!"
	@echo "Note: If this is the first time starting the container, migrations will be applied automatically."
	@echo "For new migrations, use 'make apply-migrations'"

local-start-with-migrations: # Start infrastructure and explicitly apply migrations
	$(MAKE) local-start
	$(MAKE) apply-migrations

# ======================================
# ---------- Database Migrations -------
# ======================================

apply-migrations: # Manually apply database migrations to the running Postgres instance
	@echo "Applying migrations to database..."
	docker exec -it llm-twin-postgres bash -c 'mkdir -p /tmp/migrations && cp /migrations/*.sql /tmp/migrations/ && for m in $$(ls -1 /tmp/migrations/*.sql | sort -n); do echo "Applying $$(basename $$m)"; psql -U postgres -d postgres -f $$m; done'
	@echo "Migrations applied successfully"

# ======================================
# ---------- Crawling Data -------------
# ======================================

# local-test-medium: # Make a call to the local API to crawl a Medium article.
# 	curl -X POST "http://localhost:8000/crawl/link" \
# 		-H "Content-Type: application/json" \
# 	  	-d '{"link": "https://medium.com/decodingml/an-end-to-end-framework-for-production-ready-llm-systems-by-building-your-llm-twin-2cc6bb01141f", "user_info": {"username": "test"}}'

# local-test-github: # Make a call to the local API to crawl a Github repository.
# 	curl -X POST "http://localhost:8000/crawl/link" \
# 		-H "Content-Type: application/json" \
# 	  	-d '{"link": "https://github.com/decodingml/llm-twin-course", "user_info": {"username": "test_user"}}'

# local-ingest-data: # Ingest all links from data/links.txt by calling the local API /crawl/link endpoint.
# 	while IFS= read -r link; do \
# 		echo "Processing: $$link"; \
# 		curl -X POST "http://localhost:8000/crawl/link" \
# 			-H "Content-Type: application/json" \
# 			-d "{\"link\": \"$$link\", \"user_info\": {\"username\": \"ingest_user\"}}"; \
# 		echo "\n"; \
# 		sleep 2; \
# 	done < data/links.txt

local-test-raw-text: # Make a call to the local API to submit raw text.
	curl -X POST "http://localhost:8000/crawl/raw_text" \
		-H "Content-Type: application/json" \
		-d '{"text": "Dolphins are among the most intelligent and social creatures in the ocean, possessing remarkable cognitive abilities that rival those of great apes. These marine mammals belong to the cetacean family and have evolved a complex social structure, communicating through an intricate system of clicks, whistles, and body language that researchers are still working to fully understand. Known for their playful nature, dolphins form strong social bonds within their pods, often engaging in cooperative hunting strategies that showcase their problem-solving abilities. Their brain-to-body mass ratio is second only to humans, enabling them to demonstrate self-awareness, tool usage, and even cultural learning where behaviors are passed down through generations. ", "user_info": {"username": "f_user"}, "metadata": {"source_platform": "manual_input_makefile"}}'

# ======================================
# -------- RAG Feature Pipeline --------
# ======================================

local-test-retriever: # Test the RAG retriever using your Poetry env
	cd src/feature_pipeline && poetry run python -m retriever


# ===================================================
# ===================================================
# -------- Inference Pipeline & Evaluation ----------
# ===================================================

call-inference: # Call the local FastAPI inference endpoint.
	curl -X POST "http://localhost:8000/inference/generate" \
		-H "Content-Type: application/json" \
		-d '{"query": "what is rag? give your answer in a poetic form", "use_rag": true}'


local-start-ui: # Start the Gradio UI for chatting with your LLM Twin using your Poetry env.
	cd src/inference_pipeline && poetry run python -m ui



evaluate-llm: # Run evaluation tests on the LLM model's performance using your Poetry env.
	cd src/inference_pipeline && poetry run python -m evaluation.evaluate

evaluate-rag: # Run evaluation tests specifically on the RAG system's performance using your Poetry env.
	cd src/inference_pipeline && poetry run python -m evaluation.evaluate_rag

evaluate-llm-monitoring: # Run evaluation tests for monitoring the LLM system using your Poetry env.
	cd src/inference_pipeline && poetry run python -m evaluation.evaluate_monitoring

# ======================================
# ------ Superlinked Bonus Series ------
# ======================================

install-superlinked: # Create a local Poetry virtual environment and install all required Python dependencies (with Superlinked enabled).
	poetry env use 3.11
	poetry install

local-start-superlinked: # Build and start local infrastructure used in the Superlinked series.
	docker compose -f docker-compose-superlinked.yml up --build -d

local-stop-superlinked: # Stop local infrastructure used in the Superlinked series.
	docker compose -f docker-compose-superlinked.yml down --remove-orphans

test-superlinked-server: # Ingest dummy data into the local superlinked server to check if it's working.
	poetry run python src/bonus_superlinked_rag/local_test.py

local-bytewax-superlinked: # Run the Bytewax streaming pipeline powered by Superlinked.
	RUST_BACKTRACE=full poetry run python -m bytewax.run src/bonus_superlinked_rag/main.py

local-test-retriever-superlinked: # Call the retrieval module and query the Superlinked server & vector DB
	docker exec -it llm-twin-bytewax-superlinked python -m retriever



