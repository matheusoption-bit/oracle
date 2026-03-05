"""
RAG Engine usando LlamaIndex + pgvector.
"""

from pathlib import Path
import os

from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.postgres import PGVectorStore


class RAGEngine:
    """
    Motor de RAG para indexar e consultar repositórios.
    """

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.vector_store = PGVectorStore.from_params(
            database=os.getenv("DATABASE_URL").split("/")[-1],
            host=os.getenv("SUPABASE_URL").replace("https://", "").split(".")[0],
            password=os.getenv("SUPABASE_PASSWORD"),
            port=5432,
            user="postgres",
            table_name="embeddings",
            embed_dim=1536,
        )

        self.embed_model = OpenAIEmbedding(
            model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY")
        )

    def ingest_repository(self, repo_path: str):
        """
        Indexa repositório.

        Filtros: .ts, .tsx, .py, .md
        Ignora: node_modules, .git, dist, build
        """

        reader = SimpleDirectoryReader(
            input_dir=repo_path,
            required_exts=[".ts", ".tsx", ".py", ".md"],
            exclude=["node_modules", ".git", "dist", "build", ".next"],
        )

        documents = reader.load_data()

        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=self.embed_model,
            show_progress=True,
        )

        # Salva manifest
        manifest = {"total_docs": len(documents), "indexed_at": datetime.now().isoformat()}

        (self.workspace_path / "index" / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

        return index

    def query_codebase(self, question: str, top_k: int = 5) -> str:
        """
        Consulta semântica no codebase.

        Tool: oracle_query_codebase
        """

        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        index = VectorStoreIndex.from_vector_store(
            self.vector_store,
            storage_context=storage_context,
            embed_model=self.embed_model,
        )

        query_engine = index.as_query_engine(similarity_top_k=top_k)

        response = query_engine.query(question)

        return str(response)
