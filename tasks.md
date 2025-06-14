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

[x] Task 2.1.2: Implement a function or class within supabase_client.py to manage a connection pool (if using asyncpg or SQLAlchemy) or initialize the client (if using supabase-py), using the SUPABASE_DB_URL from src.core.config. Include functions to acquire/release connections or sessions.

AC: The module provides a mechanism to establish and manage connections/sessions to the Supabase Postgres database.

[x] Task 2.1.3: Implement a basic "execute" function in supabase_client.py that takes a SQL query string and parameters, executes it against the database using an acquired connection/session, and returns the result. Handle potential connection errors.

AC: A function exists to execute arbitrary SQL statements against the connected Supabase DB.

[x] Task 2.1.4: Implement a basic "fetch" function (e.g., fetch_one, fetch_all) in supabase_client.py that executes a SELECT query and returns results, potentially mapping them to Pydantic models or dictionaries.

AC: Functions exist to execute SELECT queries and retrieve data from the Supabase DB.

[x] Task 2.2.1 (Option B - Direct SQL/Client): Refactor src/core/db/documents.py. Keep the existing Pydantic models (UserDocument, ArticleDocument, etc.) for data structure definition and validation. Remove any beanie or motor specific base classes or decorators.

AC: Pydantic models in documents.py are decoupled from MongoDB-specific ORM/ODM features.

[x] Task 2.2.2 (Option B): Create a new base class or helper functions within documents.py or supabase_client.py responsible for database interactions. (Implemented as classmethods on models)

AC: A dedicated structure exists for handling Supabase interactions related to the Pydantic document models.

[x] Task 2.2.3 (Option B): Implement an async save(instance) method/function. It should take a Pydantic model instance, construct the appropriate SQL INSERT statement (handling potential conflicts like ON CONFLICT DO UPDATE), use the supabase_client.py execute function, and potentially update the instance with the generated ID/timestamps.

AC: Calling save(article_instance) correctly inserts or updates the corresponding record in the articles table in Supabase.

[x] Task 2.2.4 (Option B): Implement an async find_one(\*\*kwargs) method/function. It should construct a SQL SELECT query based on the provided keyword arguments (mapping keys to column names), use the supabase_client.py fetch function, and return a Pydantic model instance if found, otherwise None.

AC: Calling ArticleDocument.find_one(url="...") correctly retrieves the article from Supabase and returns it as an ArticleDocument instance or None.

[x] Task 2.2.5 (Option B): Implement an async get_or_create(defaults=None, \*\*kwargs) method/function for UserDocument. It should first attempt find_one using kwargs. If found, return the user. If not found, merge kwargs and defaults, create a new user instance, call save, and return the newly created user instance. Handle potential race conditions if necessary (e.g., using transaction or ON CONFLICT DO NOTHING).

AC: Calling UserDocument.get_or_create(platform_user_id="...") correctly finds an existing user or creates a new one in the Supabase users table and returns the corresponding UserDocument instance.

[x] Task 2.2.6 (Option B): Implement an async bulk_insert(instances) method/function. It should take a list of Pydantic model instances, construct an efficient SQL INSERT statement for multiple rows (using VALUES (...), (...) or COPY if applicable via the driver), and execute it using supabase_client.py.

AC: Calling ArticleDocument.bulk_insert([article1, article2]) efficiently inserts multiple article records into the Supabase articles table in a single operation.

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

[x] Task 3.1.1: Define a PostgreSQL function (e.g., notify_data_change()) that takes no arguments, constructs a JSON payload containing the new row data (NEW.\*) along with table name and operation type ('INSERT'), and sends it using pg_notify('data_changes', payload::text).

AC: The notify_data_change SQL function is created in the Supabase database.

[x] Task 3.1.2: Create a PostgreSQL TRIGGER on the articles table that executes the notify_data_change() function AFTER INSERT FOR EACH ROW.

AC: An AFTER INSERT trigger is attached to the articles table, calling the notification function.

[x] Task 3.1.3: Create a similar PostgreSQL TRIGGER on the posts table (AFTER INSERT).

AC: An AFTER INSERT trigger is attached to the posts table, calling the notification function.

[x] Task 3.1.4: Create a similar PostgreSQL TRIGGER on the repositories table (AFTER INSERT).

AC: An AFTER INSERT trigger is attached to the repositories table, calling the notification function.

[x] Task 3.1.5: Test the trigger mechanism by manually inserting a row into articles using SQL and verifying that a notification appears on the data_changes channel (e.g., using LISTEN data_changes; in a separate psql session). Verify the JSON payload structure.

AC: Manually inserting data into triggered tables results in a correctly formatted JSON payload being sent via pg_notify on the data_changes channel.

[x] Task 3.2.1: Create a new directory src/cdc_listener/ and a file src/cdc_listener/listener.py.

AC: The directory src/cdc_listener/ and file listener.py exist.

[x] Task 3.2.2: In listener.py, implement async code to establish a connection to the Supabase Postgres DB using asyncpg and the SUPABASE_DB_URL from src.core.config.

AC: The listener script can successfully connect to the Supabase database asynchronously.

[x] Task 3.2.3: In listener.py, use the asyncpg connection to execute the LISTEN data_changes; command.

AC: The listener script successfully subscribes to the data_changes notification channel.

[x] Task 3.2.4: In listener.py, implement an asynchronous loop that waits for notifications using connection.add_listener and a callback function, or by iterating over connection.notifications().

AC: The listener script can asynchronously receive notifications sent on the data_changes channel.

[x] Task 3.2.5: Inside the notification handling logic, parse the JSON payload received from the notification string. Add error handling for invalid JSON.

AC: The listener script successfully parses the JSON string payload from incoming notifications into a Python dictionary or object.

[x] Task 3.2.6: Import and reuse the RabbitMQ connection logic and publisher from src/core/mq.py within listener.py.

AC: The listener script can access RabbitMQ publishing functionality.

[x] Task 3.2.7: After successfully parsing the JSON payload, publish it as a message to the RabbitMQ queue previously used by the Bytewax pipeline (ensure queue name is configured correctly, e.g., via core.config). Serialize the payload back to JSON string or bytes for publishing.

AC: When a notification is received and parsed, the listener script publishes the corresponding payload to the configured RabbitMQ queue.

[x] Task 3.2.8: Implement basic error handling and reconnection logic in listener.py for both the Postgres connection and the RabbitMQ connection. Log errors appropriately.

AC: The listener script includes mechanisms to attempt reconnection if the database or message queue connection is lost.

[x] Task 3.3.1: Create a new Dockerfile .docker/Dockerfile.cdc_listener. Base it on a suitable Python image.

AC: The file .docker/Dockerfile.cdc_listener exists.

[x] Task 3.3.2: In Dockerfile.cdc_listener, copy necessary source code (src/cdc_listener, src/core).

AC: The Dockerfile includes instructions to copy required source code into the image.

[x] Task 3.3.3: In Dockerfile.cdc_listener, set up the Poetry environment and install dependencies using poetry install --no-root --no-dev. Ensure asyncpg and pika (or other MQ library) are installed.

AC: The Dockerfile correctly installs project dependencies using Poetry.

[x] Task 3.3.4: In Dockerfile.cdc_listener, set the CMD or ENTRYPOINT to run the src/cdc_listener/listener.py script.

AC: The Dockerfile specifies the command to start the listener script when the container runs.

[x] Task 3.4.1: Add a new service named cdc-listener to docker-compose.yml. Configure it to build using the .docker/Dockerfile.cdc_listener context.

AC: A cdc-listener service definition is added to docker-compose.yml.

[x] Task 3.4.2: In the cdc-listener service definition in docker-compose.yml, set depends_on to include mq (RabbitMQ service) and postgres (if running Postgres locally).

AC: The cdc-listener service specifies dependencies on RabbitMQ and the local Postgres service (if applicable).

[x] Task 3.4.3: Pass necessary environment variables to the cdc-listener service using the environment or env_file directive in docker-compose.yml (e.g., SUPABASE_DB_URL, RABBITMQ_URI, queue name).

AC: Required environment variables are passed to the cdc-listener container.

[x] Task 3.5.1: Delete the entire src/data_cdc directory.

AC: The src/data_cdc directory no longer exists.

[x] Task 3.5.2: Delete the old CDC Dockerfile .docker/Dockerfile.data_cdc.

AC: The file .docker/Dockerfile.data_cdc no longer exists.

[x] Task 3.5.3: Remove the old data-cdc service definition from docker-compose.yml.

AC: The data-cdc service definition is removed from docker-compose.yml.

[x] Task 3.6.1: Ensure all necessary configuration for the new cdc-listener (DB URL, MQ URL, MQ queue name, Listen channel name 'data_changes') is present in .env and loaded via src/core/config.py.

AC: Configuration loading includes all parameters needed by the new listener.

[x] Task 3.6.2: Remove any obsolete configuration settings related to MongoDB CDC (e.g., specific Mongo collection names for CDC) from .env and src/core/config.py.

AC: Obsolete MongoDB CDC configuration is removed.

[x] Task 3.2.9: Create a file src/cdc_listener/test_listener.py that performs a complete end-to-end test of the CDC mechanism. The script should:

Establish a connection to the database
Start listening to the data_changes channel in a separate thread/process
Insert test data into each table (articles, posts, repositories) using SQL
Wait for notifications with appropriate timeouts
Log all received notifications
Verify the payload structure and content matches the inserted data
Generate a test report with PASS/FAIL status and detailed diagnostics

AC: The test script produces a comprehensive report showing:

Connection status to database
Listener activation confirmation
Successful data insertion into each table (with record IDs)
Raw notification payloads received for each insert
Validation results comparing payload data with inserted data
Timing metrics (insertion to notification receipt)
Any errors encountered during the process
Overall PASS status only if notifications were correctly received for ALL test inserts

The script should exit with code 0 if all tests pass and non-zero if any test fails, with detailed error information in STDERR.

### Story 4A: Refactor Data Crawlers to FastAPI Endpoints - Schema Models and Link Crawler Endpoint

[x] Task 4.1.1: Create a new file src/api/schemas/crawler.py.

AC: The file src/api/schemas/crawler.py exists.

[x] Task 4.1.2: Define a Pydantic model LinkCrawlRequest in crawler.py with fields like link (HttpUrl) and user_info (e.g., a nested model with platform_user_id or username).

AC: The LinkCrawlRequest Pydantic model is defined for API input validation.

[x] Task 4.1.3: Define a Pydantic model RawTextCrawlRequest in crawler.py with fields like text (str), user_info (same as above), and optional metadata (dict or nested model, e.g., source_platform, original_url).

AC: The RawTextCrawlRequest Pydantic model is defined for API input validation.

[x] Task 4.1.4: Define Pydantic models for API responses, e.g., CrawlSuccessResponse (e.g., {"status": "submitted", "document_id": "..."}) and potentially standard error responses.

AC: Pydantic models for API responses are defined for serialization.

[x] Task 4.2.1: Create a new file src/api/routers/crawling.py.

AC: The file src/api/routers/crawling.py exists.

[x] Task 4.2.2: Initialize a FastAPI APIRouter instance in crawling.py.

AC: An APIRouter is created in crawling.py.

[x] Task 4.2.3: Include the crawling router in the main FastAPI app in src/api/main.py using app.include_router.

AC: Endpoints defined in crawling.py will be accessible via the main application.

[x] Task 4.3.1: Implement a new async function for the POST /crawl/link endpoint in crawling.py. Annotate it with @router.post("/link", response_model=...). It should accept the LinkCrawlRequest model as the request body.

AC: A FastAPI POST endpoint exists at /crawl/link.

[x] Task 4.3.2: Inside the /crawl/link endpoint function, extract user information from the request body. Call the refactored UserDocument.get_or_create (with await) using the user info to get the user ID.

AC: The endpoint correctly retrieves or creates a user record in Supabase based on the request payload.

[x] Task 4.3.3: Instantiate the CrawlerDispatcher from src/data_crawling/dispatcher.py within the endpoint function (or use dependency injection later).

AC: The CrawlerDispatcher is available within the endpoint.

[x] Task 4.3.4: Call dispatcher.get_crawler(link) to determine the appropriate crawler instance based on the input link. Handle cases where no crawler is found (return HTTP 400).

AC: The endpoint correctly identifies the crawler for a given link.

[x] Task 4.3.5: Call the selected crawler's extract(link=link, user=user_id) method (with await as crawler methods interacting with DB should be async). Handle potential exceptions during crawling/extraction (return HTTP 500).

AC: The endpoint successfully invokes the extract method of the appropriate crawler.

[x] Task 4.3.6: Return an appropriate success response (e.g., CrawlSuccessResponse or a simple HTTP 202 Accepted) upon successful scheduling/completion of the crawl extraction.

AC: The /crawl/link endpoint returns a successful HTTP response upon completion.

### Story 4B: Refactor Data Crawlers to FastAPI Endpoints - Raw Text Endpoint and Infrastructure

[x] Task 4.4.1: Implement a new async function for the POST /crawl/raw_text endpoint in crawling.py. Annotate it with @router.post("/raw_text", response_model=...). It should accept the RawTextCrawlRequest model as the request body.

AC: A FastAPI POST endpoint exists at /crawl/raw_text.

[x] Task 4.4.2: Inside the /crawl/raw_text endpoint function, extract user information and call UserDocument.get_or_create (with await) to get the user ID.

AC: The endpoint correctly retrieves or creates a user record in Supabase based on the request payload.

[x] Task 4.4.3: Process the incoming text and metadata. Decide on the target table (e.g., articles with platform='raw' or posts).

AC: The logic determines how to store the raw text within the existing database schema.

[x] Task 4.4.4: Instantiate the appropriate Pydantic document model (e.g., ArticleDocument) with the processed text, metadata, and author_id.

AC: A Pydantic model instance is created representing the raw text input.

[x] Task 4.4.5: Call the refactored save method (with await) from documents.py to persist the document instance to the Supabase database. Handle potential errors (return HTTP 500).

AC: The raw text data is successfully saved to the designated Supabase table.

[x] Task 4.4.6: Return an appropriate success response (e.g., including the ID of the newly created record) from the /crawl/raw_text endpoint.

AC: The /crawl/raw_text endpoint returns a successful HTTP response, and the data persistence triggers the CDC LISTEN/NOTIFY flow.

[x] Task 4.5.1: (Refinement) Refactor crawler/dispatcher instantiation in the API endpoints. Consider creating instances once (e.g., using FastAPI's lifespan events or a simple cache) or using FastAPI's Depends for dependency injection if state management becomes complex.

AC: Crawler/dispatcher instantiation is optimized for the API context.

[x] Task 4.6.1: Delete the AWS Lambda handler specific code (e.g., wrapper functions) within src/data_crawling/main.py or other files.

AC: Lambda-specific handler code is removed from the Python source.

[x] Task 4.6.2: Delete the Dockerfile specifically for the data crawlers Lambda function (.docker/Dockerfile.data_crawlers).

AC: The file .docker/Dockerfile.data_crawlers no longer exists.

[x] Task 4.7.1: Create or update the primary API Dockerfile (e.g., .docker/Dockerfile.api). Ensure it copies all necessary source code (src/api, src/core, src/data_crawling).

AC: The API Dockerfile correctly includes crawler source code.

[x] Task 4.7.2: Ensure the API Dockerfile installs all dependencies, including those required by the crawlers (e.g., requests, beautifulsoup4, specific SDKs).

AC: The API Dockerfile installs dependencies needed for both API serving and crawling logic.

[x] Task 4.7.3: Set the CMD or ENTRYPOINT in the API Dockerfile to run the FastAPI application using uvicorn (e.g., uvicorn src.api.main:app --host 0.0.0.0 --port 80).

AC: The API Dockerfile correctly specifies the command to start the FastAPI server.

[x] Task 4.8.1: Add/Update the api service definition in docker-compose.yml. Configure it to build using the .docker/Dockerfile.api context.

AC: An api service is defined in docker-compose.yml using the correct Dockerfile.

[x] Task 4.8.2: Remove the old data-crawlers service definition (or similar name for the Lambda service) from docker-compose.yml.

AC: The service definition for the old crawler Lambda is removed from docker-compose.yml.

[x] Task 4.8.3: Map the appropriate port for the api service in docker-compose.yml (e.g., 8000:80).

AC: The API service port is correctly mapped in docker-compose.yml.

[x] Task 4.8.4: Ensure the api service in docker-compose.yml has necessary environment variables (e.g., SUPABASE_DB_URL) and potentially depends_on postgres (if local).

AC: The API service is configured with required environment variables and dependencies.

[x] Task 4.9.1: Update the Makefile command local-test-medium (and similar for other platforms) to use curl or a similar tool to send a POST request to http://localhost:8000/crawl/link with the appropriate JSON payload.

AC: The make local-test-medium command successfully calls the new FastAPI endpoint for link crawling.

[x] Task 4.9.2: Update the Makefile command local-ingest-data (if applicable) to use the new API endpoints.

AC: The make local-ingest-data command works with the refactored API.

[x] Task 4.9.3: Add a new Makefile command local-test-raw-text that uses curl to send a POST request to http://localhost:8000/crawl/raw_text with a sample JSON payload containing text and user info.

AC: A make local-test-raw-text command exists and successfully calls the new FastAPI endpoint for raw text ingestion.

### Story 5: Adapt Feature Pipeline (Bytewax)

[x] Task 5.1.1: Review the RabbitMQSource configuration in src/feature_pipeline/main.py. Confirm it reads from the same queue name that the cdc-listener is publishing to (check configuration in core/config.py).

AC: The Bytewax RabbitMQSource is configured to consume from the correct queue populated by the cdc-listener.

[x] Task 5.2.1: Inspect the JSON payload structure defined in the Postgres CDC function (notify_data_change()) created in Task 3.1.1.

AC: The exact structure of the JSON payload sent via pg_notify is known.

[x] Task 5.2.2: Review the Pydantic models defined in src/feature_pipeline/models/raw.py (e.g., RawRecord) that are used to parse the incoming RabbitMQ messages.

AC: The Pydantic models used by Bytewax for message parsing are identified.

[x] Task 5.2.3: Compare the JSON payload structure (from 5.2.1) with the Pydantic model structure (from 5.2.2). Adjust either the notify_data_change() function's payload construction or the Pydantic models in raw.py to ensure they match perfectly. Ensure all fields needed by Bytewax (content, metadata, etc.) are present.

AC: The JSON structure published by the listener matches the Pydantic model expected by the Bytewax pipeline, allowing successful parsing.

[x] Task 5.3.1: Verify that the Qdrant connection details (QDRANT_HOST, QDRANT_PORT, QDRANT_API_KEY if applicable) in .env are correct and loaded properly by src/core/config.py.

AC: Qdrant connection settings are correctly configured.

[x] Task 5.3.2: Confirm that the Bytewax pipeline's Qdrant client (src/feature_pipeline/steps/output.py or similar) uses these configuration settings to connect.

AC: The Bytewax pipeline successfully connects to the configured Qdrant instance.

[ ] Task 5.4.1: (Verification) Run the Bytewax pipeline (make local-start-feature-pipeline) after the cdc-listener has published messages. Observe logs to ensure messages are consumed, processed (cleaned, chunked, embedded), and written to Qdrant without errors related to data format or connection issues.

AC: The Bytewax pipeline runs successfully, processing messages originating from the Postgres CDC and storing results in Qdrant.

### Story 6A: Refactor Inference Pipeline to FastAPI Endpoint - Schema and API Implementation

[x] Task 6.1.1: Create a new file src/api/schemas/inference.py.

AC: The file src/api/schemas/inference.py exists.

[x] Task 6.1.2: Define a Pydantic model InferenceRequest in inference.py with fields like query (str) and optional fields like use_rag (bool, default True), user_id (str, optional).

AC: The InferenceRequest Pydantic model is defined for API input validation.

[x] Task 6.1.3: Define a Pydantic model InferenceResponse in inference.py with fields like answer (str) and optionally context (list[str] or similar, if RAG was used).

AC: The InferenceResponse Pydantic model is defined for API response serialization.

[x] Task 6.2.1: Create a new file src/api/routers/inference.py.

AC: The file src/api/routers/inference.py exists.

[x] Task 6.2.2: Initialize a FastAPI APIRouter instance in inference.py.

AC: An APIRouter is created in inference.py.

[x] Task 6.2.3: Include the inference router in the main FastAPI app in src/api/main.py using app.include_router.

AC: Endpoints defined in inference.py will be accessible via the main application.

[x] Task 6.3.1: Implement a new async function for the POST /generate endpoint in inference.py. Annotate it with @router.post("/generate", response_model=InferenceResponse). It should accept the InferenceRequest model as the request body.

AC: A FastAPI POST endpoint exists at /generate.

[x] Task 6.3.2: Inside the /generate endpoint, instantiate the core logic class (e.g., LLMTwin from src/inference_pipeline/llm_twin.py) or necessary components (model, retriever). (Consider managing this instance via startup events or dependency injection - see Task 6.4).

AC: The core inference logic components are accessible within the endpoint.

[x] Task 6.3.3: Call the main generation method (e.g., llm_twin_instance.generate(query=request.query, use_rag=request.use_rag)). Ensure this method now performs local inference instead of calling SageMaker. Await the result.

AC: The endpoint invokes the core generation logic using the request parameters.

[x] Task 6.3.4: Adapt the Opik tracking. If @opik.track was used on the original generate method, ensure it still works. If tracking was manual, ensure the necessary Opik context managers or function calls are made within the endpoint function, capturing the request (query) and response (answer, context).

AC: Requests to the /generate endpoint are correctly tracked in Opik with relevant inputs and outputs.

[x] Task 6.3.5: Format the result from the generation method into the InferenceResponse Pydantic model and return it. Handle potential errors during generation (return HTTP 500).

AC: The /generate endpoint returns the generated answer and context (if applicable) in the specified response format.

### Story 6B: Refactor Inference Pipeline to FastAPI Endpoint - Model Loading and Infrastructure

[x] Task 6.4.1 (Model Loading - Option A: Startup Event): Define startup and potentially shutdown event handlers in src/api/main.py. In the startup handler, load the fine-tuned LLM model (using transformers, unsloth, etc.) and the RAG retriever (Qdrant client) and store them globally or attached to the app state (e.g., app.state.llm, app.state.retriever).

AC: The LLM model and retriever are loaded once when the FastAPI application starts.

[x] Task 6.4.2 (Model Loading - Option B: Singleton/DI): Implement a singleton pattern or use a class-based dependency for the LLMTwin logic or its components (model, retriever) that ensures they are loaded only once when first requested by an endpoint. (Superseded by 6.4.1)

AC: The LLM model and retriever are loaded efficiently, avoiding reloading on every request.

[x] Task 6.4.3: Refactor src/inference_pipeline/llm_twin.py (or wherever model prediction occurs). Remove the build_sagemaker_predictor method or any code instantiating sagemaker.huggingface.model.HuggingFacePredictor.

AC: SageMaker predictor instantiation code is removed.

[x] Task 6.4.4: Replace calls like self.\_llm_endpoint.predict(...) with direct calls to the loaded model's generation method (e.g., model.generate(...) or pipeline(...) from the transformers library, or Unsloth's inference methods). Ensure input formatting matches the local model's requirements.

AC: Inference calls are made directly to the locally loaded model object.

[x] Task 6.5.1: Update src/inference_pipeline/config.py and potentially src/core/config.py. Remove the SAGEMAKER_ENDPOINT_NAME setting.

AC: SageMaker endpoint configuration is removed.

[x] Task 6.5.2: Verify that settings required for local inference are present and correctly loaded: Hugging Face model ID (MODEL_ID), Hugging Face token (HF_TOKEN if needed for private models), device mapping (cuda, cpu), RAG parameters (chunk size, embedding model), Qdrant connection details.

AC: All necessary configurations for local inference and RAG are correctly loaded.

[x] Task 6.6.1: Delete the Python script src/inference_pipeline/aws/deploy_sagemaker_endpoint.py.

AC: The SageMaker deployment script is removed.

[x] Task 6.6.2: Delete the Python script src/inference_pipeline/aws/delete_sagemaker_endpoint.py.

AC: The SageMaker deletion script is removed.

[x] Task 6.6.3: Remove any remaining imports or usage of the deleted AWS scripts or SageMaker client libraries within the src/inference_pipeline module.

AC: Codebase no longer references SageMaker deployment/deletion scripts or SageMaker predictor classes.

[x] Task 6.7.1: Update the API Dockerfile (.docker/Dockerfile.api). Add dependencies required for inference: torch, transformers, unsloth (if used), qdrant-client, sentence-transformers (or other embedding model library), opik-sdk. Ensure correct versions compatible with the model.

AC: Inference-related Python dependencies are added to the API Dockerfile installation steps.

[x] Task 6.7.2: Ensure the API Dockerfile includes the source code from src/inference_pipeline.

AC: The API Dockerfile copies the inference pipeline source code into the image.

[x] Task 6.7.3: Plan for model weight handling. Options:

Option 1 (Download at build): Add RUN commands in the Dockerfile to download model weights during the image build (increases image size). Use HF_HUB_CACHE to manage cache location.

Option 2 (Download at runtime): Ensure the runtime environment has internet access and sufficient disk space for the model to be downloaded on first startup (using the startup event handler from Task 6.4.1).

Option 3 (Mount volume): Assume model weights are pre-downloaded and mounted into the container at runtime (requires external process/volume management).

AC: A strategy for handling model weights within the Docker container is chosen and implemented in the Dockerfile or runtime logic.

### Story 6C: Refactor Inference Pipeline to FastAPI Endpoint - UI Integration

[x] Task 6.8.1: Remove the deploy-inference-pipeline command from the Makefile.

AC: The deploy-inference-pipeline Make target is removed.

[x] Task 6.8.2: Remove the delete-inference-pipeline-deployment command from the Makefile.

AC: The delete-inference-pipeline-deployment Make target is removed.

[x] Task 6.8.3: Modify the call-inference-pipeline command in the Makefile to use curl to send a POST request to http://localhost:8000/generate with a sample InferenceRequest JSON payload.

AC: The make call-inference-pipeline command successfully calls the new FastAPI inference endpoint.

[x] Task 6.8.4: Refactor the Gradio UI script (src/inference_pipeline/ui.py). Update the function that handles user input and generates the response. Instead of calling LLMTwin().generate() directly or using boto3 to call SageMaker, it should now use a library like requests or httpx to make a POST request to the FastAPI /generate endpoint (http://api:80/generate if running via Docker Compose, or http://localhost:8000/generate if run locally). Parse the JSON response to display the answer.

AC: Running make local-start-ui launches the Gradio UI, and interacting with it successfully calls the FastAPI /generate backend endpoint to get responses.

[x] Task 6.8.5: Review evaluation scripts (evaluate-llm, evaluate-rag, etc.). If they relied on the SageMaker endpoint, update them to either: a) Instantiate the LLMTwin logic directly (if feasible), or b) Call the FastAPI /generate endpoint. (No changes needed as scripts already used local LLMTwin or evaluated logged data).

AC: Evaluation scripts are updated to work with the refactored local/FastAPI inference setup.

Story 7: Replace Local Inference with External LLM API
Goal: Modify the inference pipeline to use an external LLM API (e.g., OpenAI) instead of the locally loaded Hugging Face model, following SOLID and DRY principles.

7.1: Define LLM Interaction Interface (OCP, DIP)
[x] Task 7.1.1: Create a new directory src/core/llm_clients/.
AC: The directory src/core/llm_clients/ exists.

[x] Task 7.1.2: Create a new file src/core/llm_clients/**init**.py.
AC: The file src/core/llm_clients/**init**.py exists and is empty.

[x] Task 7.1.3: Create a new file src/core/llm_clients/base.py.
AC: The file src/core/llm_clients/base.py exists.

[x] Task 7.1.4: In src/core/llm_clients/base.py, import necessary modules: from abc import ABC, abstractmethod, from typing import List, Dict, Any.
AC: Imports are correctly added to src/core/llm_clients/base.py.

[x] Task 7.1.5: In src/core/llm_clients/base.py, define an abstract base class LLMClientInterface(ABC).
AC: The class LLMClientInterface inheriting from ABC is defined.

[x] Task 7.1.6: In src/core/llm_clients/base.py, define an abstract async method generate within LLMClientInterface with the signature async def generate(self, messages: List[Dict[str, str]], \*\*kwargs: Any) -> str:. Add a docstring explaining its purpose (to take formatted messages and return the LLM's text response).
AC: The abstract async method generate with the specified signature and docstring exists within LLMClientInterface.

7.2: Implement OpenAI Client (SRP)
[x] Task 7.2.1: Create a new file src/core/llm_clients/openai_client.py.
AC: The file src/core/llm_clients/openai_client.py exists.

[x] Task 7.2.2: In src/core/llm_clients/openai_client.py, import necessary modules: import openai, import logging, from typing import List, Dict, Any, from .base import LLMClientInterface, from ..config import settings.
AC: Imports are correctly added to src/core/llm_clients/openai_client.py.

[x] Task 7.2.3: In src/core/llm_clients/openai_client.py, get a logger instance: logger = logging.getLogger(**name**).
AC: Logger instance is created.

[x] Task 7.2.4: In src/core/llm_clients/openai_client.py, define a class OpenAIClient that inherits from LLMClientInterface.
AC: The class OpenAIClient(LLMClientInterface) is defined.

[x] Task 7.2.5: Implement the **init** method for OpenAIClient. It should check if settings.OPENAI_API_KEY exists, raise ValueError if not, and initialize self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY). Add logging for initialization.
AC: **init** method correctly initializes the async OpenAI client and handles missing API key.

[x] Task 7.2.6: Implement the async generate method in OpenAIClient conforming to the LLMClientInterface.
AC: The async generate method signature matches the interface.

[x] Task 7.2.7: Inside async generate, implement a try...except block to handle potential OpenAI API errors (openai.APIError, openai.RateLimitError, openai.AuthenticationError, openai.APIConnectionError, Exception). Log errors appropriately.
AC: Robust error handling for OpenAI API calls is implemented with logging.

[x] Task 7.2.8: Inside the try block of async generate, make an asynchronous call to self.client.chat.completions.create().
AC: Asynchronous API call to OpenAI chat completions endpoint is made.

[x] Task 7.2.9: Pass the messages list to chat.completions.create(). Use settings.OPENAI_MODEL_ID for the model parameter. Pass relevant generation parameters from kwargs or use defaults (e.g., temperature=0.7, max_tokens=512).
AC: messages, model, and generation parameters are correctly passed to the API call.

[x] Task 7.2.10: Extract the generated text content from the first choice in the API response (response.choices[0].message.content). Handle cases where the response might be empty or malformed.
AC: Generated text is correctly extracted from the API response.

[x] Task 7.2.11: Return the extracted text string from async generate. If an error occurred, return an informative error message or re-raise a custom exception.
AC: The method returns the generated string on success or handles errors appropriately.

[x] Task 7.2.12: In src/core/llm_clients/**init**.py, add from .base import LLMClientInterface and from .openai_client import OpenAIClient. Add **all** = ["LLMClientInterface", "OpenAIClient"].
AC: Exports are correctly set up in src/core/llm_clients/**init**.py.

7.3: Update Configuration
[x] Task 7.3.1: In src/core/config.py, within the AppSettings class, ensure OPENAI_API_KEY: str | None = None and OPENAI_MODEL_ID: str = "gpt-4o-mini" (or similar default) exist.
AC: AppSettings contains the necessary OpenAI configuration variables.

[x] Task 7.3.2: In src/core/config.py (AppSettings), remove or comment out MODEL_ID if it specifically referred to the fine-tuned Hugging Face model ID. Keep it if it refers to a base model potentially used elsewhere, or rename if ambiguous.
AC: Obsolete local model ID configuration is removed or clarified in AppSettings.

[x] Task 7.3.3: In src/core/config.py (AppSettings), remove TRUST_REMOTE_CODE: bool = False.
AC: TRUST_REMOTE_CODE configuration is removed from AppSettings.

[x] Task 7.3.4: In src/inference_pipeline/config.py, remove the entire Settings class or comment out all its contents, as configuration should primarily be managed in src/core/config.py. Ensure no code imports from src/inference_pipeline/config.py.
AC: src/inference_pipeline/config.py is effectively removed or deprecated, and no code relies on it.

[x] Task 7.3.5: Review src/core/config.py and remove any remaining settings solely related to local model loading/inference (e.g., potentially HF_TOKEN if not needed for other purposes like private dataset access).
AC: Core configuration is free of obsolete local inference settings.

[x] Task 7.3.6: Update .env.example to include OPENAI_API_KEY=your_openai_api_key_here and OPENAI_MODEL_ID=gpt-4o-mini (or chosen model).
AC: .env.example includes necessary OpenAI variables.

[x] Task 7.3.7: Update .env.example to remove TRUST_REMOTE_CODE, and potentially MODEL_ID and HF_TOKEN if they were only for the local fine-tuned model. Remove SAGEMAKER_ENDPOINT_NAME.
AC: .env.example is cleaned of obsolete local inference and SageMaker variables.

7.4: Refactor Inference Logic (LLMTwin)
[x] Task 7.4.1: In src/inference_pipeline/llm_twin.py, remove the llm_pipeline and tokenizer parameters from the generate method signature.
AC: generate method signature in LLMTwin is updated.

[x] Task 7.4.2: In src/inference_pipeline/llm_twin.py, remove the llm_pipeline and tokenizer parameters from the call_llm_service method signature.
AC: call_llm_service method signature in LLMTwin is updated.

[x] Task 7.4.3: In src/inference_pipeline/llm_twin.py (generate method), add a new parameter llm_client: LLMClientInterface (import LLMClientInterface from src.core.llm_clients).
AC: generate method now accepts an LLMClientInterface instance.

[x] Task 7.4.4: In src/inference_pipeline/llm_twin.py (generate method), pass the llm_client instance to the call_llm_service method call.
AC: llm_client is passed down to call_llm_service.

[x] Task 7.4.5: In src/inference_pipeline/llm_twin.py (call_llm_service method), add the llm_client: LLMClientInterface parameter to its signature.
AC: call_llm_service signature now accepts the client instance.

[x] Task 7.4.6: In src/inference_pipeline/llm_twin.py (call_llm_service method), remove all code related to tokenizer.apply_chat_template, calculating input_token_count, calculating max_new_tokens, and calling llm_pipeline(...).
AC: Local model execution logic is completely removed from call_llm_service.

[x] Task 7.4.7: In src/inference_pipeline/llm_twin.py (call_llm_service method), add an await call to llm_client.generate(messages=messages). Store the result in the answer variable.
AC: The method now calls the generate method of the injected llm_client.

[x] Task 7.4.8: In src/inference_pipeline/llm_twin.py (call_llm_service method), remove the self.\_mock check or adapt it if mocking external calls is still desired (potentially by injecting a mock client). For now, assume removal. Remove the mock: bool parameter from generate if self.\_mock usage is removed.
AC: Local mocking logic based on self.\_mock is removed.

[x] Task 7.4.9: In src/inference_pipeline/llm_twin.py (generate method), update the opik_context.update_current_trace metadata to use settings.OPENAI_MODEL_ID instead of settings.MODEL_ID. Remove embedding_model_id if it's not relevant here or move it to RAG context. Adjust token calculation logic if necessary (input tokens are now based on the formatted prompt before sending to the API, output tokens might need estimation or retrieval if the API provides it). For simplicity, can remove token counts if not critical or reliably obtained.
AC: Opik trace metadata is updated for the external model, token calculation adjusted/removed.

[x] Task 7.4.10: In src/inference_pipeline/llm_twin.py, remove the unused imports pipeline, AutoTokenizer, PreTrainedTokenizerBase, Pipeline, QdrantClient. Add import for LLMClientInterface.
AC: Unused imports related to local models are removed, necessary client interface imported.

7.5: Integrate Client into API Layer
[x] Task 7.5.1: In src/api/main.py, import OpenAIClient from src.core.llm_clients.
AC: OpenAIClient is imported in main.py.

[x] Task 7.5.2: In src/api/main.py, modify the lifespan context manager's startup phase:

- Initialize app.state.llm_client = None.
- Add a try...except block to instantiate app.state.llm_client = OpenAIClient().
- Log success or failure of client initialization.
- Remove the loading logic for app.state.llm_pipeline and app.state.tokenizer.
- Keep the Qdrant client loading logic.
  AC: OpenAIClient is instantiated on startup and stored in app.state, local model loading is removed.

[x] Task 7.5.3: In src/api/main.py, modify the lifespan context manager's shutdown phase:

- Remove the deletion logic for app.state.llm_pipeline and app.state.tokenizer.
- Add logic to potentially close the OpenAIClient if its underlying library requires it (e.g., await app.state.llm_client.close() if implemented), though often not needed for HTTP clients. Add logging.
  AC: API shutdown logic is updated to remove local model cleanup and potentially add external client cleanup.

[x] Task 7.5.4: In src/api/routers/inference.py, remove the retrieval of llm_pipeline and tokenizer from request_obj.app.state.
AC: Code accessing local model/tokenizer from app state is removed.

[x] Task 7.5.5: In src/api/routers/inference.py, retrieve the LLM client: llm_client = request_obj.app.state.llm_client.
AC: The external LLM client is retrieved from app state.

[x] Task 7.5.6: In src/api/routers/inference.py, add a check: if not llm_client: raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LLM service is not ready.").
AC: A check ensures the LLM client was successfully initialized on startup.

[x] Task 7.5.7: In src/api/routers/inference.py, update the call to llm_twin_instance.generate to pass the retrieved llm_client: result = await llm_twin_instance.generate(..., llm_client=llm_client).
AC: The llm_client instance is passed to the generate method.

7.6: Update Dependencies
[x] Task 7.6.1: In pyproject.toml, under [tool.poetry.dependencies], remove torch, transformers, accelerate. Remove unsloth if present.
AC: Local model dependencies are removed from pyproject.toml.

[x] Task 7.6.2: In pyproject.toml, under [tool.poetry.dependencies], add openai = "^<latest_version>". Check and add httpx if the openai library requires it explicitly or for other async calls. Keep requests if used by the UI.
AC: OpenAI client library dependency is added to pyproject.toml.

[x] Task 7.6.3: Run poetry lock --no-update in the terminal.
AC: Poetry lock file is updated to reflect dependency changes.

[x] Task 7.6.4: Run make install or poetry install in the terminal.
AC: Project dependencies are updated in the virtual environment.

7.7: Update Docker Configuration
[x] Task 7.7.1: In .docker/Dockerfile.api, remove any RUN commands related to downloading Hugging Face models (e.g., using huggingface-cli download or Python scripts).
AC: Dockerfile no longer attempts to download local model weights.

[x] Task 7.7.2: Verify that the poetry install command in .docker/Dockerfile.api correctly installs the new dependencies (openai) and excludes the removed ones (torch, transformers, etc.).
AC: Dockerfile installs the correct set of dependencies.

[x] Task 7.7.3: In docker-compose.yml, review the api service definition. Consider reducing allocated resources (e.g., remove deploy.resources.reservations.devices if GPU was reserved) unless RAG processing is resource-intensive.
AC: Resource allocation for the api service in docker-compose.yml is reviewed and potentially adjusted.

7.8: Update UI and Testing
[x] Task 7.8.1: In src/inference_pipeline/ui.py, review the predict function. It already uses requests to call the /generate endpoint. Ensure the API_ENDPOINT variable points correctly to the FastAPI service (e.g., http://api:80 within Docker Compose or http://localhost:8000 locally). No major changes likely needed here as it interacts via API.
AC: Gradio UI correctly calls the updated FastAPI /generate endpoint.

[x] Task 7.8.2: In Makefile, verify the call-inference-pipeline command correctly sends a POST request to the /generate endpoint. No changes likely needed.
AC: Makefile command call-inference-pipeline works with the modified backend.

[x] Task 7.8.3: In src/inference_pipeline/main.py (if used for standalone testing), update it to instantiate and use the OpenAIClient instead of the local transformers pipeline.
AC: Standalone inference test script (src/inference_pipeline/main.py) is updated to use the new client, or is removed if obsolete.

Story 8: Remove Training Pipeline and Associated Components
Goal: Eliminate all code, configuration, dependencies, evaluation artifacts, and documentation related to fine-tuning the local model.

8.1: Delete Training Source Code
[x] Task 8.1.1: Delete the entire directory src/training_pipeline/.
AC: The directory src/training_pipeline/ no longer exists.

[x] Task 8.1.2: Delete the entire directory src/feature_pipeline/generate_dataset/.
AC: The directory src/feature_pipeline/generate_dataset/ no longer exists.

[x] Task 8.1.3: Delete the file src/core/aws/create_sagemaker_role.py.
AC: The file src/core/aws/create_sagemaker_role.py no longer exists.

[x] Task 8.1.4: Delete the directory src/inference_pipeline/aws/ if it exists and contains SageMaker deployment/deletion scripts for the fine-tuned model.
AC: The directory src/inference_pipeline/aws/ and its contents (if any) are removed.

[x] Task 8.1.5: Search the entire src/ directory for any remaining imports from src.training_pipeline, src.feature_pipeline.generate_dataset, or src.core.aws.create_sagemaker_role and remove them. Check files like src/core/**init**.py, src/feature_pipeline/main.py, etc.
AC: No dangling imports from deleted training modules remain in the codebase.

8.2: Clean Configuration
[x] Task 8.2.1: In src/core/config.py (AppSettings), remove the DATASET_ID variable (related to Comet artifact for training).
AC: DATASET_ID is removed from AppSettings.

[x] Task 8.2.2: In src/core/config.py (AppSettings), remove the AWS_ARN_ROLE variable if its sole purpose was SageMaker training/deployment. If used for other AWS services, keep it.
AC: AWS_ARN_ROLE is removed from AppSettings if it was only for SageMaker training/deployment.

[x] Task 8.2.3: In .env.example, remove the lines for DATASET_ID and potentially AWS_ARN_ROLE (matching the changes in AppSettings).
AC: .env.example is cleaned of training-specific variables.

[x] Task 8.2.4: Delete the file sagemaker_execution_role.json from the project root if it exists. Add sagemaker_execution_role.json to .gitignore.
AC: The generated SageMaker role file is deleted and ignored.

8.3: Remove Training Dependencies
[x] Task 8.3.1: In pyproject.toml, under [tool.poetry.dependencies], remove datasets (if only used for loading training data), peft, trl, bitsandbytes. Remove unsloth if it was used specifically for fine-tuning support.
AC: Training-specific dependencies are removed from pyproject.toml.

[x] Task 8.3.2: In pyproject.toml, check if flash-attn was added for training; if so, remove it.
AC: flash-attn dependency is removed if it was only for training.

[x] Task 8.3.3: Run poetry lock --no-update in the terminal.
AC: Poetry lock file is updated to reflect removed dependencies.

[x] Task 8.3.4: Run make install or poetry install in the terminal.
AC: Training dependencies are removed from the virtual environment.

8.4: Clean Makefile
[x] Task 8.4.1: In Makefile, delete the targets: start-training-pipeline-dummy-mode, start-training-pipeline, local-start-training-pipeline.
AC: Makefile targets for starting training are removed.

[x] Task 8.4.2: In Makefile, delete the target: download-instruct-dataset.
AC: Makefile target for downloading the instruct dataset is removed.

[x] Task 8.4.3: In Makefile, delete the target: create-sagemaker-execution-role.
AC: Makefile target for creating the SageMaker role is removed.

[x] Task 8.4.4: In Makefile, delete the target: local-generate-instruct-dataset.
AC: Makefile target for generating the instruct dataset is removed.

[x] Task 8.4.5: If deploy-inference-pipeline and delete-inference-pipeline-deployment targets existed specifically for deploying the fine-tuned model via SageMaker (as opposed to a generic API deployment), delete them. (Based on previous refactoring, these might already be gone or repurposed).
AC: Obsolete SageMaker deployment targets for the fine-tuned model are removed from Makefile.

8.5: Adapt Evaluation Scripts
[x] Task 8.5.1: In src/inference_pipeline/evaluation/evaluate.py (main function):

- Remove the call to create_dataset_from_artifacts. Evaluation should perhaps run on a standard benchmark dataset or a curated set of prompts not tied to the old training artifacts.
- Define a new static list of evaluation prompts/inputs, or load from a simple file/benchmark dataset.
- Update the evaluation_task function to call the inference API endpoint (requests.post) or instantiate and use OpenAIClient directly (passing the necessary input from the new evaluation data source). Ensure enable_rag=False.
- Remove metrics that relied heavily on comparing against the fine-tuning data (e.g., LevenshteinRatio might be less relevant). Keep metrics like Hallucination, Moderation, Style.
- Update experiment_config to reflect the external model ID (e.g., settings.OPENAI_MODEL_ID).
  AC: evaluate.py is adapted to use the external LLM, a suitable evaluation dataset (not training artifacts), and relevant metrics.

[x] Task 8.5.2: In src/inference_pipeline/evaluation/evaluate_rag.py (main function):

- Remove the call to create_dataset_from_artifacts. Use the same new evaluation data source as in evaluate.py.
- Update the evaluation_task function: It needs to perform RAG retrieval (instantiate VectorRetriever, call retrieve_top_k, rerank) and then call the external LLM API/client with the query and retrieved context. Ensure enable_rag=True equivalent logic is applied.
- Keep RAG-specific metrics (ContextRecall, ContextPrecision). Keep Hallucination as well.
- Update experiment_config.
  AC: evaluate_rag.py is adapted to use the external LLM with RAG, a suitable evaluation dataset, and relevant metrics.

[x] Task 8.5.3: In src/inference_pipeline/evaluation/evaluate_monitoring.py:

- Verify the evaluation_task correctly extracts query, context, and output from the format logged by Opik for the new API calls. Adjust parsing if needed.
- Ensure metrics (Hallucination, Moderation, AnswerRelevance, Style) are appropriate for evaluating production logs from the external LLM.
- Update experiment_config.
  AC: evaluate_monitoring.py correctly processes logs from the new inference setup and uses relevant metrics.

[x] Task 8.5.4: Review src/core/opik_utils.py:

- Remove the create_dataset_from_artifacts function as it relies on training artifacts.
- Check if add_to_dataset_with_sampling is still needed for monitoring dataset creation; if so, ensure the dataset_name used matches the one expected by evaluate_monitoring.py.
  AC: opik_utils.py is cleaned of functions dependent on training artifacts.

  8.6: Update Documentation
  [x] Task 8.6.1: In README.md:

- Remove the "Training Pipeline" section/component from the architecture diagram and description.
- In the "Lessons" table, remove or mark as deprecated/removed the lessons specifically about generating instruct datasets and the fine-tuning pipeline (Lessons 6, 7). Update descriptions of related lessons (like Evaluation, Inference) if needed.
- Remove src/training_pipeline/ and src/feature_pipeline/generate_dataset/ from the Project Structure description.
- Search for and remove any mentions of fine-tuning, LoRA, QLoRA, instruct datasets, SageMaker training jobs.
  AC: README.md accurately reflects the removal of the training pipeline in architecture, lessons, and structure sections.

[x] Task 8.6.2: In INSTALL_AND_USAGE.md:

- Remove the section "Step 5: Generating the instruct dataset".
- Remove the section "Step 6: Setting up AWS SageMaker" entirely, including creating the execution role.
- Remove the section "Step 7: Starting the fine-tuning pipeline".
- Update the "Configure" section to remove mentions of AWS_ARN_ROLE (if removed from src.core config) and DATASET_ID. Ensure OPENAI_API_KEY setup is clear.
- Update the "Cloud Services" table to remove SageMaker for training.
- Remove dependencies listed for training (e.g., needing specific AWS permissions for training roles).
- Update the evaluation steps (like "Step 8: Runing the evaluation pipelines") to reflect the changes made (e.g., no longer relying on instruct dataset artifacts).
- Ensure all AWS/SageMaker references related to training or deploying the fine-tuned model are removed.
  AC: INSTALL_AND_USAGE.md is updated to remove all setup, configuration, and usage instructions related to the training pipeline and its artifacts/infrastructure.

### Story 9A: Final Cleanup, Testing & Configuration

[ ] Task 9.1.1: Review .env.example and ensure it reflects all necessary environment variables for the new stack (Supabase URL, RabbitMQ URI, Qdrant Host/Port, HF Model ID, etc.) and remove all obsolete variables (Mongo URI, SageMaker Endpoint).

AC: .env.example accurately lists all required configuration variables for the refactored application.

[ ] Task 9.1.2: Review all configuration loading logic in src/core/config.py and any service-specific config files (src/\*/config.py). Ensure consistency, remove unused settings, and verify defaults are sensible.

AC: Configuration loading code is clean, consistent, and only loads necessary settings.

[ ] Task 9.2.1: Perform a final review of docker-compose.yml. Check service names (api, cdc-listener, feature-pipeline, mq, qdrant, postgres or external Supabase config), build contexts, image names, environment variables, port mappings, volumes, and depends_on relationships.

AC: docker-compose.yml accurately defines the services, dependencies, and configurations for the complete refactored stack.

[ ] Task 9.2.2: Ensure resource limits (memory, CPU) are considered or added to docker-compose.yml services if needed, especially for the api service running the LLM.

AC: Resource allocation in docker-compose.yml is reviewed and potentially adjusted.

[ ] Task 9.3.1: Perform a final review of the Makefile. Verify that install, local-start, local-stop, local-logs, local-test-_, call-inference-pipeline, local-start-ui, evaluate-_ commands work correctly with the new structure.

AC: All primary Makefile commands function as expected against the refactored application.

[ ] Task 9.3.2: Remove any obsolete Makefile commands related to MongoDB, old CDC, Lambda deployment, or SageMaker deployment.

AC: Obsolete commands are removed from the Makefile.

[ ] Task 9.4.1: Write unit tests for the src/core/db/supabase_client.py functions (mocking the actual DB connection).

AC: Unit tests verify the basic functionality of the Supabase client module.

[ ] Task 9.4.2: Write unit tests for the src/cdc_listener/listener.py logic (mocking DB connection/notifications and MQ publishing). Test payload parsing and publishing logic.

AC: Unit tests verify the core logic of the CDC listener service.

[ ] Task 9.4.3: Write unit/integration tests for the FastAPI endpoints in src/api/routers/crawling.py. Use FastAPI's TestClient. Mock external calls (crawler extraction, DB saves) for unit tests, or use a test database for integration tests.

AC: Unit/integration tests verify the behavior of the crawler API endpoints.

[ ] Task 9.4.4: Write unit/integration tests for the FastAPI endpoint in src/api/routers/inference.py. Use TestClient. Mock the LLM generation and RAG retrieval for unit tests.

AC: Unit/integration tests verify the behavior of the inference API endpoint.

[ ] Task 9.5.1: Execute end-to-end test scenario 1:

Start all services (make local-start).

Call make local-test-medium (or similar crawler test).

Verify data appears in the corresponding Supabase table (articles, users).

Check cdc-listener logs for notification received and published message.

Check feature-pipeline logs for message consumed and processed.

Verify embeddings appear in Qdrant for the new content.

Call make call-inference-pipeline with a relevant query and use_rag=True.

Verify the response includes content derived from the newly ingested article.

AC: End-to-end data flow from link ingestion through RAG-based inference is successful.

[ ] Task 9.5.2: Execute end-to-end test scenario 2:

Start all services (make local-start).

Call make local-test-raw-text.

Verify data appears in the designated Supabase table (articles or posts, users).

Check cdc-listener logs for notification received and published message.

Check feature-pipeline logs for message consumed and processed.

Verify embeddings appear in Qdrant for the new content.

Call make call-inference-pipeline with a relevant query and use_rag=True.

Verify the response includes content derived from the newly ingested raw text.

AC: End-to-end data flow from raw text ingestion through RAG-based inference is successful.

### Story 9B: Documentation Updates

[ ] Task 9.6.1: Update the Architecture Overview section in README.md to describe the new components (Supabase, FastAPI, Postgres CDC Listener). Remove mentions of MongoDB, Lambda, SageMaker endpoint.

AC: README accurately reflects the refactored architecture.

[ ] Task 9.6.2: Update any architecture diagrams referenced or included in the documentation.

AC: Architecture diagrams are updated to match the new flow.

[ ] Task 9.6.3: Update the Setup/Installation instructions in README.md to include Supabase setup (local or cloud) and remove MongoDB setup.

AC: README setup instructions are correct for the new architecture.

[ ] Task 9.7.1: Update INSTALL_AND_USAGE.md. Modify dependency installation steps if necessary (e.g., system dependencies for psycopg2).

AC: Installation dependencies in INSTALL_AND_USAGE.md are correct.

[ ] Task 9.7.2: Update INSTALL_AND_USAGE.md. Add instructions for setting up Supabase (connecting to cloud or running local Docker). Include details on obtaining the DB URL. Remove MongoDB setup instructions.

AC: Database setup instructions in INSTALL_AND_USAGE.md are correct for Supabase.

[ ] Task 9.7.3: Update INSTALL_AND_USAGE.md. Modify usage examples (e.g., how to trigger ingestion, how to call inference) to use the new Makefile commands or direct curl calls to the FastAPI endpoints. Remove examples using Lambda invocation or direct SageMaker calls.

AC: Usage examples in INSTALL_AND_USAGE.md correctly demonstrate interaction with the refactored application via FastAPI.

[ ] Task 9.7.4: Review INSTALL_AND_USAGE.md for any remaining references to AWS Lambda or AWS SageMaker endpoints in the context of core application deployment/usage (training pipeline usage might still involve SageMaker jobs, which is outside this refactoring's scope).

AC: INSTALL_AND_USAGE.md is free of obsolete deployment/usage instructions related to Lambda/SageMaker endpoints for crawling and inference serving.

Story 10: Define Embedding Client Abstraction
Goal: Create a standard interface for embedding generation, decoupling high-level modules from specific implementations.

Task 10.1.1: Create the directory src/core/embedding_clients.

AC: The directory src/core/embedding_clients exists.

Task 10.1.2: Inside src/core/embedding_clients, create a new file named base.py.

AC: The file src/core/embedding_clients/base.py exists.

Task 10.1.3: In src/core/embedding_clients/base.py, import necessary modules: abc (ABC, abstractmethod), typing (Any, List).

AC: Imports from abc import ABC, abstractmethod and from typing import Any, List are present in base.py.

Task 10.1.4: Define an abstract base class EmbeddingClientInterface inheriting from ABC in src/core/embedding_clients/base.py.

AC: class EmbeddingClientInterface(ABC): exists in base.py.

Task 10.1.5: Define an abstract asynchronous method embed within EmbeddingClientInterface.

Signature: async def embed(self, texts: List[str], \*\*kwargs: Any) -> List[List[float]]:

Decorate it with @abstractmethod.

AC: The abstract method embed with the correct signature and decorator exists in EmbeddingClientInterface.

Task 10.1.6: Add a clear docstring to the embed method explaining its purpose, arguments (especially texts for batching), return value (list of embedding vectors), and its asynchronous nature.

AC: The embed method has a comprehensive docstring.

Task 10.1.7: Create/Update the **init**.py file in src/core/embedding_clients/ to export the interface.

Add: from .base import EmbeddingClientInterface

Add: **all** = ["EmbeddingClientInterface"]

AC: src/core/embedding_clients/**init**.py exists and exports EmbeddingClientInterface.

Story 11: Implement Concrete OpenAI Embedding Client
Goal: Create a specific client implementation to interact with the OpenAI embedding API.

Task 11.1.1: Inside src/core/embedding_clients, create a new file named openai_client.py.

AC: The file src/core/embedding_clients/openai_client.py exists.

Task 11.1.2: In openai_client.py, import necessary modules: logging, typing (Any, Dict, List), openai, settings from src.core.config, and EmbeddingClientInterface from .base.

AC: All required imports are present in openai_client.py.

Task 11.1.3: Get a logger instance in openai_client.py (e.g., logger = logging.getLogger(**name**)).

AC: A logger is initialized in the module.

Task 11.1.4: Define the class OpenAIEmbeddingClient inheriting from EmbeddingClientInterface.

AC: class OpenAIEmbeddingClient(EmbeddingClientInterface): exists.

Task 11.2.1: Implement the **init** method for OpenAIEmbeddingClient.

Log the initialization start.

Check if settings.OPENAI_API_KEY is set. If not, log an error and raise a ValueError with a clear message.

Instantiate the openai.AsyncOpenAI client using the API key from settings and store it as self.client.

Wrap the client instantiation in a try...except block to catch potential errors during initialization (e.g., invalid key format), log the error, and re-raise.

Log successful initialization.

AC: **init** correctly initializes the openai.AsyncOpenAI client, checks for the API key, and includes logging and error handling.

Task 11.3.1: Implement the async def embed(self, texts: List[str], \*\*kwargs: Any) -> List[List[float]] method in OpenAIEmbeddingClient.

AC: The embed method exists with the correct signature matching the interface.

Task 11.3.2: Inside embed, add a check for an empty texts list. If empty, log a warning and return an empty list [].

AC: The method handles empty input gracefully.

Task 11.3.3: Log the start of the API call, mentioning the model ID being used (read from settings.OPENAI_EMBEDDING_MODEL_ID - Requires adding this setting in Story 14).

AC: Logging indicates the model being used.

Task 11.3.4: Prepare the parameters for the OpenAI API call. Use settings.OPENAI_EMBEDDING_MODEL_ID for the model parameter. Merge any kwargs passed to the method (allowing overrides).

AC: API parameters include the correct model ID.

Task 11.3.5: Call await self.client.embeddings.create(model=..., input=texts, \*\*generation_params).

AC: The asynchronous OpenAI API call is made correctly.

Task 11.3.6: Wrap the API call in a try...except block to handle specific openai exceptions (AuthenticationError, RateLimitError, APIConnectionError, APIError, InvalidRequestError) and generic Exception. Log errors clearly, mentioning the type of error, and re-raise a generic Exception containing the original error message.

AC: Robust error handling for OpenAI API calls is implemented.

Task 11.3.7: Process the successful response:

Check if response.data exists and is a list.

Iterate through the response.data list. For each item, check if it has an embedding attribute which is a list of floats.

Extract all embedding lists into a new list List[List[float]].

If the response structure is unexpected or data is missing, log an error and raise an Exception.

Log successful reception and parsing of embeddings.

Return the extracted list of embeddings.

AC: The API response is correctly parsed, validated, and returned in the format List[List[float]].

Task 11.4.1: Update src/core/embedding_clients/**init**.py to also export the concrete client.

Add: from .openai_client import OpenAIEmbeddingClient

Update: **all** = ["EmbeddingClientInterface", "OpenAIEmbeddingClient"]

AC: **init**.py exports both the interface and the OpenAI implementation.

Story 12: Refactor Feature Pipeline Embedding Logic
Goal: Modify the feature pipeline (Bytewax) to use the new EmbeddingClientInterface via dependency injection, removing direct calls to local embedding functions.

Task 12.1.1: Modify src/feature_pipeline/data_logic/embedding_data_handlers.py: Add EmbeddingClientInterface import: from src.core.embedding_clients import EmbeddingClientInterface.

AC: Import is added.

Task 12.1.2: Modify the **init** method of PostEmbeddingHandler, ArticleEmbeddingHandler, and RepositoryEmbeddingHandler to accept an argument embedding_client: EmbeddingClientInterface and store it as self.embedding_client.

AC: Handler **init** methods accept and store the embedding_client.

Task 12.2.1: In the embedd method of PostEmbeddingHandler:

Remove the call to the old embedd_text function.

Call embeddings = await self.embedding_client.embed([data_model.chunk_content]).

Get the first embedding: embedding_vector = embeddings[0] if embeddings else None. Handle the case where embeddings might be empty (though the client should raise an error before this).

Instantiate PostEmbeddedChunkModel, passing embedding_vector to the embedded_content field. Verify/Ensure PostEmbeddedChunkModel.embedded_content type matches the client output (List[float]) or add conversion (e.g., np.array(embedding_vector) if model requires numpy array).

AC: PostEmbeddingHandler.embedd uses the injected client, handles the result list, and correctly populates the PostEmbeddedChunkModel.

Task 12.2.2: In the embedd method of ArticleEmbeddingHandler:

Perform the same refactoring as in Task 12.2.1, but for ArticleChunkModel and ArticleEmbeddedChunkModel.

AC: ArticleEmbeddingHandler.embedd uses the injected client and correctly populates the ArticleEmbeddedChunkModel.

Task 12.2.3: In the embedd method of RepositoryEmbeddingHandler:

Perform the same refactoring as in Task 12.2.1, but for RepositoryChunkModel and RepositoryEmbeddedChunkModel.

AC: RepositoryEmbeddingHandler.embedd uses the injected client and correctly populates the RepositoryEmbeddedChunkModel.

Task 12.3.1: Modify src/feature_pipeline/data_logic/dispatchers.py: Update EmbeddingHandlerFactory.create_handler.

Change signature to create_handler(data_type: str, embedding_client: EmbeddingClientInterface) -> EmbeddingDataHandler:.

Pass the received embedding_client when instantiating the specific handlers (e.g., return PostEmbeddingHandler(embedding_client=embedding_client)).

AC: EmbeddingHandlerFactory accepts and passes the client to handlers.

Task 12.3.2: Modify src/feature_pipeline/data_logic/dispatchers.py: Update EmbeddingDispatcher.dispatch_embedder.

Change signature to dispatch_embedder(cls, data_model: DataModel, embedding_client: EmbeddingClientInterface) -> DataModel:.

Pass the embedding_client when calling cls.cleaning_factory.create_handler(data_type, embedding_client=embedding_client).

AC: EmbeddingDispatcher accepts and passes the client to the factory.

Task 12.4.1: Modify src/feature_pipeline/main.py:

Import the concrete client: from src.core.embedding_clients import OpenAIEmbeddingClient.

Before the flow = Dataflow(...) line, instantiate the client: embedding_client = OpenAIEmbeddingClient(). Wrap in try/except, log errors, and potentially exit if initialization fails.

Modify the op.map("embedded chunk dispatch", ...) step. Use a lambda function to pass both the data model and the client instance: lambda model: EmbeddingDispatcher.dispatch_embedder(model, embedding_client=embedding_client).

AC: Bytewax flow instantiates the client once and injects it into the dispatcher map step.

Task 12.5.1: Delete the file src/feature_pipeline/utils/embeddings.py.

AC: The obsolete local embedding utility file is removed.

Task 12.5.2: Check all files within src/feature_pipeline/ for any remaining imports or usage of the deleted utils.embeddings module or the old embedd_text function. Remove/update them.

AC: No residual usage of the old embedding code exists in the feature pipeline.

Task 12.6.1: Delete the file src/feature_pipeline/config.py.

AC: The duplicate/obsolete config file is removed.

Task 12.6.2: Search for any imports of feature_pipeline.config within the src/feature_pipeline directory (e.g., in utils/chunking.py, models/embedded_chunk.py). Replace them with imports from src.core.config.

AC: All necessary configuration in the feature pipeline is now sourced from src/core/config.py.

Story 13: Refactor RAG Retriever Embedding Logic
Goal: Modify the VectorRetriever to use the injected EmbeddingClientInterface for embedding user queries.

Task 13.1.1: Modify src/core/rag/retriever.py: Import the interface: from ..embedding_clients import EmbeddingClientInterface.

AC: Import is added.

Task 13.1.2: Modify VectorRetriever.**init**:

Remove the self.\_embedder = SentenceTransformer(...) line.

Add embedding_client: EmbeddingClientInterface as a required parameter to **init**.

Store the passed client: self.embedding_client = embedding_client.

AC: VectorRetriever constructor removes local embedder and accepts+stores an EmbeddingClientInterface.

Task 13.2.1: Modify VectorRetriever.\_search_single_query:

Replace query_vector = self.\_embedder.encode(generated_query).tolist() with the asynchronous call: embedding_result = await self.embedding_client.embed([generated_query]).

Extract the vector: query_vector = embedding_result[0] if embedding_result else None. Add error handling or assertion if embedding_result is empty/None.

Make the \_search_single_query method async because it now awaits the embedding client.

AC: \_search_single_query is now async and uses the injected client to get the query vector.

Task 13.2.2: Modify VectorRetriever.retrieve_top_k:

Since \_search_single_query is now async, the parallel execution needs adjustment. Replace concurrent.futures.ThreadPoolExecutor with asynchronous task management.

Create async tasks for each query: tasks = [asyncio.create_task(self._search_single_query(query, author_id, k)) for query in generated_queries].

Wait for tasks to complete: results = await asyncio.gather(\*tasks).

Update the flattening logic: hits = lib.flatten(results).

Ensure asyncio is imported.

AC: retrieve_top_k uses asyncio to run the async \_search_single_query tasks concurrently.

Task 13.3.1: Modify src/inference_pipeline/llm_twin.py:

Import the interface: from src.core.embedding_clients import EmbeddingClientInterface.

Add embedding_client: EmbeddingClientInterface as a required parameter to the generate method signature.

When instantiating VectorRetriever inside generate, pass the embedding_client: retriever = VectorRetriever(query=query, embedding_client=embedding_client).

AC: LLMTwin.generate accepts and passes the embedding_client to the VectorRetriever.

Task 13.4.1: Modify src/api/routers/inference.py:

Inside the generate_response endpoint function, retrieve the embedding client from app state: embedding_client = request_obj.app.state.embedding_client.

Add a check: if embedding_client is None, raise HTTPException(status_code=503, detail="Embedding service is not ready.").

Pass the retrieved embedding_client when calling llm_twin_instance.generate: result = await llm_twin_instance.generate(..., embedding_client=embedding_client).

AC: Inference API endpoint retrieves the embedding client from state and passes it to the LLMTwin.

Task 13.5.1: Modify the test script src/feature_pipeline/retriever.py (if still used/relevant):

Import OpenAIEmbeddingClient from src.core.embedding_clients.

Instantiate the client: embedding_client = OpenAIEmbeddingClient(). Handle potential errors.

Pass the embedding_client when creating VectorRetriever: retriever = VectorRetriever(query=query, embedding_client=embedding_client).

Since retrieve_top_k is now async, wrap the call in asyncio.run() or make the main execution block async. E.g., hits = asyncio.run(retriever.retrieve_top_k(...)). Ensure asyncio is imported.

AC: The retriever test script correctly instantiates and uses the OpenAIEmbeddingClient.

Story 14: Configure and Manage Embedding Client Lifespan
Goal: Ensure embedding clients are instantiated efficiently and configuration is centralized and up-to-date.

Task 14.1.1: Modify src/api/main.py's lifespan context manager:

Add app.state.embedding_client = None at the beginning.

After Qdrant and LLM client initialization, add logic to initialize the embedding client.

Import OpenAIEmbeddingClient (or the chosen implementation).

Add logger.info("Initializing Embedding client...").

Instantiate the client: embedding_client = OpenAIEmbeddingClient().

Wrap instantiation in a try...except block. Catch ValueError (e.g., missing API key) and general Exception. Log errors appropriately. Set app.state.embedding_client = None within the except block.

If successful, store the instance: app.state.embedding_client = embedding_client.

Log success or failure of embedding client initialization.

AC: Embedding client is initialized once during API startup and stored in app.state, with proper error handling and logging.

Task 14.2.1: Modify src/core/config.py (AppSettings class):

Add OPENAI_EMBEDDING_MODEL_ID: str = "text-embedding-3-small" (or another default).

Add OPENAI_EMBEDDING_DIMENSIONS: int = 1536 (or the correct dimension for the chosen model).

Ensure EMBEDDING_SIZE is set to the same value as OPENAI_EMBEDDING_DIMENSIONS. Update its default if necessary.

Remove the old EMBEDDING_MODEL_ID setting (e.g., "BAAI/bge-small-en-v1.5").

Remove EMBEDDING_MODEL_MAX_INPUT_LENGTH.

Remove EMBEDDING_MODEL_DEVICE.

AC: core/config.py contains necessary settings for the OpenAI embedding API and removes obsolete local model settings. EMBEDDING_SIZE matches the API model dimension.

Task 14.3.1: Review src/core/db/qdrant.py: Ensure create_vector_collection uses settings.EMBEDDING_SIZE for the vector parameters size. (It already does, just verify).

AC: Qdrant collection creation uses the correct embedding dimension from the updated settings.

Story 15: Cleanup, Testing, and Configuration Update
Goal: Verify the integrated system, perform cleanup, add/update tests, and ensure configuration is correct.

Task 15.1.1: Review .env.example:

Ensure OPENAI_API_KEY is present.

Add OPENAI_EMBEDDING_MODEL_ID (optional if default in config.py is sufficient).

Remove any environment variables related only to the old local embedding model (if any existed).

AC: .env.example reflects necessary configuration for OpenAI API key and potentially the embedding model ID. Obsolete variables are removed.

Task 15.1.2: Final review of src/core/config.py to ensure all settings are correctly defined, defaults are sensible, and no conflicts exist.

AC: core/config.py is clean and accurate.

Task 15.2.1: Review docker-compose.yml:

Ensure api and feature_pipeline services have the OPENAI_API_KEY passed as an environment variable (from .env file).

AC: Required services have access to the OpenAI API key via environment variables.

Task 15.2.2: Review Dockerfiles (.docker/Dockerfile.api, .docker/Dockerfile.feature_pipeline):

Ensure openai library is installed via poetry install.

Remove installation steps for sentence-transformers, torch, onnxruntime (or other local embedding dependencies) if they are no longer needed for other purposes. Verify if they are still needed (e.g., Reranker might use ST). If Reranker uses ST, keep it.

AC: Dockerfiles install required openai lib and remove unnecessary local embedding dependencies.

Task 15.3.1: Review Makefile: Check that commands like local-start, apply-migrations, call-inference-pipeline, local-test-_, evaluate-_ are still relevant and function correctly. Update any commands if paths or dependencies changed significantly.

AC: Makefile commands are functional with the refactored embedding logic.

Task 15.4.1: Write unit tests for src/core/embedding_clients/openai_client.py.

Mock the openai.AsyncOpenAI client and its embeddings.create method.

Test successful embedding generation (correct input, output format).

Test handling of empty input list.

Test handling of various OpenAI API errors (mocking exceptions).

Test **init** error handling (missing API key).

AC: Unit tests cover the OpenAIEmbeddingClient functionality and error handling.

Task 15.4.2: Update unit tests for src/feature_pipeline/data_logic/embedding_data_handlers.py.

Mock the EmbeddingClientInterface.

Instantiate handlers with the mocked client.

Verify that the handler's embedd method calls the mocked client's embed method with the correct text content (wrapped in a list).

Verify the handler correctly processes the mocked embedding result and populates the output model.

AC: Unit tests for embedding handlers confirm correct interaction with the injected client.

Task 15.4.3: Update unit tests for src/core/rag/retriever.py.

Mock the EmbeddingClientInterface and QdrantClient.

Instantiate VectorRetriever with the mocked embedding client.

Test retrieve_top_k (and implicitly \_search_single_query): verify it calls the mocked embedding client's embed method with the correct query and uses the result in the mocked Qdrant search call. Test the async execution flow.

AC: Unit tests for VectorRetriever verify correct usage of the injected embedding client.

Task 15.4.4: Update integration/unit tests for src/api/routers/inference.py (test_inference.py).

Ensure the TestClient setup provides a mocked embedding_client in app.state.

Update tests calling the /generate endpoint to mock the embedding_client.embed call if needed during RAG simulation.

Add a test case for when app.state.embedding_client is None (should return 503).

AC: Inference endpoint tests are updated for the injected embedding client and cover ready/not-ready states.

Task 15.5.1: Execute end-to-end test for feature pipeline:

Start services (make local-start).

Trigger a CDC event (e.g., insert data into a relevant Supabase table like articles or posts).

Monitor cdc-listener logs for notification pickup and push to RabbitMQ.

Monitor feature_pipeline logs for message consumption, processing (cleaning, chunking), and embedding calls (look for logs from OpenAIEmbeddingClient).

Verify that data points are upserted into the corresponding Qdrant vector collection (vector_posts, vector_articles, etc.). Check Qdrant UI or use a client script to confirm points exist and have the correct embedding dimension (settings.EMBEDDING_SIZE).

AC: Data flows from Supabase through CDC, RabbitMQ, Bytewax, gets embedded via OpenAI API, and lands in Qdrant with the correct dimensions.

Task 15.5.2: Execute end-to-end test for RAG inference:

Ensure data exists in Qdrant (from previous test or pre-populated).

Start API service (make local-start).

Call the inference endpoint (make call-inference-pipeline or curl) with use_rag=True and a query relevant to the data in Qdrant.

Monitor api logs: Check logs from VectorRetriever showing query embedding via OpenAIEmbeddingClient, Qdrant search, and LLM call via OpenAIClient.

Verify the final response is relevant to the query and likely used the retrieved context.

AC: The inference endpoint successfully uses the API-based embedding for query embedding and RAG retrieval.

Task 15.6.1: Review pyproject.toml and installed dependencies.

Identify sentence-transformers and its heavy dependencies (like torch).

If these are only used for the old embedding generation and not other features (e.g., reranking - check Reranker implementation), remove them from pyproject.toml.

Run poetry lock --no-update then poetry install --sync to update the lock file and remove the unused packages from the environment.

AC: Unnecessary local embedding dependencies are removed from the project.

Story 16: Documentation Updates
Goal: Update project documentation (README, etc.) to reflect the use of external API for embeddings.

Task 16.1.1: Update Architecture Overview section in README.md.

Modify descriptions/diagrams to show that embedding generation for both pipeline and query happens via an external API (e.g., OpenAI).

Remove references to local Sentence Transformer models for embedding.

AC: README accurately describes the embedding process using external APIs.

Task 16.1.2: Update any detailed architecture diagrams if they exist and show the embedding component location/type.

AC: Diagrams reflect the use of external embedding APIs.

Task 16.2.1: Update Setup/Installation instructions in README.md or INSTALL_AND_USAGE.md.

Clearly state the requirement for an OPENAI_API_KEY (or the key for the chosen provider) for embedding generation.

Remove any instructions related to downloading local embedding models.

Update environment variable lists (.env.example explanation) to include OPENAI_EMBEDDING_MODEL_ID if relevant.

AC: Setup instructions correctly mention API key requirements and remove local model steps.

Task 16.3.1: Update Configuration sections in documentation.

Explain the new embedding-related settings in src/core/config.py (OPENAI_EMBEDDING_MODEL_ID, OPENAI_EMBEDDING_DIMENSIONS).

Explain that EMBEDDING_SIZE must match the dimension of the chosen API model.

Remove documentation for obsolete local model settings.

AC: Configuration documentation accurately describes settings for API-based embeddings.

Task 16.4.1: Review Usage Examples. Ensure they still function and don't implicitly rely on local embeddings if specific behavior was expected. (Likely no changes needed here, but review).

AC: Usage examples remain valid.
