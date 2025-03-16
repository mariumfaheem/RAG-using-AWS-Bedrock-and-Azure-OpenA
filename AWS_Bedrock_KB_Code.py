import os
import boto3


boto3_session = boto3.Session()
bedrock_agent_runtime_client = boto3_session.client(service_name='bedrock-agent-runtime')

kb_id = os.environ.get('KNOWLEGDE_BASE_ID')


def retrive(input_text,KB_ID):
    response = bedrock_agent_runtime_client.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={
            'text': input_text
        },
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 5
            }
        }
    )
    return response

def lambda_handler(event, context):
    if 'question' not in event:
        return {
            'statusCode': 400,
            'body': 'Missing question parameter'
        }
    input_text = event['question']
    response = retrive(input_text, kb_id)
    return {
        'statusCode': 200,
        'body': response
    }