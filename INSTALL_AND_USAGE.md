<table style="border-collapse: collapse; border: none;">
  <tr style="border: none;">
    <td width="20%" style="border: none;">
      <a href="https://decodingml.substack.com/" aria-label="Decoding ML">
        <img src="https://github.com/user-attachments/assets/f2f2f9c0-54b7-4ae3-bf8d-23a359c86982" alt="Decoding ML Logo" width="150"/>
      </a>
    </td>
    <td width="80%" style="border: none;">
      <div>
        <h2>📬 Stay Updated</h2>
        <p><b><a href="https://decodingml.substack.com/">Join Decoding ML</a></b> for proven content on production-grade AI, GenAI, and information retrieval systems. Every week, straight to your inbox.</p>
      </div>
    </td>
  </tr>
</table>

<p align="center">
  <a href="https://decodingml.substack.com/">
    <img src="https://img.shields.io/static/v1?label&logo=substack&message=Subscribe Now&style=for-the-badge&color=black&scale=2" alt="Subscribe Now" height="40">
  </a>
</p>

---

# Install

## Local dependencies

Before starting to install the LLM Twin project, make sure you have installed the following dependencies on your local system:

| Tool     | Version | Purpose             | Installation Link                                                                              |
| -------- | ------- | ------------------- | ---------------------------------------------------------------------------------------------- |
| Python   | 3.11    | Runtime environment | [Download](https://www.python.org/downloads/)                                                  |
| Poetry   | ≥1.8.4  | Package management  | [Install Guide](https://python-poetry.org/docs/)                                               |
| GNU Make | ≥3.81   | Build automation    | [Install Guide](https://www.gnu.org/software/make/)                                            |
| Docker   | ≥27.0.3 | Containerization    | [Install Guide](https://www.docker.com/)                                                       |
| AWS CLI  | ≥2.18.5 | Cloud management    | [Install Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) |

## Cloud services

The code also uses and depends on the following cloud services. For now, you don't have to do anything. We will guide you in the installation and deployment sections on how to use them:

| Service                                            | Purpose                            | Cost                | Mandatory Credentials                                                            |
| -------------------------------------------------- | ---------------------------------- | ------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| [HuggingFace](https://huggingface.com/)            | Model registry                     | Free                | `HUGGINGFACE_ACCESS_TOKEN`                                                       |
| [Comet ML](https://www.comet.com/site/)            | Experiment tracker                 | Free tier available | `COMET_API_KEY` <br> `COMET_WORKSPACE`                                           |
| [Opik](https://www.comet.com/site/products/opik/)  | Prompt monitoring & LLM Evaluation | Free tier available | `COMET_API_KEY` <br> `COMET_WORKSPACE`                                           |
| [OpenAI API](https://openai.com/index/openai-api/) | LLM API for recommender system     | Pay-per-use         | `OPENAI_API_KEY`                                                                 | [Quick Start Guide](https://platform.openai.com/docs/quickstart) |
| [Supabase](https://supabase.com/)                  | Postgres DB & Backend              | Free tier available | `SUPABASE_DB_URL`                                                                |
| [Qdrant](https://qdrant.tech/)                     | Vector database                    | Free tier available | -                                                                                |
| [AWS](https://aws.amazon.com/)                     | Optional Cloud Services (e.g., S3) | Pay-per-use         | `AWS_REGION` <br> `AWS_ACCESS_KEY` <br> `AWS_SECRET_KEY` (if using AWS services) |

## Supported commands

We will use `GNU Make` to install and run our application.

To see all our supported commands, run the following:

```shell
make help
```

## Configure

All the sensitive credentials are placed in a `.env` file that will always sit at the root of your directory, at the same level with the `.env.example` file.

Go to the root of the repository and copy our `.env.example` file as follows:

```shell
cp .env.example .env
```

Now fill it with your credentials, following the suggestions from the next section.

### Getting credentials for cloud services

Now, let's understand how to fill in all the essential variables within the `.env` file to get you started. The following are the mandatory settings we must complete when working locally:

#### OpenAI

To authenticate to OpenAI's API, you must fill out the `OPENAI_API_KEY` env var with an authentication token.

```env
OPENAI_API_KEY=your_api_key_here
```

→ Check out this [tutorial](https://platform.openai.com/docs/quickstart) to learn how to provide one from OpenAI.

#### Hugging Face

To authenticate to Hugging Face, you must fill out the `HUGGINGFACE_ACCESS_TOKEN` env var with an authentication token.

```env
HUGGINGFACE_ACCESS_TOKEN=your_token_here
```

→ Check out this [tutorial](https://huggingface.co/docs/hub/en/security-tokens) to learn how to provide one from Hugging Face.

#### Comet ML & Opik

To authenticate to Comet ML and Opik (used for evaluation and monitoring), you must fill out the `COMET_API_KEY` and `COMET_WORKSPACE` env vars with your authentication token and workspace name.

```env
COMET_API_KEY=your_api_key_here
COMET_WORKSPACE=your_workspace_name_here
```

→ Check out this [tutorial](https://www.comet.com/docs/v2/api-and-sdk/rest-api/overview/) to learn how to get the Comet ML variables from above. You can also access Opik's dashboard using 🔗[this link](https://www.comet.com/opik).

#### Supabase

You need the connection URL for your Supabase project (either cloud or local Docker).

```env
SUPABASE_DB_URL=postgresql://user:password@host:port/dbname
```

→ Find this in your Supabase project settings or configure it if running locally via Docker.

#### AWS (Optional)

Required only if you intend to use specific AWS services (e.g., S3 for storage). Fill in `AWS_REGION`, `AWS_ACCESS_KEY`, `AWS_SECRET_KEY` if needed.

#### Qdrant

Optional, only if you want to use Qdrant cloud. Otherwise, you can complete the course using the local version of Qdrant.

## Install local dependencies

You can create a Python virtual environment and install all the necessary dependencies using Poetry, by running:

```shell
make install
```

> [!IMPORTANT]
> You need Python 3.11 installed! You can either install it globally or install [pyenv](https://github.com/pyenv/pyenv) to manage multiple Python dependencies. The `.python-version` file will signal to `pyenv` what Python version it needs to use in this particular project.

After installing the dependencies into the Poetry virtual environment, you can activate your virtual environment into your current CLI by running:

```bash
poetry shell
```

## Set up the data infrastructure

We support running the entire data infrastructure (API, CDC listener, feature pipeline, Postgres, RabbitMQ, and Qdrant) through Docker. Thus, with a few commands you can quickly populate the database and vector DB with relevant data to test out the RAG and inference parts of the course.

### Spin up the infrastructure

You can start all the required Docker containers, by running:

```shell
make local-start
```

It will take a while to run until all the Docker images are pulled or built.

Behind the scenes it will build and run all the Docker images defined in the [docker-compose.yml](https://github.com/decodingml/llm-twin-course/blob/main/docker-compose.yml) file.

> [!NOTE]
>
> > If running Postgres locally via Docker (as defined in `docker-compose.yml`), ensure the `SUPABASE_DB_URL` in your `.env` file points to the Docker service (e.g., `postgresql://postgres:postgres@localhost:54322/postgres` if using default ports and credentials). If using Supabase Cloud, use the connection string provided by Supabase.

> [!WARNING]
> For `arm` users (e.g., `M macOS devices`), go to your Docker desktop application and enable `Use Rosetta for x86_64/amd64 emulation on Apple Silicon` from the Settings. There is a checkbox you have to check.
> Otherwise, your Docker containers will crash.

### Tear down the infrastructure

Run the following `Make` command to tear down all your docker containers:

```shell
make local-stop
```

# Usage: Run an end-to-end flow

Now that we have configured our credentials, local environment and Docker infrastructure let's look at how to run an end-to-end flow of the LLM Twin course.

> [!IMPORTANT]
> Note that we won't go into the details of the system here. To fully understand it, check out our free lessons, which explains everything step-by-step: [LLM Twin articles series](https://medium.com/decodingml/llm-twin-course/home).

### Step 1: Crawling data

Trigger the API endpoint to crawl data and add it to the Supabase database:

```shell
make local-test-medium
# or make local-test-github
# or make local-test-raw-text
```

You should get a response with a `200` status code, as follows:

```
{"status":"submitted","document_id":"..."} # Example response, actual may vary
```

After running the command, this will happen:

1. The API endpoint receives the request.
2. It calls the appropriate crawler (for links) or saves the raw text directly.
3. Data is saved to the Supabase Postgres database (e.g., `articles` table).
4. The Postgres `INSERT` triggers a notification via `pg_notify`.
5. The `cdc-listener` service receives the notification and publishes the data to RabbitMQ.
6. The `feature-pipeline` (Bytewax) consumes the message, processes it (cleans, chunks, embeds), and saves embeddings to the Qdrant vector DB.

You can check the logs from the API service Docker container by running:

```bash
docker logs llm-twin-api # Check API logs for crawl request handling
```

You should see something similar to:

```text
{"level":"info","message":"POST /crawl/link HTTP/1.1\" 200 OK","timestamp":"..."} # Example API log
```

### Step 2: Feature engineering & Vector DB

The previous step actually called both the crawling and RAG feature engineering pipeline. But now, let's check that everything worked as expected.

Thus, let's check that the feature pipeline works and the vector DB is successfully populated.

To do so, check the logs of the `llm-twin-feature-pipeline` Docker container by running:

```shell
docker logs llm-twin-feature-pipeline
```

You should see something similar to:

```text
2024-12-25 16:53:45 [info     ] Cleaned content chunked successfully. cls=data_logic.dispatchers data_type=repositories num=955
2024-12-25 16:53:45 [info     ] Chunk embedded successfully.   cls=data_logic.dispatchers data_type=repositories embedding_len=384
2024-12-25 16:53:45 [info     ] Chunk embedded successfully.   cls=data_logic.dispatchers data_type=repositories embedding_len=384
```

Also, you can check the logs of the CDC listener, RabbitMQ, and feature pipeline containers:

```bash
docker logs llm-twin-cdc-listener # CDC listener service
docker logs llm-twin-mq           # RabbitMQ
```

You should see logs reflecting the cleaning, chunking, and embedding operations (without any errors, of course).

To check that the Qdrant `vector DB` is populated successfully, go to its dashboard by typing in your browser: **[localhost:6333/dashboard](localhost:6333/dashboard)**. There, you should see the repositories or article collections created and populated, similar to the image below:

![Qdrant Example](media/qdrant-example.png)

> [!NOTE]
> If using the cloud version of Qdrant, go to your Qdrant account and cluster to see the same thing as in the local dashboard.

### Step 3: Populating Supabase and Qdrant with more data

To populate the Supabase database and Qdrant VectorDB with ~50 links from `data/links.txt`, run the following command (ensure services are running):

```bash
make local-ingest-data
```

This command iterates through the links file and calls the `/crawl/link` API endpoint for each.

### Step 4: Testing the RAG retrieval step

Now that our Qdrant vector DB is populated with our data let's test out the RAG retrieval module to see that everything works fine by retrieving some items using a dummy query:

```shell
make local-test-retriever
```

> [!IMPORTANT]
> Before running this command, check [Qdrant's dashboard](localhost:6333/dashboard) to ensure your vector DB is populated with data. Otherwise, the retriever will not have any data to work with.

### Step 5: Running the evaluation pipelines (Optional)

After populating the vector database, you can run evaluation scripts to test the LLM and RAG performance using predefined prompts or data logged by Opik.

To evaluate the LLM directly (using the configured OpenAI model):

```shell
make evaluate-llm
```

To evaluate the RAG system (retrieval + generation):

```shell
make evaluate-rag
```

To evaluate based on production monitoring data logged by Opik:

```shell
make evaluate-llm-monitoring
```

Check the evaluation results logged to the console and potentially in [Opik's Dashboard](https://www.comet.com/opik).

### Step 6: Testing the inference pipeline

The inference pipeline runs as part of the FastAPI `api` service. Ensure all services are running (`make local-start`).

You can call the inference endpoint directly using `curl` or the provided Makefile command:

```shell
make call-inference-pipeline
```

This sends a sample query ("What is RAG?") to the `/generate` endpoint.

After testing the inference pipeline from the CLI, you can start playing around with the LLM Twin from our GUI, by running:

```shell
make local-start-ui
```

Now you can access the GUI at **[http://localhost:7860](http://localhost:7860)** and start asking the LLM Twin to generate some content for you, such as: **"Draft a post about RAG systems."** as in the example below:

![UI Example](media/ui-example.png)

Interacting with the UI or calling the API endpoint will generate logs that can be monitored using Opik. Check [Opik's Dashboard](https://www.comet.com/opik) to see logged prompts and responses.

> [!NOTE]
>
> > There are no separate deployment steps for the inference pipeline in this refactored version, as it's integrated into the main `api` service managed by Docker Compose. Stopping the services (`make local-stop`) will stop the inference endpoint.
