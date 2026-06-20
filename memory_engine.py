# memory_engine.py
import chromadb
import datetime

class LongTermMemory:
    def __init__(self):
        """
        Initialize the local persistent ChromaDB client for long-term semantic memory.
        Source: ChromaDB Architecture Core Documentation.
        """
        # Establish a persistent database directory on the local disk
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Get or create a collection strictly dedicated to system conversations
        self.collection = self.chroma_client.get_or_create_collection(name="mindmate_memory")

    def save_message(self, gemini_client, user_id, role, text):
        """
        Generate embedding vectors using Gemini API and store them securely in ChromaDB.
        Source: Google GenAI SDK Reference Guide.
        """
        if not text.strip():
            return
        
        try:
            # Generate semantic embedding vector using Gemini's production embedding model
            response = gemini_client.models.embed_content(
                model="text-embedding-gecko-003",
                contents=text
            )
            embedding = response.embeddings[0].values
            
            # Construct a unique document ID based on timestamp
            doc_id = f"user_{user_id}_{datetime.datetime.now().timestamp()}"
            
            # Persist document metadata for multi-user data isolation and domain security
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    "user_id": int(user_id), 
                    "role": role, 
                    "timestamp": str(datetime.datetime.now())
                }]
            )
            print(f"Successfully committed message to Long-Term Memory for User {user_id}.")
        except Exception as e:
            print(f"Error saving to vector database: {e}")

    def retrieve_context(self, gemini_client, user_id, query_text, n_results=3):
        """
        Query the Vector DB using semantic similarity matching to fetch relevant past context.
        """
        if not query_text.strip():
            return ""
            
        try:
            # Generate the embedding vector for the current incoming user query
            response = gemini_client.models.embed_content(
                model="text-embedding-004",
                contents=query_text
            )
            query_embedding = response.embeddings[0].values
            
            # Execute semantic query filtering strictly by the active authenticated user_id
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"user_id": int(user_id)}
            )
            
            # Format and stitch together the retrieved historical text fragments
            if results and results['documents'] and results['documents'][0]:
                relevant_docs = results['documents'][0]
                context_str = "\n".join([f"- {doc}" for doc in relevant_docs])
                return context_str
        except Exception as e:
            print(f"Error querying long-term memory: {e}")
            return ""
        return ""