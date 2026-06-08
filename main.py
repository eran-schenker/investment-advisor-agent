
######## test APIs ########

# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()

# client = OpenAI()

# response = client.chat.completions.create(
#     model="gpt-4.1-mini",
#     messages=[
#         {"role": "user", "content": "Say hello like a financial analyst."}
#     ]
# )

# print(response.choices[0].message.content)

# import os
# from dotenv import load_dotenv  # Remove 'load_model'
# from tavily import TavilyClient

# # Load environment variables from the .env file
# load_dotenv()

# # Initialize the client
# client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# results = client.search("Apple stock news")

# print(results)

######## test APIs end ########

###### main before pipeline May 21st ######## 

## the following logic moved into Pipeline
# from services.market_data import get_market_data_and_detect_anomalies

# if __name__ == "__main__":
#     results, flagged = get_market_data_and_detect_anomalies()
#     print(flagged)

###### main before pipeline May 21st END ######## 

from services.pipeline import run_pipeline

if __name__ == "__main__":
    _, flagged = run_pipeline()
    print(flagged)