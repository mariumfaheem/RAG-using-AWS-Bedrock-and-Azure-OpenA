from fastapi import FastAPI, HTTPException, status, Query
from fastapi.responses import JSONResponse, RedirectResponse

import boto3
import json
import os

from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

lambda_client = boto3.client(
    'lambda',
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")

)

print(os.getenv('AWS_ACCESS_KEY_ID'))

def get_context(question):
    try:
        # Invoke the Lambda function

        response = lambda_client.invoke(
            FunctionName='rag-using-aws-bedrock-and-azure-openai_lambda',
            InvocationType='RequestResponse',
            Payload=json.dumps({"question": question})
        )



        # Read the Lambda function's response stream and parse it
        response_payload = response['Payload'].read()
        print(response_payload)
        response_payload_dict = json.loads(response_payload)

        # Navigate to the retrievalResults
        results = response_payload_dict['body']['answer']['retrievalResults']

        print(results)

        # Initialize an empty string to store the extracted paragraph
        extracted_paragraph = ""

        # Loop through each result and concatenate text to a paragraph
        for result in results:
            text = result['content']['text']
            extracted_paragraph += text + " "

        # Return the concatenated paragraph
        return {"response": extracted_paragraph.strip()}

    except Exception as e:
        return {"error": str(e)}


def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def get_answer_from_kb(query):

    llm = AzureChatOpenAI(
        openai_api_version="2024-02-15-preview",
        openai_api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
        azure_deployment="gpt-4o",
        max_tokens=10000,
        temperature=0.4
    )

    kb_prompt_template = """
    You are a helpful AI assistant who is expert in answering questions. Your task is to answer user's questions as factually as possible. You will be given enough context with information to answer the user's questions. Find the context:
    Context: {context}
    Question: {query}

    Now generate a detailed answer that will be helpful for the user. Return the helpful answer.

    Answer: 
    """
    kb_prompt_template = """
    You are a helpful AI assistant who is expert in answering questions. Your task is to answer user's questions as factually as possible. You will be given enough context with information to answer the user's questions. Find the context:
    Context: {context}
    Question: {query}

    Now generate a detailed answer that will be helpful for the user. Return the helpful answer.

    Answer: 
    """

    prompt_template_kb = PromptTemplate(
        input_variables=["context", "query"], template=kb_prompt_template
    )

    llm_chain = LLMChain(llm=llm, prompt=prompt_template_kb)

    context = get_context(query)
    result = llm_chain.run({"context": context, "query": query})

    return result

@app.post("/chat_with_knowledge_base")
def chat_with_knowledge_base(query):
    response =  get_answer_from_kb(query)
    return JSONResponse(content = response,status_code = 200)


# if __name__ == "__main__":
#     test_question = {"question": "What is FastAPI?"}
#     print(get_context(test_question))