from ibm_watsonx_ai.metanames import GenTextParamsMetaNames
from ibm_watsonx_ai.foundation_models import ModelInference
from langchain_ibm import WatsonxLLM
import os

# Initialize the model
model = WatsonxLLM(
    model="ibm/granite-13b-chat-v2",  # example model ID
    api_key=os.environ["WATSONX_API_KEY"],
    api_base_url=os.environ["WATSONX_URL"],
    project_id=os.environ["WATSONX_PROJECT_ID"],
    generation_kwargs={
        "temperature": 0.5,
        "max_new_tokens": 150,
        "top_p": 0.9
    }
)

# Example query
response = model.generate("Hello, how can I help with today's orders?")
print(response.content)
