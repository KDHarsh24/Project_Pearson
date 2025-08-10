import os
from dotenv import load_dotenv
from langchain_ibm import ChatWatsonx

def get_env_variable(name: str, default=None, cast_type=None):
    value = os.getenv(name, default)
    if cast_type and value is not None:
        try:
            return cast_type(value)
        except ValueError:
            return default
    return value

def get_chatwatsonx():
    load_dotenv()
    api_key = get_env_variable("WATSONX_API_KEY")
    url = get_env_variable("WATSONX_URL")
    project_id = get_env_variable("WATSONX_PROJECT_ID")
    model_id = get_env_variable("MODEL_ID", "ibm/granite-13b-chat-v2")
    params = {
        "temperature": get_env_variable("TEMPERATURE", 0.5, float),
        "max_new_tokens": get_env_variable("MAX_NEW_TOKENS", 150, int),
        "top_p": get_env_variable("TOP_P", 0.9, float),
    }
    try:
        chat = ChatWatsonx(
            model_id=model_id,
            url=url,
            apikey=api_key,
            project_id=project_id,
            params=params,
        )
        return chat
    except Exception as e:
        raise RuntimeError("Failed to initialize ChatWatsonx. Check API key, URL region, and Project ID.") from e
