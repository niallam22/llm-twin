import logging
from typing import Any, Dict, List

import openai

# Import specific message types from the openai library
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from ..config import settings
from .base import LLMClientInterface

logger = logging.getLogger(__name__)


class OpenAIClient(LLMClientInterface):
    def __init__(self):
        logger.info("Initializing OpenAIClient...")
        if not settings.OPENAI_API_KEY:
            logger.error("OpenAI API key (OPENAI_API_KEY) is not configured.")
            raise ValueError("OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable.")
        try:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAIClient initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
            raise

    async def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Generates a text response using the OpenAI API based on the provided message history.

        Args:
            messages: A list of message dictionaries, where each dictionary
                      has 'role' (e.g., 'user', 'assistant', 'system') and 'content' keys.
            **kwargs: Additional keyword arguments to pass to the OpenAI API,
                      e.g., temperature, max_tokens.

        Returns:
            The generated text response from the LLM.

        Raises:
            Exception: If the API call fails or returns an unexpected response.
            ValueError: If an invalid role is provided in the messages.
        """
        try:
            logger.debug(f"Calling OpenAI API with model: {settings.OPENAI_MODEL_ID}")

            # Map the input dictionaries to the required OpenAI message types
            typed_messages: List[ChatCompletionMessageParam] = []
            for msg in messages:
                role = msg.get("role")
                content = msg.get("content")
                if not role or not content:
                    logger.warning(f"Skipping message with missing role or content: {msg}")
                    continue

                if role == "user":
                    typed_messages.append(ChatCompletionUserMessageParam(role="user", content=content))
                elif role == "assistant":
                    typed_messages.append(ChatCompletionAssistantMessageParam(role="assistant", content=content))
                elif role == "system":
                    typed_messages.append(ChatCompletionSystemMessageParam(role="system", content=content))
                # Add other roles like 'tool' if needed later
                else:
                    logger.error(f"Invalid role '{role}' encountered in messages.")
                    raise ValueError(f"Invalid role '{role}' in messages.")

            if not typed_messages:
                logger.error("No valid messages to send to OpenAI API after filtering.")
                raise ValueError("No valid messages provided.")

            # Prepare generation parameters, merging defaults with kwargs
            generation_params = {
                "temperature": 0.7,
                "max_tokens": 512,
                **kwargs,  # Allow overriding defaults
            }

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL_ID,
                messages=typed_messages,  # Pass the correctly typed list
                **generation_params,
            )

            if response.choices and response.choices[0].message.content:
                generated_text = response.choices[0].message.content.strip()
                logger.debug("Received response from OpenAI API.")
                return generated_text
            else:
                logger.error(f"OpenAI API returned an unexpected response structure: {response}")
                raise Exception("OpenAI API returned an empty or malformed response.")

        except openai.AuthenticationError as e:
            logger.error(f"OpenAI Authentication Error: {e}", exc_info=True)
            raise Exception(f"OpenAI Authentication Error: {e}") from e
        except openai.RateLimitError as e:
            logger.error(f"OpenAI Rate Limit Error: {e}", exc_info=True)
            raise Exception(f"OpenAI Rate Limit Error: {e}") from e
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI API Connection Error: {e}", exc_info=True)
            raise Exception(f"OpenAI API Connection Error: {e}") from e
        except openai.APIError as e:
            logger.error(f"OpenAI API Error: {e}", exc_info=True)
            raise Exception(f"OpenAI API Error: {e}") from e
        except ValueError:  # Catch the ValueError raised for invalid roles
            raise  # Re-raise it to be handled by the caller
        except Exception as e:
            logger.error(f"An unexpected error occurred during OpenAI API call: {e}", exc_info=True)
            raise Exception(f"An unexpected error occurred: {e}") from e
