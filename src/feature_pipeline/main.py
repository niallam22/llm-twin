import bytewax.operators as op
from bytewax.dataflow import Dataflow
from data_flow.stream_input import RabbitMQSource
from data_flow.stream_output import QdrantOutput
from data_logic.dispatchers import (
    ChunkingDispatcher,
    CleaningDispatcher,
    EmbeddingDispatcher,
    RawDispatcher,
)

from src.core.db.qdrant import QdrantDatabaseConnector

# bytewax creates a continuous data pipeline stream between rabbit mq and app functionality
# input creates a source node to read data from queue
# map creates a one to one map for each message in the queue
# flatmap transforms one messes to many
# sends data to final destination

connection = QdrantDatabaseConnector()

flow = Dataflow("Streaming ingestion pipeline")
stream = op.input("input", flow, RabbitMQSource())
stream = op.map("raw dispatch", stream, RawDispatcher.handle_mq_message)  # convert raw message to data model
stream = op.map("clean dispatch", stream, CleaningDispatcher.dispatch_cleaner)  # clean data
op.output(
    "cleaned data insert to qdrant",
    stream,
    QdrantOutput(connection=connection, sink_type="clean"),  # insert clean data to qdrant
)
stream = op.flat_map("chunk dispatch", stream, ChunkingDispatcher.dispatch_chunker)  # create chunks from clean data
stream = op.map("embedded chunk dispatch", stream, EmbeddingDispatcher.dispatch_embedder)
op.output(
    "embedded data insert to qdrant",
    stream,
    QdrantOutput(connection=connection, sink_type="vector"),
)  # store embeddings in vector db
