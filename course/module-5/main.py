from inference import ModelInference
from dotenv import load_dotenv
if __name__ == '__main__':
    load_dotenv()
    tool = ModelInference()
    query = """
            Hello my author_id is 1.

            Could you please draft a LinkedIn post discussing RAG systems?
            I'm particularly interested in how RAG works and how it is integrated with vector DBs and large language models (LLMs).
            """
    content = tool.generate_content(query=query)
    print(content)
