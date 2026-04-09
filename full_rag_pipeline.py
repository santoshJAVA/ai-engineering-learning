import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def setup_database():
    """Sets up the in-memory ChromaDB and populates it with our pricing rules."""
    chroma_client = chromadb.Client()
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ.get("OPENAI_API_KEY"),
        model_name="text-embedding-3-small"
    )
    
    collection = chroma_client.create_collection(name="freelance_pricing", embedding_function=openai_ef)
    
    collection.add(
        documents=[
            "Base Shopify E-commerce setup with 5 pages and payment gateway integration costs $4,500. Takes 3 weeks.",
            "Custom React frontend with a Node.js backend costs $12,000. Takes 8 weeks. Maintenance is $500/month.",
            "Simple WordPress landing page for marketing campaigns costs $1,200. Takes 1 week.",
            "SEO Audit and technical optimization costs $800 as a one-time fee."
        ],
        ids=["id_ecommerce", "id_custom_app", "id_landing_page", "id_seo"]
    )
    return collection

def generate_proposal(user_query: str, collection) -> str:
    """The full RAG loop: 1. Retrieve context, 2. Inject context, 3. Generate response."""
    
    print(f"\n--- STEP 1: RETRIEVAL ---")
    print(f"User Query: '{user_query}'")
    
    # 1. RETRIEVE the relevant context from the Vector DB
    results = collection.query(
        query_texts=[user_query],
        n_results=1
    )
    
    retrieved_context = results['documents'][0][0]
    print(f"Retrieved internal pricing context: '{retrieved_context}'")
    
    print("\n--- STEP 2 & 3: AUGMENT & GENERATE ---")
    print("Calling OpenAI to draft the final proposal using ONLY the retrieved context...")
    
    # 2. AUGMENT the prompt with the retrieved context
    # Notice we strictly instruct the LLM to only use the provided context.
    system_prompt = f"""
    You are an expert freelance proposal writer. 
    You must draft a polite, professional proposal for a client based on their request.
    
    CRITICAL RULE: You must ONLY use the pricing and timeline rules provided in the INTERNAL CONTEXT below. 
    Do not invent prices or timelines.
    
    INTERNAL CONTEXT: 
    {retrieved_context}
    """
    
    # 3. GENERATE the final output
    completion = client.chat.completions.create(
        model="gpt-4o", # We use 4o here for better, more human-like writing
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Client request: {user_query}"}
        ]
    )
    
    return completion.choices[0].message.content

if __name__ == "__main__":
    # Setup our DB
    db_collection = setup_database()
    
    # The messy voice memo from the freelancer
    messy_memo = "I just talked to Sarah. She wants a basic online shop to sell her handmade jewelry. She needs a cart, a checkout, and maybe like 3 or 4 pages total."
    
    # Run the full RAG pipeline
    final_proposal = generate_proposal(messy_memo, db_collection)
    
    print("\n✅ FINAL GENERATED PROPOSAL:\n")
    print("=" * 50)
    print(final_proposal)
    print("=" * 50)