"""PDF ingestion, chunking, embedding, and Pinecone upload."""

import os
from typing import List

import pymupdf
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from pydantic import BaseModel
from pinecone import Pinecone, ServerlessSpec

from src.config import Settings


class IngestionStats(BaseModel):
    """Statistics from ingestion process."""

    pdf_path: str
    num_pages: int
    num_chunks: int
    vectors_uploaded: int
    embedding_model: str
    pinecone_index: str


class DocumentIngestionPipeline:
    """Handles PDF ingestion, chunking, embedding, and Pinecone upload."""

    def __init__(self, settings: Settings):
        """Initialize the ingestion pipeline."""

        self.settings = settings
        self.logger = settings.get_logger()
        self.embeddings = None
        self.pc = None

    def validate_pdf_exists(self) -> bool:
        """Validate that the PDF file exists."""

        if not os.path.exists(self.settings.pdf_path):
            self.logger.error(
                f"PDF not found at {self.settings.pdf_path}"
            )
            return False

        self.logger.info(
            f"PDF found at {self.settings.pdf_path}"
        )

        return True

    def load_pdf(self) -> List:
        """Load PDF using PyMuPDF."""

        if not self.validate_pdf_exists():
            raise FileNotFoundError(
                f"PDF not found at {self.settings.pdf_path}"
            )

        try:
            self.logger.info(
                f"Loading PDF from {self.settings.pdf_path}..."
            )

            pdf = pymupdf.open(self.settings.pdf_path)
            documents = []

            for page_number, page in enumerate(pdf):
                text = page.get_text("text")

                if text.strip():
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": self.settings.pdf_path,
                                "page": page_number
                            }
                        )
                    )

            pdf.close()

            self.logger.info(
                f"Loaded {len(documents)} pages with text from PDF"
            )

            return documents

        except Exception as e:
            self.logger.error(
                f"Error loading PDF: {e}"
            )

            raise ValueError(
                f"Failed to load PDF: {e}"
            )

    def chunk_documents(self, documents: List) -> List:
        """Split PDF documents into chunks."""

        self.logger.info(
            f"Splitting documents into chunks "
            f"(size={self.settings.chunk_size}, "
            f"overlap={self.settings.chunk_overlap})..."
        )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                " ",
                ""
            ]
        )

        chunks = splitter.split_documents(documents)

        self.logger.info(
            f"Created {len(chunks)} chunks"
        )

        return chunks

    def generate_embeddings(self) -> OpenAIEmbeddings:
        """Initialize OpenAI embedding model."""

        self.logger.info(
            f"Initializing embeddings model: "
            f"{self.settings.embedding_model}..."
        )

        self.embeddings = OpenAIEmbeddings(
            model=self.settings.embedding_model,
            api_key=self.settings.openai_api_key
        )

        self.logger.info(
            "Embeddings model initialized"
        )

        return self.embeddings

    def setup_pinecone(self) -> Pinecone:
        """Connect to Pinecone and create index if required."""

        self.logger.info(
            f"Connecting to Pinecone with index: "
            f"{self.settings.pinecone_index_name}..."
        )

        try:
            self.pc = Pinecone(
                api_key=self.settings.pinecone_api_key
            )

            existing_indexes = self.pc.list_indexes()

            index_names = [
                index["name"]
                for index in existing_indexes
            ]

            if self.settings.pinecone_index_name not in index_names:

                self.logger.info(
                    f"Creating index "
                    f"{self.settings.pinecone_index_name} "
                    f"(dimension="
                    f"{self.settings.pinecone_dimension}, "
                    f"metric=cosine)..."
                )

                self.pc.create_index(
                    name=self.settings.pinecone_index_name,
                    dimension=self.settings.pinecone_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.settings.pinecone_environment
                    )
                )

                self.logger.info(
                    "Pinecone index creation requested"
                )

            else:
                self.logger.info(
                    f"Pinecone index "
                    f"'{self.settings.pinecone_index_name}' "
                    f"already exists"
                )

            self.logger.info(
                f"Pinecone index "
                f"'{self.settings.pinecone_index_name}' ready"
            )

            return self.pc

        except Exception as e:

            self.logger.error(
                f"Pinecone connection error: {e}"
            )

            raise

    def upload_vectors(self, chunks: List) -> int:
        """Generate embeddings and upload vectors to Pinecone."""

        if not self.embeddings:
            raise ValueError(
                "Embeddings not initialized. "
                "Call generate_embeddings() first."
            )

        if not self.pc:
            raise ValueError(
                "Pinecone not initialized. "
                "Call setup_pinecone() first."
            )

        self.logger.info(
            f"Generating embeddings for "
            f"{len(chunks)} chunks..."
        )

        index = self.pc.Index(
            self.settings.pinecone_index_name
        )

        vectors_to_upsert = []

        for i, chunk in enumerate(chunks):

            try:
                embedding = self.embeddings.embed_query(
                    chunk.page_content
                )

                metadata = {
                    "source": chunk.metadata.get(
                        "source",
                        "unknown"
                    ),
                    "page": chunk.metadata.get(
                        "page",
                        0
                    ),
                    "chunk_index": i,
                    "content": chunk.page_content
                }

                vector = (
                    f"chunk_{i}",
                    embedding,
                    metadata
                )

                vectors_to_upsert.append(vector)

                if (i + 1) % 10 == 0:
                    self.logger.info(
                        f"Processed "
                        f"{i + 1}/{len(chunks)} chunks"
                    )

            except Exception as e:

                self.logger.warning(
                    f"Error processing chunk {i}: {e}"
                )

        batch_size = 100
        uploaded = 0

        for i in range(
            0,
            len(vectors_to_upsert),
            batch_size
        ):

            batch = vectors_to_upsert[
                i:i + batch_size
            ]

            try:

                index.upsert(
                    vectors=batch
                )

                uploaded += len(batch)

                self.logger.info(
                    f"Uploaded batch "
                    f"{i // batch_size + 1}"
                )

            except Exception as e:

                self.logger.error(
                    f"Error uploading batch: {e}"
                )

                raise

        self.logger.info(
            f"Successfully uploaded "
            f"{uploaded} vectors to Pinecone"
        )

        return uploaded

    def run_ingestion(self) -> IngestionStats:
        """Execute complete ingestion pipeline."""

        self.logger.info("=" * 60)
        self.logger.info(
            "STARTING DOCUMENT INGESTION PIPELINE"
        )
        self.logger.info("=" * 60)

        try:

            # Step 1: Load PDF
            documents = self.load_pdf()
            num_pages = len(documents)

            # Step 2: Split into chunks
            chunks = self.chunk_documents(
                documents
            )
            num_chunks = len(chunks)

            # Step 3: Initialize embeddings
            self.generate_embeddings()

            # Step 4: Connect to Pinecone
            self.setup_pinecone()

            # Step 5: Upload vectors
            vectors_uploaded = self.upload_vectors(
                chunks
            )

            stats = IngestionStats(
                pdf_path=self.settings.pdf_path,
                num_pages=num_pages,
                num_chunks=num_chunks,
                vectors_uploaded=vectors_uploaded,
                embedding_model=self.settings.embedding_model,
                pinecone_index=self.settings.pinecone_index_name
            )

            self.logger.info("=" * 60)
            self.logger.info(
                "INGESTION PIPELINE COMPLETED SUCCESSFULLY"
            )
            self.logger.info(
                f"Pages: {stats.num_pages}"
            )
            self.logger.info(
                f"Chunks: {stats.num_chunks}"
            )
            self.logger.info(
                f"Vectors uploaded: "
                f"{stats.vectors_uploaded}"
            )
            self.logger.info("=" * 60)

            return stats

        except Exception as e:

            self.logger.error(
                f"Ingestion pipeline failed: {e}"
            )

            raise