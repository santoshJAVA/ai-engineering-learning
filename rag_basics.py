import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

def run_vector_search():
    print("Initializing local ChromaDB in memory...\n")
    
    # 2. Setup the Chroma client
    client = chromadb.Client()
    
    # 3. Setup the OpenAI Embedding Function 
    # This automatically turns our text into vectors behind the scenes
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ.get("OPENAI_API_KEY"),
        model_name="text-embedding-3-small"
    )
    
    # 4. Create a "collection" (similar to a SQL Table)
    collection = client.create_collection(
        name="freelance_pricing", 
        embedding_function=openai_ef
    )
    
    # 5. Insert your private data into the Vector DB
    print("Embedding and storing private data into Vector DB...\n")
    collection.add(
        documents=[
            "Base Shopify E-commerce setup with 5 pages and payment gateway integration costs $4,500. Takes 3 weeks.",
            "Custom React frontend with a Node.js backend costs $12,000. Takes 8 weeks. Maintenance is $500/month.",
            "Simple WordPress landing page for marketing campaigns costs $1,200. Takes 1 week.",
            "SEO Audit and technical optimization costs $800 as a one-time fee."
        ],
        ids=["id_ecommerce", "id_custom_app", "id_landing_page", "id_seo"]
    )
    
    # 6. Simulate a messy user query (e.g., from a transcribed voice memo)
    # Notice how this query doesn't use the exact words "Shopify", "E-commerce", or "Custom React"
    messy_query = "The client wants a web store to sell their t-shirts online, and they need to accept credit cards."
    
    print(f"Messy User Query: '{messy_query}'\n")
    print("Performing semantic vector search...\n")
    
    # 7. Query the Vector DB! We ask for the top 1 most relevant result (n_results=1)
    results = collection.query(
        query_texts=[messy_query],
        n_results=1
    )
    
    # 8. Output the results
    print("✅ MOST RELEVANT PRIVATE DATA FOUND:")
    print("-" * 40)
    # results['documents'][0][0] accesses the first result of the first query
    print(results['documents'][0][0]) 
    print("-" * 40)

if __name__ == "__main__":
    run_vector_search()