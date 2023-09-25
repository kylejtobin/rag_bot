# Custom modules
from src.utils.config import load_config, setup_environment_variables

# Primary Components
from llama_index import SimpleDirectoryReader, StorageContext, VectorStoreIndex, ServiceContext
from llama_index.embeddings import LangchainEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain.embeddings import OpenAIEmbeddings

# Utilities
import logging
import os
import shutil

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class QdrantCollectionManager:

    @staticmethod
    def collection_exists(client: QdrantClient, collection_name: str) -> bool:
        try:
            client.get_collection(collection_name)
            return True
        except Exception:
            return False

    @staticmethod
    def create_collection(client: QdrantClient, collection_name: str, vector_size: int):
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config={
                "size": vector_size,
                "distance": "Cosine"
            }
        )

    @staticmethod
    def ensure_collection(client: QdrantClient, collection_name: str, vector_size: int):
        if not QdrantCollectionManager.collection_exists(client, collection_name):
            QdrantCollectionManager.create_collection(client, collection_name, vector_size)

class DocumentLoader:

    def __init__(self, source_dir='/app/src/scraper/scraped_data', collection_name="techdocs"):
        self.source_dir = source_dir
        self.collection_name = collection_name
        self.CONFIG = load_config()
        setup_environment_variables(self.CONFIG)
        self.embed_model = LangchainEmbedding(OpenAIEmbeddings(openai_api_key = os.getenv("OPENAI_API_KEY")))
        self.client = QdrantClient(url="http://RAG_BOT_QDRANT:6333")

        if not QdrantCollectionManager.collection_exists(self.client, collection_name):
            QdrantCollectionManager.create_collection(self.client, collection_name, 1536)


    def load_documents(self):
        try:
            service_context = ServiceContext.from_defaults(embed_model=self.embed_model)
            documents = SimpleDirectoryReader(self.source_dir).load_data()
            vector_store = QdrantVectorStore(client=self.client, collection_name=self.collection_name)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, service_context=service_context)
            
            # Move the files after successfully loading them to the vector index
            self.move_files_to_out()
            
            return index
        except Exception as e:
            logging.error(f"load_documents: Error - {str(e)}")
            raise e
    
    def move_files_to_out(self):
        out_dir = '/app/src/scraper/out'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        for filename in os.listdir(self.source_dir):
            file_path = os.path.join(self.source_dir, filename)
            if os.path.isfile(file_path):
                shutil.move(file_path, os.path.join(out_dir, filename))
