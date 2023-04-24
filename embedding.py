from openai.embeddings_utils import (
    get_embedding,
)
import dotenv
import os
import openai
import pandas as pd
import numpy as np
import pinecone
dotenv.load_dotenv()
NCBI_API_KEY = os.getenv("NCBI_API_KEY")
from metapub import PubMedFetcher

openai.api_key = os.getenv("OPENAI_API_KEY")

embedding_model = "text-embedding-ada-002"
embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191
top_n = 1000

input_datapath = "data/pm_eutils.csv"
output_embeddings_path = "data/pm_embeddings_with_id.csv"


pinecone.init(os.getenv("PINECONE_API_KEY"), environment="us-east-1-aws")

fetch = PubMedFetcher()


def makeContext(ids):
    context = ""
    for id in ids:
        content = str(fetch.article_by_pmid(id).abstract)
        context += f"PM ID: {id}: " + content + "\n"
    return context

def pineconeFilter(query, topK=3, index="pm-embeddings-001"):
    queryEmbedding = get_embedding(
        query,
        engine="text-embedding-ada-002"
    )
    # print(queryEmbedding)
    index = pinecone.Index(index)
    pineconeQuery = index.query(
        namespace="PM_ID",
        vector=queryEmbedding,
        top_k=topK,
        include_values=False
    )
    # print(pineconeQuery['matches'])
    ids = []
    for i in pineconeQuery['matches']:
        try:
            ids.append(i['id'])
            print('id')
        except:
            ids.append(i['pm_id'])
            print('pm_id')
        # ids.append(i['id'])
    return makeContext(ids), ids
   