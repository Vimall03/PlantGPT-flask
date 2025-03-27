# Description: This script is used to call the LLM model to get the summary of the environmental data.
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from pydantic import RootModel 
import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def llm_call(query):
  try:
    class DummyModel(RootModel):
      root: dict

    model = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name=MODEL_NAME)
    parser_json = JsonOutputParser(pydantic_object=DummyModel)
    prompt = PromptTemplate(
      template="Answer the user query.\n{format_instructions}\n{query}\n",
      input_variables=["query"],
      partial_variables={"format_instructions": parser_json.get_format_instructions()},
    )
    chain = prompt | model | parser_json
    response = chain.invoke({"query": query})
    return response
  except Exception as e:
    raise RuntimeError(f"Failed to call LLM: {e}") from e

def get_summary(humidity, temperature, voc_levels, ppm_levels, time_frame):
  query = f"""As an environmental data analyst expert in plant health, assess sensor data averaged over {time_frame} from a forest:

Humidity (%): {humidity}
Temperature (°C): {temperature}
VOC (ppm): {voc_levels}
PPM (ppm): {ppm_levels}

Tasks:
1. Evaluate plant health (thriving, stable, stressed, declining).
2. Check risks:
   - Mold: VOC > 100, humidity > 80%, 25°C-35°C
   - Drying: Humidity < 30%, temperature > 30°C
   - Poor Air: VOC > 150, PPM > 200
   - Cold Stress: Temperature < 10°C, humidity > 70%
   - Root Rot: Humidity > 90% (prolonged)
3. Return JSON:
   No risks: {{"overall_health": "<50-60 word assessment as a report>", "risks": "False"}} //Clearly mention that are no potential risks are found in the overall_health.
   Risks: {{"overall_health": "<50-60 word assessment as a report>", "risks": "True", "recommendations": "<45-50 word recommendation practical for a forest manager>"}} //Clearly mention that are risks are found in the overall_health.

Recommendation Example: Increase ground cover to retain moisture. Monitor water-stressed zones, Consider implementing measures to reduce temperature and VOC levels, Monitor the situation closely
   """
  
  response = llm_call(query)
  return response
