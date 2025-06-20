import opik
from langchain_openai import ChatOpenAI
from opik.integrations.langchain import OpikTracer

import src.core.logger_utils as logger_utils
from src.core import lib
from src.core.config import settings
from src.core.db.documents import UserDocument
from src.core.rag.prompt_templates import SelfQueryTemplate

logger = logger_utils.get_logger(__name__)


class SelfQuery:
    opik_tracer = OpikTracer(tags=["SelfQuery"])

    @staticmethod
    @opik.track(name="SelQuery.generate_response")
    async def generate_response(query: str) -> str | None:
        prompt = SelfQueryTemplate().create_template()
        model = ChatOpenAI(
            model=settings.OPENAI_MODEL_ID,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )
        chain = prompt | model
        chain = chain.with_config({"callbacks": [SelfQuery.opik_tracer]})

        response = chain.invoke({"question": query})
        response = response.content

        user_full_name = response.strip("\n ")

        if user_full_name == "none":
            return None

        logger.info(
            "Successfully extracted the user full name from the query.",
            user_full_name=user_full_name,
        )
        first_name, last_name = lib.split_user_full_name(user_full_name)

        logger.info(
            "Successfully extracted the user first and last name from the query.",
            first_name=first_name,
            last_name=last_name,
        )
        user_id = await UserDocument.get_or_create(username=user_full_name)

        return user_id
