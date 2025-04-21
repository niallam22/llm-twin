import concurrent.futures

from qdrant_client import models

import src.core.logger_utils as logger_utils
from src.core import lib
from src.core.db.qdrant import QdrantDatabaseConnector
from src.core.rag.query_expanison import QueryExpansion
from src.core.rag.reranking import Reranker
from src.core.rag.self_query import SelfQuery
from src.feature_pipeline.utils.embeddings import embedd_text

logger = logger_utils.get_logger(__name__)


class VectorRetriever:
    """
    Class for retrieving vectors from a Vector store in a RAG system using query expansion and Multitenancy search.
    """

    def __init__(self, query: str) -> None:
        self._client = QdrantDatabaseConnector()
        self.query = query
        self._embedder = embedd_text
        self._query_expander = QueryExpansion()
        self._metadata_extractor = SelfQuery()
        self._reranker = Reranker()

    def _search_single_query(self, generated_query: str, author_id: str, k: int, collection_id: str):
        assert k > 3, "k should be greater than 3"
        logger.info(f"generated query     {generated_query}")
        query_vector = self._embedder(generated_query).tolist()

        vectors = [
            # self._client.search(
            #     collection_name="vector_posts",
            #     query_filter=models.Filter(
            #         must=[
            #             models.FieldCondition(
            #                 key="author_id",
            #                 match=models.MatchValue(
            #                     value=author_id,
            #                 ),
            #             )
            #         ]
            #         if author_id
            #         else None
            #     ),
            #     query_vector=query_vector,
            #     limit=k // 3,
            # ),
            self._client.search(
                collection_name="vector_articles",
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="collection_id",
                            match=models.MatchValue(
                                value=collection_id,
                            ),
                        )
                    ]
                ),
                query_vector=query_vector,
                limit=k // 3,
            ),
            # self._client.search(
            #     collection_name="vector_repositories",
            #     query_filter=models.Filter(
            #         must=[
            #             models.FieldCondition(
            #                 key="owner_id",
            #                 match=models.MatchValue(
            #                     value=author_id,
            #                 ),
            #             )
            #         ]
            #         if author_id
            #         else None
            #     ),
            #     query_vector=query_vector,
            #     limit=k // 3,
            # ),
        ]

        return lib.flatten(vectors)

    # @opik.track(name="retriever.retrieve_top_k")
    async def retrieve_top_k(self, k: int, to_expand_to_n_queries: int, collection_id: str) -> list:
        generated_queries = self._query_expander.generate_response(self.query, to_expand_to_n=to_expand_to_n_queries)
        logger.info(
            "Successfully generated queries for search.",
            num_queries=len(generated_queries),
        )
        author_id = None

        # Not using selfquery
        # author_id = await self._metadata_extractor.generate_response(self.query)
        # if author_id:
        #     logger.info(
        #         "Successfully extracted the author_id from the query.",
        #         author_id=author_id,
        #     )
        # else:

        #     logger.warning("Did not found any author data in the user's prompt.")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            search_tasks = [
                executor.submit(self._search_single_query, query, author_id or "", k, collection_id=collection_id)
                for query in generated_queries
            ]

            hits = [task.result() for task in concurrent.futures.as_completed(search_tasks)]
            hits = lib.flatten(hits)

        logger.info("All documents retrieved successfully.", num_documents=len(hits))

        return hits

    # @opik.track(name="retriever.rerank")
    def rerank(self, hits: list, keep_top_k: int) -> list[str]:
        content_list = [hit.payload["content"] for hit in hits]
        rerank_hits = self._reranker.generate_response(query=self.query, passages=content_list, keep_top_k=keep_top_k)

        logger.info("Documents reranked successfully.", num_documents=len(rerank_hits))

        return rerank_hits

    def set_query(self, query: str):
        self.query = query
