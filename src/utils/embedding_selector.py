from pydantic import BaseModel
from typing import Optional
from src.utils.config import load_config

CONFIG = load_config()


# Pydantic model for configuration
class EmbeddingConfig(BaseModel):
    type: str
    huggingface_model: Optional[str] = "sentence-transformers/multi-qa-mpnet-base-dot-v1"


class EmbeddingSelector:
    def __init__(self, config: EmbeddingConfig):
        self.config = config

    def get_embedding_model(self):
        if self.config.type == "openai":
            from llama_index.embeddings import OpenAIEmbedding
            return OpenAIEmbedding()
        elif self.config.type == "local":
            from llama_index.embeddings import HuggingFaceEmbedding
            return HuggingFaceEmbedding(model_name=self.config.huggingface_model)
        else:
            raise ValueError(f"Unsupported embedding type: {self.config.type}")
