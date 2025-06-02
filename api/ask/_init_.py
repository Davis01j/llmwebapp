import logging
import azure.functions as func
from azure.cosmos import CosmosClient
import openai
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    question = req.get_json().get("question")
    if not question:
        return func.HttpResponse("No question provided", status_code=400)

    # Cosmos DB
    cosmos = CosmosClient(os.environ["COSMOS_URL"], os.environ["COSMOS_KEY"])
    container = cosmos.get_database_client("pdfdata").get_container_client("extractedtext")
    docs = list(container.read_all_items())
    all_text = "\n\n".join([doc["text"] for doc in docs])

    # OpenAI
    openai.api_key = os.environ["AZURE_OPENAI_KEY"]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant answering based on PDF documents."},
            {"role": "user", "content": f"PDF content: {all_text[:12000]}\n\nQuestion: {question}"}
        ]
    )

    return func.HttpResponse(
        json.dumps({ "answer": response.choices[0].message.content }),
        mimetype="application/json"
    )

