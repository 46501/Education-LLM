import logging
from litellm import acompletion, aembedding
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from litellm.exceptions import RateLimitError, APIConnectionError, Timeout

logger = logging.getLogger(__name__)

# Retry only on transient errors: RateLimit, Timeout, Connection errors.
def is_transient_error(exception):
    return isinstance(exception, (RateLimitError, APIConnectionError, Timeout))

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RateLimitError, APIConnectionError, Timeout)),
    reraise=True
)
async def safe_acompletion(*args, **kwargs):
    try:
        return await acompletion(*args, **kwargs)
    except Exception as e:
        if is_transient_error(e):
            logger.warning(f"Transient LLM error: {str(e)}. Retrying...")
            raise e
        logger.error(f"Non-transient LLM error: {str(e)}")
        from ..core.exceptions import LLMServiceError
        raise LLMServiceError()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RateLimitError, APIConnectionError, Timeout)),
    reraise=True
)
async def safe_aembedding(*args, **kwargs):
    try:
        return await aembedding(*args, **kwargs)
    except Exception as e:
        if is_transient_error(e):
            logger.warning(f"Transient LLM embedding error: {str(e)}. Retrying...")
            raise e
        logger.error(f"Non-transient LLM embedding error: {str(e)}")
        from ..core.exceptions import LLMServiceError
        raise LLMServiceError()
