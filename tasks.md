Release 1: Foundation & Data Layer Migration

Story 1: Core Infrastructure Setup (Supabase & FastAPI)

[x] Task 1.1.1: Provision a new Supabase project either via the Supabase cloud dashboard or by setting up the Supabase stack locally using Docker.

AC: A Supabase project is accessible.

[x] Task 1.1.2: Securely retrieve and document the Supabase project's database connection string (including host, port, database name, user, password) and API keys (if needed for client libraries).

AC: Database connection details (host, port, dbname, user, password) are recorded.

[x] Task 1.2.1: Define the SQL schema for the users table. Include columns: id (UUID, primary key, default gen_random_uuid()), platform_user_id (TEXT, unique, nullable), username (TEXT, unique, nullable), created_at (TIMESTAMPTZ, default now()), updated_at (TIMESTAMPTZ, default now()). Create this table in the Supabase database.

AC: The users table exists in the Supabase database with the specified columns, types, constraints, and default values.

[x] Task 1.2.2: Define the SQL schema for the articles table. Include columns: id (UUID, primary key, default gen_random_uuid()), author_id (UUID, foreign key references users(id), nullable), url (TEXT, unique, nullable), platform (TEXT), title (TEXT), content (TEXT), metadata (JSONB), crawled_at (TIMESTAMPTZ, default now()), published_at (TIMESTAMPTZ, nullable). Create this table in the Supabase database.

AC: The articles table exists in the Supabase database with the specified columns, types, constraints, and default values, including the foreign key relationship to users.

[x] Task 1.2.3: Define the SQL schema for the posts table (e.g., for LinkedIn/Substack). Include columns: id (UUID, primary key, default gen_random_uuid()), author_id (UUID, foreign key references users(id), nullable), url (TEXT, unique, nullable), platform (TEXT), content (TEXT), metadata (JSONB), crawled_at (TIMESTAMPTZ, default now()), published_at (TIMESTAMPTZ, nullable). Create this table in the Supabase database.

AC: The posts table exists in the Supabase database with the specified columns, types, constraints, and default values, including the foreign key relationship to users.

[x] Task 1.2.4: Define the SQL schema for the repositories table. Include columns: id (UUID, primary key, default gen_random_uuid()), owner_id (UUID, foreign key references users(id), nullable), url (TEXT, unique), name (TEXT), description (TEXT, nullable), metadata (JSONB), crawled_at (TIMESTAMPTZ, default now()), updated_repo_at (TIMESTAMPTZ, nullable). Create this table in the Supabase database.

AC: The repositories table exists in the Supabase database with the specified columns, types, constraints, and default values, including the foreign key relationship to users.

[x] Task 1.2.5: Define and implement a mechanism (e.g., a simple SQL function and trigger) to automatically update the updated_at column on users table whenever a row is updated.

AC: Updating a row in the users table automatically updates its updated_at timestamp.

[x] Task 1.3.1: Create the basic directory structure for the FastAPI application: src/api/, src/api/main.py, src/api/routers/, src/api/schemas/.

AC: The specified directories and main.py file exist within the src directory.

[x] Task 1.3.2: Initialize a basic FastAPI app instance in src/api/main.py. Include a root endpoint (/) that returns a simple JSON response (e.g., {"message": "API is running"}).

AC: Running uvicorn src.api.main:app --reload starts the server, and accessing http://localhost:8000/ returns the specified JSON response.

[x] Task 1.4.1: Add the retrieved Supabase database connection URL (DSN format: postgresql://user:password@host:port/dbname) to the .env file under a suitable variable name (e.g., SUPABASE_DB_URL).

AC: The .env file contains the SUPABASE_DB_URL variable with the correct connection string.

[x] Task 1.4.2: Update the AppSettings class in src/core/config.py to load the SUPABASE_DB_URL from the environment variables using Pydantic settings management.

AC: When the application loads configuration, the settings.supabase_db_url attribute holds the correct value from the .env file.

[x] Task 1.4.3: Remove any MongoDB connection string variables (e.g., MONGO_URI, MONGO_DB_NAME) from .env.example and .env.

AC: MongoDB connection variables are removed from environment configuration files.

[x] Task 1.4.4: Remove the loading and validation logic for MongoDB connection details from src/core/config.py.

AC: The AppSettings class in src/core/config.py no longer references or loads MongoDB configuration.

[x] Task 1.5.1: Add fastapi, uvicorn[standard] to the project's dependencies in pyproject.toml.

AC: fastapi and uvicorn are listed as dependencies in pyproject.toml.

[x] Task 1.5.2: Add a suitable asynchronous Postgres driver library (e.g., asyncpg) to the project's dependencies in pyproject.toml.

AC: asyncpg (or chosen alternative) is listed as a dependency in pyproject.toml.

[x] Task 1.5.3: (Optional, if using ORM) Add sqlalchemy[asyncio] and potentially sqlalchemy-utils to the project's dependencies in pyproject.toml. (If using Supabase Python client directly, add supabase-py).

AC: Chosen data access library (SQLAlchemy or supabase-py) is listed as a dependency in pyproject.toml.

[x] Task 1.5.4: Update the make install command in the Makefile to ensure poetry install correctly installs all new dependencies defined in pyproject.toml.

AC: Running make install successfully installs FastAPI, Uvicorn, the chosen Postgres driver, and ORM/client library without errors.

Story 2: Migrate Data Storage from MongoDB to Supabase

[x] Task 2.1.1: Create a new module src/core/db/supabase_client.py.

AC: The file src/core/db/supabase_client.py exists.

[x] Task 2.1.2: Implement a function or class within supabase_client.py to manage a connection pool (if using asyncpg or SQLAlchemy) or initialize the client (if using supabase-py), using the SUPABASE_DB_URL from core.config. Include functions to acquire/release connections or sessions.

AC: The module provides a mechanism to establish and manage connections/sessions to the Supabase Postgres database.

[x] Task 2.1.3: Implement a basic "execute" function in supabase_client.py that takes a SQL query string and parameters, executes it against the database using an acquired connection/session, and returns the result. Handle potential connection errors.

AC: A function exists to execute arbitrary SQL statements against the connected Supabase DB.

[x] Task 2.1.4: Implement a basic "fetch" function (e.g., fetch_one, fetch_all) in supabase_client.py that executes a SELECT query and returns results, potentially mapping them to Pydantic models or dictionaries.

AC: Functions exist to execute SELECT queries and retrieve data from the Supabase DB.

[x] Task 2.2.1 (Option B - Direct SQL/Client): Refactor src/core/db/documents.py. Keep the existing Pydantic models (UserDocument, ArticleDocument, etc.) for data structure definition and validation. Remove any beanie or motor specific base classes or decorators.

AC: Pydantic models in documents.py are decoupled from MongoDB-specific ORM/ODM features.

[ ] Task 2.2.2 (Option B): Create a new base class or helper functions within documents.py or supabase_client.py responsible for database interactions.

AC: A dedicated structure exists for handling Supabase interactions related to the Pydantic document models.

[x] Task 2.2.3 (Option B): Implement an async save(instance) method/function. It should take a Pydantic model instance, construct the appropriate SQL INSERT statement (handling potential conflicts like ON CONFLICT DO UPDATE), use the supabase_client.py execute function, and potentially update the instance with the generated ID/timestamps.

AC: Calling save(article_instance) correctly inserts or updates the corresponding record in the articles table in Supabase.

[x] Task 2.2.4 (Option B): Implement an async find_one(\*\*kwargs) method/function. It should construct a SQL SELECT query based on the provided keyword arguments (mapping keys to column names), use the supabase_client.py fetch function, and return a Pydantic model instance if found, otherwise None.

AC: Calling ArticleDocument.find_one(url="...") correctly retrieves the article from Supabase and returns it as an ArticleDocument instance or None.

[x] Task 2.2.5 (Option B): Implement an async get_or_create(defaults=None, \*\*kwargs) method/function for UserDocument. It should first attempt find_one using kwargs. If found, return the user. If not found, merge kwargs and defaults, create a new user instance, call save, and return the newly created user instance. Handle potential race conditions if necessary (e.g., using transaction or ON CONFLICT DO NOTHING).

AC: Calling UserDocument.get_or_create(platform_user_id="...") correctly finds an existing user or creates a new one in the Supabase users table and returns the corresponding UserDocument instance.

[x] Task 2.2.6 (Option B): Implement an async bulk_insert(instances) method/function. It should take a list of Pydantic model instances, construct an efficient SQL INSERT statement for multiple rows (using VALUES (...), (...) or COPY if applicable via the driver), and execute it using supabase_client.py.

AC: Calling ArticleDocument.bulk_insert([article1, article2]) efficiently inserts multiple article records into the Supabase articles table in a single operation.

[ ] Task 2.2.7 (Option A - ORM): Alternative to 2.2.1-2.2.6. Define SQLAlchemy models in src/core/db/sql_models.py corresponding to the Postgres tables (User, Article, Post, Repository).

AC: SQLAlchemy model classes mapping to the database tables exist.

[ ] Task 2.2.8 (Option A): Refactor src/core/db/documents.py to use the SQLAlchemy models. Adapt Pydantic models if needed or use them primarily for API boundaries. Update save, find_one, get_or_create, bulk_insert methods to use SQLAlchemy async session operations (session.add, session.execute(select(...)), session.merge, session.add_all, session.commit).

AC: Methods in documents.py correctly interact with the database via the SQLAlchemy ORM async session. UserDocument.get_or_create uses the ORM's capabilities.

[x] Task 2.3.1: Update the save_documents method in src/data_crawling/crawlers/base.py. Replace the self.model.bulk_insert(documents) call with the equivalent refactored bulk insert method from documents.py (ensure it's called with await).

AC: The BaseCrawler's save_documents method now uses the Supabase-compatible bulk insert logic.

[x] Task 2.3.2: Review src/data_crawling/crawlers/custom_article.py. Ensure the extract method correctly instantiates ArticleDocument and UserDocument (if applicable) and that saving happens through the refactored methods (likely via save_documents). Remove any direct Mongo calls.

AC: CustomArticleCrawler correctly creates Pydantic models and persists them to Supabase via the refactored data access layer.

[x] Task 2.3.3: Review src/data_crawling/crawlers/github.py. Ensure the extract method correctly instantiates RepositoryDocument and UserDocument and uses the refactored saving methods. Remove any direct Mongo calls.

AC: GithubCrawler correctly creates Pydantic models and persists them to Supabase via the refactored data access layer.

[x] Task 2.3.4: Review src/data_crawling/crawlers/medium.py (and others like linkedin.py if still used). Ensure they use the refactored Pydantic models and saving logic compatible with Supabase. Remove any direct Mongo calls.

AC: Other crawlers correctly create Pydantic models and persist them to Supabase via the refactored data access layer.

[x] Task 2.4.1: Update src/data_crawling/main.py (or the future FastAPI endpoint logic that uses this). Ensure the call UserDocument.get_or_create(...) uses the refactored, Supabase-compatible version and is called with await.

AC: The user lookup/creation logic correctly interacts with the Supabase users table.

[x] Task 2.5.1: Delete the file src/core/db/mongo.py.

AC: The file src/core/db/mongo.py no longer exists.

[x] Task 2.5.2: Remove MongoDB client libraries (pymongo, motor, beanie) from pyproject.toml.

AC: MongoDB related dependencies are removed from pyproject.toml.

[x] Task 2.5.3: Run poetry lock and poetry install (or make install) to update the lock file and environment, removing the old dependencies.

AC: The Poetry lock file is updated, and MongoDB libraries are removed from the virtual environment.

[x] Task 2.6.1: Edit docker-compose.yml. Remove the service definitions for mongo1, mongo2, mongo3 (or however many MongoDB services exist).

AC: MongoDB service definitions are removed from docker-compose.yml.

[x] Task 2.6.2: Edit docker-compose.yml. Remove any named volumes associated solely with the removed MongoDB services.

AC: MongoDB volumes are removed from the volumes section of docker-compose.yml.

[x] Task 2.6.3: (If running Postgres locally via Docker) Add a postgres service definition to docker-compose.yml using an official Postgres image (e.g., postgres:15). Configure necessary environment variables (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB), map ports (e.g., 5432:5432), and define a volume for data persistence. Ensure the credentials match the SUPABASE_DB_URL in .env (adjusting host to the service name, e.g., postgres).

AC: A postgres service is defined in docker-compose.yml for local development, or configuration points to the cloud Supabase instance.

[x] Task 2.6.4: Update the depends_on sections of other services (like the future API or listener) in docker-compose.yml if they need the database to be ready (add postgres service if running locally).

AC: Service dependencies in docker-compose.yml correctly reflect the need for the Postgres database to be available.

Release 2: CDC and Crawler Endpoint Refactoring

Story 3: Implement Postgres LISTEN/NOTIFY CDC Mechanism

[ ] Task 3.1.1: Define a PostgreSQL function (e.g., notify_data_change()) that takes no arguments, constructs a JSON payload containing the new row data (NEW.\*) along with table name and operation type ('INSERT'), and sends it using pg_notify('data_changes', payload::text).

AC: The notify_data_change SQL function is created in the Supabase database.

[ ] Task 3.1.2: Create a PostgreSQL TRIGGER on the articles table that executes the notify_data_change() function AFTER INSERT FOR EACH ROW.

AC: An AFTER INSERT trigger is attached to the articles table, calling the notification function.

[ ] Task 3.1.3: Create a similar PostgreSQL TRIGGER on the posts table (AFTER INSERT).

AC: An AFTER INSERT trigger is attached to the posts table, calling the notification function.

[ ] Task 3.1.4: Create a similar PostgreSQL TRIGGER on the repositories table (AFTER INSERT).

AC: An AFTER INSERT trigger is attached to the repositories table, calling the notification function.

[ ] Task 3.1.5: Test the trigger mechanism by manually inserting a row into articles using SQL and verifying that a notification appears on the data_changes channel (e.g., using LISTEN data_changes; in a separate psql session). Verify the JSON payload structure.

AC: Manually inserting data into triggered tables results in a correctly formatted JSON payload being sent via pg_notify on the data_changes channel.

[ ] Task 3.2.1: Create a new directory src/cdc_listener/ and a file src/cdc_listener/listener.py.

AC: The directory src/cdc_listener/ and file listener.py exist.

[ ] Task 3.2.2: In listener.py, implement async code to establish a connection to the Supabase Postgres DB using asyncpg and the SUPABASE_DB_URL from core.config.

AC: The listener script can successfully connect to the Supabase database asynchronously.

[ ] Task 3.2.3: In listener.py, use the asyncpg connection to execute the LISTEN data_changes; command.

AC: The listener script successfully subscribes to the data_changes notification channel.

[ ] Task 3.2.4: In listener.py, implement an asynchronous loop that waits for notifications using connection.add_listener and a callback function, or by iterating over connection.notifications().

AC: The listener script can asynchronously receive notifications sent on the data_changes channel.

[ ] Task 3.2.5: Inside the notification handling logic, parse the JSON payload received from the notification string. Add error handling for invalid JSON.

AC: The listener script successfully parses the JSON string payload from incoming notifications into a Python dictionary or object.

[ ] Task 3.2.6: Import and reuse the RabbitMQ connection logic and publisher from src/core/mq.py within listener.py.

AC: The listener script can access RabbitMQ publishing functionality.

[ ] Task 3.2.7: After successfully parsing the JSON payload, publish it as a message to the RabbitMQ queue previously used by the Bytewax pipeline (ensure queue name is configured correctly, e.g., via core.config). Serialize the payload back to JSON string or bytes for publishing.

AC: When a notification is received and parsed, the listener script publishes the corresponding payload to the configured RabbitMQ queue.

[ ] Task 3.2.8: Implement basic error handling and reconnection logic in listener.py for both the Postgres connection and the RabbitMQ connection. Log errors appropriately.

AC: The listener script includes mechanisms to attempt reconnection if the database or message queue connection is lost.

[ ] Task 3.3.1: Create a new Dockerfile .docker/Dockerfile.cdc_listener. Base it on a suitable Python image.

AC: The file .docker/Dockerfile.cdc_listener exists.

[ ] Task 3.3.2: In Dockerfile.cdc_listener, copy necessary source code (src/cdc_listener, src/core).

AC: The Dockerfile includes instructions to copy required source code into the image.

[ ] Task 3.3.3: In Dockerfile.cdc_listener, set up the Poetry environment and install dependencies using poetry install --no-root --no-dev. Ensure asyncpg and pika (or other MQ library) are installed.

AC: The Dockerfile correctly installs project dependencies using Poetry.

[ ] Task 3.3.4: In Dockerfile.cdc_listener, set the CMD or ENTRYPOINT to run the src/cdc_listener/listener.py script.

AC: The Dockerfile specifies the command to start the listener script when the container runs.

[ ] Task 3.4.1: Add a new service named cdc-listener to docker-compose.yml. Configure it to build using the .docker/Dockerfile.cdc_listener context.

AC: A cdc-listener service definition is added to docker-compose.yml.

[ ] Task 3.4.2: In the cdc-listener service definition in docker-compose.yml, set depends_on to include mq (RabbitMQ service) and postgres (if running Postgres locally).

AC: The cdc-listener service specifies dependencies on RabbitMQ and the local Postgres service (if applicable).

[ ] Task 3.4.3: Pass necessary environment variables to the cdc-listener service using the environment or env_file directive in docker-compose.yml (e.g., SUPABASE_DB_URL, RABBITMQ_URI, queue name).

AC: Required environment variables are passed to the cdc-listener container.

[ ] Task 3.5.1: Delete the entire src/data_cdc directory.

AC: The src/data_cdc directory no longer exists.

[ ] Task 3.5.2: Delete the old CDC Dockerfile .docker/Dockerfile.data_cdc.

AC: The file .docker/Dockerfile.data_cdc no longer exists.

[ ] Task 3.5.3: Remove the old data-cdc service definition from docker-compose.yml.

AC: The data-cdc service definition is removed from docker-compose.yml.

[ ] Task 3.6.1: Ensure all necessary configuration for the new cdc-listener (DB URL, MQ URL, MQ queue name, Listen channel name 'data_changes') is present in .env and loaded via src/core/config.py.

AC: Configuration loading includes all parameters needed by the new listener.

[ ] Task 3.6.2: Remove any obsolete configuration settings related to MongoDB CDC (e.g., specific Mongo collection names for CDC) from .env and src/core/config.py.

AC: Obsolete MongoDB CDC configuration is removed.

Story 4: Refactor Data Crawlers to FastAPI Endpoints

[ ] Task 4.1.1: Create a new file src/api/schemas/crawler.py.

AC: The file src/api/schemas/crawler.py exists.

[ ] Task 4.1.2: Define a Pydantic model LinkCrawlRequest in crawler.py with fields like link (HttpUrl) and user_info (e.g., a nested model with platform_user_id or username).

AC: The LinkCrawlRequest Pydantic model is defined for API input validation.

[ ] Task 4.1.3: Define a Pydantic model RawTextCrawlRequest in crawler.py with fields like text (str), user_info (same as above), and optional metadata (dict or nested model, e.g., source_platform, original_url).

AC: The RawTextCrawlRequest Pydantic model is defined for API input validation.

[ ] Task 4.1.4: Define Pydantic models for API responses, e.g., CrawlSuccessResponse (e.g., {"status": "submitted", "document_id": "..."}) and potentially standard error responses.

AC: Pydantic models for API responses are defined for serialization.

[ ] Task 4.2.1: Create a new file src/api/routers/crawling.py.

AC: The file src/api/routers/crawling.py exists.

[ ] Task 4.2.2: Initialize a FastAPI APIRouter instance in crawling.py.

AC: An APIRouter is created in crawling.py.

[ ] Task 4.2.3: Include the crawling router in the main FastAPI app in src/api/main.py using app.include_router.

AC: Endpoints defined in crawling.py will be accessible via the main application.

[ ] Task 4.3.1: Implement a new async function for the POST /crawl/link endpoint in crawling.py. Annotate it with @router.post("/link", response_model=...). It should accept the LinkCrawlRequest model as the request body.

AC: A FastAPI POST endpoint exists at /crawl/link.

[ ] Task 4.3.2: Inside the /crawl/link endpoint function, extract user information from the request body. Call the refactored UserDocument.get_or_create (with await) using the user info to get the user ID.

AC: The endpoint correctly retrieves or creates a user record in Supabase based on the request payload.

[ ] Task 4.3.3: Instantiate the CrawlerDispatcher from src/data_crawling/dispatcher.py within the endpoint function (or use dependency injection later).

AC: The CrawlerDispatcher is available within the endpoint.

[ ] Task 4.3.4: Call dispatcher.get_crawler(link) to determine the appropriate crawler instance based on the input link. Handle cases where no crawler is found (return HTTP 400).

AC: The endpoint correctly identifies the crawler for a given link.

[ ] Task 4.3.5: Call the selected crawler's extract(link=link, user=user_id) method (with await as crawler methods interacting with DB should be async). Handle potential exceptions during crawling/extraction (return HTTP 500).

AC: The endpoint successfully invokes the extract method of the appropriate crawler.

[ ] Task 4.3.6: Return an appropriate success response (e.g., CrawlSuccessResponse or a simple HTTP 202 Accepted) upon successful scheduling/completion of the crawl extraction.

AC: The /crawl/link endpoint returns a successful HTTP response upon completion.

[ ] Task 4.4.1: Implement a new async function for the POST /crawl/raw_text endpoint in crawling.py. Annotate it with @router.post("/raw_text", response_model=...). It should accept the RawTextCrawlRequest model as the request body.

AC: A FastAPI POST endpoint exists at /crawl/raw_text.

[ ] Task 4.4.2: Inside the /crawl/raw_text endpoint function, extract user information and call UserDocument.get_or_create (with await) to get the user ID.

AC: The endpoint correctly retrieves or creates a user record in Supabase based on the request payload.

[ ] Task 4.4.3: Process the incoming text and metadata. Decide on the target table (e.g., articles with platform='raw' or posts).

AC: The logic determines how to store the raw text within the existing database schema.

[ ] Task 4.4.4: Instantiate the appropriate Pydantic document model (e.g., ArticleDocument) with the processed text, metadata, and author_id.

AC: A Pydantic model instance is created representing the raw text input.

[ ] Task 4.4.5: Call the refactored save method (with await) from documents.py to persist the document instance to the Supabase database. Handle potential errors (return HTTP 500).

AC: The raw text data is successfully saved to the designated Supabase table.

[ ] Task 4.4.6: Return an appropriate success response (e.g., including the ID of the newly created record) from the /crawl/raw_text endpoint.

AC: The /crawl/raw_text endpoint returns a successful HTTP response, and the data persistence triggers the CDC LISTEN/NOTIFY flow.

[ ] Task 4.5.1: (Refinement) Refactor crawler/dispatcher instantiation in the API endpoints. Consider creating instances once (e.g., using FastAPI's lifespan events or a simple cache) or using FastAPI's Depends for dependency injection if state management becomes complex.

AC: Crawler/dispatcher instantiation is optimized for the API context.

[ ] Task 4.6.1: Delete the AWS Lambda handler specific code (e.g., wrapper functions) within src/data_crawling/main.py or other files.

AC: Lambda-specific handler code is removed from the Python source.

[ ] Task 4.6.2: Delete the Dockerfile specifically for the data crawlers Lambda function (.docker/Dockerfile.data_crawlers).

AC: The file .docker/Dockerfile.data_crawlers no longer exists.

[ ] Task 4.7.1: Create or update the primary API Dockerfile (e.g., .docker/Dockerfile.api). Ensure it copies all necessary source code (src/api, src/core, src/data_crawling).

AC: The API Dockerfile correctly includes crawler source code.

[ ] Task 4.7.2: Ensure the API Dockerfile installs all dependencies, including those required by the crawlers (e.g., requests, beautifulsoup4, specific SDKs).

AC: The API Dockerfile installs dependencies needed for both API serving and crawling logic.

[ ] Task 4.7.3: Set the CMD or ENTRYPOINT in the API Dockerfile to run the FastAPI application using uvicorn (e.g., uvicorn src.api.main:app --host 0.0.0.0 --port 80).

AC: The API Dockerfile correctly specifies the command to start the FastAPI server.

[ ] Task 4.8.1: Add/Update the api service definition in docker-compose.yml. Configure it to build using the .docker/Dockerfile.api context.

AC: An api service is defined in docker-compose.yml using the correct Dockerfile.

[ ] Task 4.8.2: Remove the old data-crawlers service definition (or similar name for the Lambda service) from docker-compose.yml.

AC: The service definition for the old crawler Lambda is removed from docker-compose.yml.

[ ] Task 4.8.3: Map the appropriate port for the api service in docker-compose.yml (e.g., 8000:80).

AC: The API service port is correctly mapped in docker-compose.yml.

[ ] Task 4.8.4: Ensure the api service in docker-compose.yml has necessary environment variables (e.g., SUPABASE_DB_URL) and potentially depends_on postgres (if local).

AC: The API service is configured with required environment variables and dependencies.

[ ] Task 4.9.1: Update the Makefile command local-test-medium (and similar for other platforms) to use curl or a similar tool to send a POST request to http://localhost:8000/crawl/link with the appropriate JSON payload.

AC: The make local-test-medium command successfully calls the new FastAPI endpoint for link crawling.

[ ] Task 4.9.2: Update the Makefile command local-ingest-data (if applicable) to use the new API endpoints.

AC: The make local-ingest-data command works with the refactored API.

[ ] Task 4.9.3: Add a new Makefile command local-test-raw-text that uses curl to send a POST request to http://localhost:8000/crawl/raw_text with a sample JSON payload containing text and user info.

AC: A make local-test-raw-text command exists and successfully calls the new FastAPI endpoint for raw text ingestion.

Story 5: Adapt Feature Pipeline (Bytewax)

[ ] Task 5.1.1: Review the RabbitMQSource configuration in src/feature_pipeline/main.py. Confirm it reads from the same queue name that the cdc-listener is publishing to (check configuration in core/config.py).

AC: The Bytewax RabbitMQSource is configured to consume from the correct queue populated by the cdc-listener.

[ ] Task 5.2.1: Inspect the JSON payload structure defined in the Postgres CDC function (notify_data_change()) created in Task 3.1.1.

AC: The exact structure of the JSON payload sent via pg_notify is known.

[ ] Task 5.2.2: Review the Pydantic models defined in src/feature_pipeline/models/raw.py (e.g., RawRecord) that are used to parse the incoming RabbitMQ messages.

AC: The Pydantic models used by Bytewax for message parsing are identified.

[ ] Task 5.2.3: Compare the JSON payload structure (from 5.2.1) with the Pydantic model structure (from 5.2.2). Adjust either the notify_data_change() function's payload construction or the Pydantic models in raw.py to ensure they match perfectly. Ensure all fields needed by Bytewax (content, metadata, etc.) are present.

AC: The JSON structure published by the listener matches the Pydantic model expected by the Bytewax pipeline, allowing successful parsing.

[ ] Task 5.3.1: Verify that the Qdrant connection details (QDRANT_HOST, QDRANT_PORT, QDRANT_API_KEY if applicable) in .env are correct and loaded properly by src/core/config.py.

AC: Qdrant connection settings are correctly configured.

[ ] Task 5.3.2: Confirm that the Bytewax pipeline's Qdrant client (src/feature_pipeline/steps/output.py or similar) uses these configuration settings to connect.

AC: The Bytewax pipeline successfully connects to the configured Qdrant instance.

[ ] Task 5.4.1: (Verification) Run the Bytewax pipeline (make local-start-feature-pipeline) after the cdc-listener has published messages. Observe logs to ensure messages are consumed, processed (cleaned, chunked, embedded), and written to Qdrant without errors related to data format or connection issues.

AC: The Bytewax pipeline runs successfully, processing messages originating from the Postgres CDC and storing results in Qdrant.

Release 3: Inference Pipeline Refactoring & UI Integration

Story 6: Refactor Inference Pipeline to FastAPI Endpoint

[ ] Task 6.1.1: Create a new file src/api/schemas/inference.py.

AC: The file src/api/schemas/inference.py exists.

[ ] Task 6.1.2: Define a Pydantic model InferenceRequest in inference.py with fields like query (str) and optional fields like use_rag (bool, default True), user_id (str, optional).

AC: The InferenceRequest Pydantic model is defined for API input validation.

[ ] Task 6.1.3: Define a Pydantic model InferenceResponse in inference.py with fields like answer (str) and optionally context (list[str] or similar, if RAG was used).

AC: The InferenceResponse Pydantic model is defined for API response serialization.

[ ] Task 6.2.1: Create a new file src/api/routers/inference.py.

AC: The file src/api/routers/inference.py exists.

[ ] Task 6.2.2: Initialize a FastAPI APIRouter instance in inference.py.

AC: An APIRouter is created in inference.py.

[ ] Task 6.2.3: Include the inference router in the main FastAPI app in src/api/main.py using app.include_router.

AC: Endpoints defined in inference.py will be accessible via the main application.

[ ] Task 6.3.1: Implement a new async function for the POST /generate endpoint in inference.py. Annotate it with @router.post("/generate", response_model=InferenceResponse). It should accept the InferenceRequest model as the request body.

AC: A FastAPI POST endpoint exists at /generate.

[ ] Task 6.3.2: Inside the /generate endpoint, instantiate the core logic class (e.g., LLMTwin from src/inference_pipeline/llm_twin.py) or necessary components (model, retriever). (Consider managing this instance via startup events or dependency injection - see Task 6.4).

AC: The core inference logic components are accessible within the endpoint.

[ ] Task 6.3.3: Call the main generation method (e.g., llm_twin_instance.generate(query=request.query, use_rag=request.use_rag)). Ensure this method now performs local inference instead of calling SageMaker. Await the result.

AC: The endpoint invokes the core generation logic using the request parameters.

[ ] Task 6.3.4: Adapt the Opik tracking. If @opik.track was used on the original generate method, ensure it still works. If tracking was manual, ensure the necessary Opik context managers or function calls are made within the endpoint function, capturing the request (query) and response (answer, context).

AC: Requests to the /generate endpoint are correctly tracked in Opik with relevant inputs and outputs.

[ ] Task 6.3.5: Format the result from the generation method into the InferenceResponse Pydantic model and return it. Handle potential errors during generation (return HTTP 500).

AC: The /generate endpoint returns the generated answer and context (if applicable) in the specified response format.

[ ] Task 6.4.1 (Model Loading - Option A: Startup Event): Define startup and potentially shutdown event handlers in src/api/main.py. In the startup handler, load the fine-tuned LLM model (using transformers, unsloth, etc.) and the RAG retriever (Qdrant client) and store them globally or attached to the app state (e.g., app.state.llm, app.state.retriever).

AC: The LLM model and retriever are loaded once when the FastAPI application starts.

[ ] Task 6.4.2 (Model Loading - Option B: Singleton/DI): Implement a singleton pattern or use a class-based dependency for the LLMTwin logic or its components (model, retriever) that ensures they are loaded only once when first requested by an endpoint.

AC: The LLM model and retriever are loaded efficiently, avoiding reloading on every request.

[ ] Task 6.4.3: Refactor src/inference_pipeline/llm_twin.py (or wherever model prediction occurs). Remove the build_sagemaker_predictor method or any code instantiating sagemaker.huggingface.model.HuggingFacePredictor.

AC: SageMaker predictor instantiation code is removed.

[ ] Task 6.4.4: Replace calls like self.\_llm_endpoint.predict(...) with direct calls to the loaded model's generation method (e.g., model.generate(...) or pipeline(...) from the transformers library, or Unsloth's inference methods). Ensure input formatting matches the local model's requirements.

AC: Inference calls are made directly to the locally loaded model object.

[ ] Task 6.5.1: Update src/inference_pipeline/config.py and potentially src/core/config.py. Remove the SAGEMAKER_ENDPOINT_NAME setting.

AC: SageMaker endpoint configuration is removed.

[ ] Task 6.5.2: Verify that settings required for local inference are present and correctly loaded: Hugging Face model ID (MODEL_ID), Hugging Face token (HF_TOKEN if needed for private models), device mapping (cuda, cpu), RAG parameters (chunk size, embedding model), Qdrant connection details.

AC: All necessary configurations for local inference and RAG are correctly loaded.

[ ] Task 6.6.1: Delete the Python script src/inference_pipeline/aws/deploy_sagemaker_endpoint.py.

AC: The SageMaker deployment script is removed.

[ ] Task 6.6.2: Delete the Python script src/inference_pipeline/aws/delete_sagemaker_endpoint.py.

AC: The SageMaker deletion script is removed.

[ ] Task 6.6.3: Remove any remaining imports or usage of the deleted AWS scripts or SageMaker client libraries within the src/inference_pipeline module.

AC: Codebase no longer references SageMaker deployment/deletion scripts or SageMaker predictor classes.

[ ] Task 6.7.1: Update the API Dockerfile (.docker/Dockerfile.api). Add dependencies required for inference: torch, transformers, unsloth (if used), qdrant-client, sentence-transformers (or other embedding model library), opik-sdk. Ensure correct versions compatible with the model.

AC: Inference-related Python dependencies are added to the API Dockerfile installation steps.

[ ] Task 6.7.2: Ensure the API Dockerfile includes the source code from src/inference_pipeline.

AC: The API Dockerfile copies the inference pipeline source code into the image.

[ ] Task 6.7.3: Plan for model weight handling. Options:

Option 1 (Download at build): Add RUN commands in the Dockerfile to download model weights during the image build (increases image size). Use HF_HUB_CACHE to manage cache location.

Option 2 (Download at runtime): Ensure the runtime environment has internet access and sufficient disk space for the model to be downloaded on first startup (using the startup event handler from Task 6.4.1).

Option 3 (Mount volume): Assume model weights are pre-downloaded and mounted into the container at runtime (requires external process/volume management).

AC: A strategy for handling model weights within the Docker container is chosen and implemented in the Dockerfile or runtime logic.

[ ] Task 6.8.1: Remove the deploy-inference-pipeline command from the Makefile.

AC: The deploy-inference-pipeline Make target is removed.

[ ] Task 6.8.2: Remove the delete-inference-pipeline-deployment command from the Makefile.

AC: The delete-inference-pipeline-deployment Make target is removed.

[ ] Task 6.8.3: Modify the call-inference-pipeline command in the Makefile to use curl to send a POST request to http://localhost:8000/generate with a sample InferenceRequest JSON payload.

AC: The make call-inference-pipeline command successfully calls the new FastAPI inference endpoint.

[ ] Task 6.8.4: Refactor the Gradio UI script (src/inference_pipeline/ui.py). Update the function that handles user input and generates the response. Instead of calling LLMTwin().generate() directly or using boto3 to call SageMaker, it should now use a library like requests or httpx to make a POST request to the FastAPI /generate endpoint (http://api:80/generate if running via Docker Compose, or http://localhost:8000/generate if run locally). Parse the JSON response to display the answer.

AC: Running make local-start-ui launches the Gradio UI, and interacting with it successfully calls the FastAPI /generate backend endpoint to get responses.

[ ] Task 6.8.5: Review evaluation scripts (evaluate-llm, evaluate-rag, etc.). If they relied on the SageMaker endpoint, update them to either: a) Instantiate the LLMTwin logic directly (if feasible), or b) Call the FastAPI /generate endpoint.

AC: Evaluation scripts are updated to work with the refactored local/FastAPI inference setup.

Release 4: Finalization, Testing & Documentation

Story 7: Final Cleanup, Testing & Documentation

[ ] Task 7.1.1: Review .env.example and ensure it reflects all necessary environment variables for the new stack (Supabase URL, RabbitMQ URI, Qdrant Host/Port, HF Model ID, etc.) and remove all obsolete variables (Mongo URI, SageMaker Endpoint).

AC: .env.example accurately lists all required configuration variables for the refactored application.

[ ] Task 7.1.2: Review all configuration loading logic in src/core/config.py and any service-specific config files (src/\*/config.py). Ensure consistency, remove unused settings, and verify defaults are sensible.

AC: Configuration loading code is clean, consistent, and only loads necessary settings.

[ ] Task 7.2.1: Perform a final review of docker-compose.yml. Check service names (api, cdc-listener, feature-pipeline, mq, qdrant, postgres or external Supabase config), build contexts, image names, environment variables, port mappings, volumes, and depends_on relationships.

AC: docker-compose.yml accurately defines the services, dependencies, and configurations for the complete refactored stack.

[ ] Task 7.2.2: Ensure resource limits (memory, CPU) are considered or added to docker-compose.yml services if needed, especially for the api service running the LLM.

AC: Resource allocation in docker-compose.yml is reviewed and potentially adjusted.

[ ] Task 7.3.1: Perform a final review of the Makefile. Verify that install, local-start, local-stop, local-logs, local-test-_, call-inference-pipeline, local-start-ui, evaluate-_ commands work correctly with the new structure.

AC: All primary Makefile commands function as expected against the refactored application.

[ ] Task 7.3.2: Remove any obsolete Makefile commands related to MongoDB, old CDC, Lambda deployment, or SageMaker deployment.

AC: Obsolete commands are removed from the Makefile.

[ ] Task 7.4.1: Write unit tests for the src/core/db/supabase_client.py functions (mocking the actual DB connection).

AC: Unit tests verify the basic functionality of the Supabase client module.

[ ] Task 7.4.2: Write unit tests for the src/cdc_listener/listener.py logic (mocking DB connection/notifications and MQ publishing). Test payload parsing and publishing logic.

AC: Unit tests verify the core logic of the CDC listener service.

[ ] Task 7.4.3: Write unit/integration tests for the FastAPI endpoints in src/api/routers/crawling.py. Use FastAPI's TestClient. Mock external calls (crawler extraction, DB saves) for unit tests, or use a test database for integration tests.

AC: Unit/integration tests verify the behavior of the crawler API endpoints.

[ ] Task 7.4.4: Write unit/integration tests for the FastAPI endpoint in src/api/routers/inference.py. Use TestClient. Mock the LLM generation and RAG retrieval for unit tests.

AC: Unit/integration tests verify the behavior of the inference API endpoint.

[ ] Task 7.5.1: Execute end-to-end test scenario 1:

Start all services (make local-start).

Call make local-test-medium (or similar crawler test).

Verify data appears in the corresponding Supabase table (articles, users).

Check cdc-listener logs for notification received and published message.

Check feature-pipeline logs for message consumed and processed.

Verify embeddings appear in Qdrant for the new content.

Call make call-inference-pipeline with a relevant query and use_rag=True.

Verify the response includes content derived from the newly ingested article.

AC: End-to-end data flow from link ingestion through RAG-based inference is successful.

[ ] Task 7.5.2: Execute end-to-end test scenario 2:

Start all services (make local-start).

Call make local-test-raw-text.

Verify data appears in the designated Supabase table (articles or posts, users).

Check cdc-listener logs for notification received and published message.

Check feature-pipeline logs for message consumed and processed.

Verify embeddings appear in Qdrant for the new content.

Call make call-inference-pipeline with a relevant query and use_rag=True.

Verify the response includes content derived from the newly ingested raw text.

AC: End-to-end data flow from raw text ingestion through RAG-based inference is successful.

[ ] Task 7.6.1: Update the Architecture Overview section in README.md to describe the new components (Supabase, FastAPI, Postgres CDC Listener). Remove mentions of MongoDB, Lambda, SageMaker endpoint.

AC: README accurately reflects the refactored architecture.

[ ] Task 7.6.2: Update any architecture diagrams referenced or included in the documentation.

AC: Architecture diagrams are updated to match the new flow.

[ ] Task 7.6.3: Update the Setup/Installation instructions in README.md to include Supabase setup (local or cloud) and remove MongoDB setup.

AC: README setup instructions are correct for the new architecture.

[ ] Task 7.7.1: Update INSTALL_AND_USAGE.md. Modify dependency installation steps if necessary (e.g., system dependencies for psycopg2).

AC: Installation dependencies in INSTALL_AND_USAGE.md are correct.

[ ] Task 7.7.2: Update INSTALL_AND_USAGE.md. Add instructions for setting up Supabase (connecting to cloud or running local Docker). Include details on obtaining the DB URL. Remove MongoDB setup instructions.

AC: Database setup instructions in INSTALL_AND_USAGE.md are correct for Supabase.

[ ] Task 7.7.3: Update INSTALL_AND_USAGE.md. Modify usage examples (e.g., how to trigger ingestion, how to call inference) to use the new Makefile commands or direct curl calls to the FastAPI endpoints. Remove examples using Lambda invocation or direct SageMaker calls.

AC: Usage examples in INSTALL_AND_USAGE.md correctly demonstrate interaction with the refactored application via FastAPI.

[ ] Task 7.7.4: Review INSTALL_AND_USAGE.md for any remaining references to AWS Lambda or AWS SageMaker endpoints in the context of core application deployment/usage (training pipeline usage might still involve SageMaker jobs, which is outside this refactoring's scope).

AC: INSTALL_AND_USAGE.md is free of obsolete deployment/usage instructions related to Lambda/SageMaker endpoints for crawling and inference serving.
