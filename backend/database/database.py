import iris
import os
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import json

from langchain_iris import IRISVector

# Dynamically find all PDFs in the 'data' directory relative to this module
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get current module directory
DATA_DIR = os.path.join(BASE_DIR, "data")  # Define relative folder for PDFs

# Collect all PDFs in the data folder
pdf_paths = [
    os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".pdf")
]

#if not os.environ.get("OPENAI_API_KEY"):
#    os.environ["OPENAI_API_KEY"] = "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"

# Connect to IRIS database
username = 'demo'
password = 'demo'
hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
port = 1972
namespace = 'USER'
CONNECTION_STRING = f"{hostname}:{port}/{namespace}"
sql_conn = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"

def init_database():
    print(CONNECTION_STRING)

    # Connect to InterSystems IRIS
    conn = iris.connect(CONNECTION_STRING, username, password, ssl=True)
    cursor = conn.cursor()

    cursor.execute("SET OPTION PKEY_IS_IDKEY = true")
    conn.commit()

    # create table to store pdf
    init_vector_table(sql_conn)

    create_health_tables(cursor, conn)

    cursor.close()
    conn.close()


def init_vector_table(conn_string):
    """Creates a table in IRIS to store document embeddings if it does not exist."""
    embeddings_model = OpenAIEmbeddings()
    print("Creating database")
    docs = prepare_pdfs()

    # This creates a persistent vector store (a SQL table). You should run this ONCE only
    IRISVector.from_documents(
        embedding=embeddings_model,
        documents=docs,
        collection_name="Documents",
        connection_string=conn_string,
    )


def prepare_pdfs():
    """Loads PDFs, extracts text, chunks it, generates embeddings, and stores in IRIS."""

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = []

    for pdf_path in pdf_paths:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()

        # Split text into chunks
        doc_splits = text_splitter.split_documents(pages)

        for doc in doc_splits:
            documents.append(Document(page_content=doc.page_content, metadata={"source": pdf_path}))

    return documents

def create_health_tables(cursor, conn):
    """Creates tables in IRIS for storing user health analysis and unanswered questions."""

    # Create HealthAnalysis table with an auto-incrementing ID as the primary key
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS HealthAnalysis (
            id SERIAL PRIMARY KEY,  -- Unique identifier for each health analysis entry
            name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            mental_health FLOAT,
            knowledge FLOAT,
            physical_health FLOAT,
            preventive_care FLOAT,
            health_seeking FLOAT
        )
    """)

    # Create UnansweredQuestions table with a foreign key linking to HealthAnalysis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UnansweredQuestions (
            id SERIAL PRIMARY KEY,  -- Unique identifier for each unanswered question
            health_id INT,  -- Foreign key linking to HealthAnalysis
            question TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (health_id) REFERENCES HealthAnalysis(id) ON DELETE CASCADE
        )
    """)

    # Commit the changes to the database
    conn.commit()

def get_health_records():
    conn = iris.connect(CONNECTION_STRING, username, password)
    cursor = conn.cursor()

    # Query all records from HealthAnalysis
    cursor.execute("SELECT * FROM HealthAnalysis ORDER BY timestamp DESC")
    columns = [col[0] for col in cursor.description]  # Get column names
    records = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return records

def get_individual_records(health_id):
    """Retrieves a list of unanswered questions for a given health_id."""
    conn = iris.connect(CONNECTION_STRING, username, password)
    cursor = conn.cursor()

    health_analysis_query = """
            SELECT * FROM HealthAnalysis WHERE id = ?
            """
    cursor.execute(health_analysis_query, [health_id])
    columns = [col[0] for col in cursor.description]  # Get column names
    health_records = dict(zip(columns, cursor.fetchone()))

    unanswered_query = """
    SELECT question FROM UnansweredQuestions WHERE health_id = ?
    """
    cursor.execute(unanswered_query, [health_id])
    questions = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return {
        "name": health_records["name"],
        "timestamp": health_records["timestamp"],
        "mental_health": health_records["mental_health"],
        "knowledge": health_records["knowledge"],
        "physical_health": health_records["physical_health"],
        "preventive_care": health_records["preventive_care"],
        "health_seeking": health_records["health_seeking"],
        "unanswered_questions": questions
    }


if __name__ == "__main__":
    init_database()
    print("Done!")
