# Dr. X Research Assistant

Dr. X Research Assistant is an AI-powered tool designed to assist with document processing tasks such as summarization, translation, and question answering. It supports multiple document formats and provides a user-friendly interface for interaction.

## Features

- **Summarization**: Generate concise summaries of technical and academic content.
- **Translation**: Translate documents into multiple languages.
- **Question Answering**: Answer questions based on the content of uploaded documents.
- **Document Processing**: Supports `.docx`, `.pdf`, `.xlsx`, `.csv`, and `.txt` file formats.

## Significant Discoveries

### 1. **Recursive Splitting for Efficient Text Processing**
   - The use of the `RecursiveCharacterTextSplitter` in [`helper/process_file.py`](helper/process_file.py) has proven to be a highly effective technique for handling large documents. 
   - By splitting text into manageable chunks of 1000 tokens with a 300-token overlap, the system ensures that:
     - Context is preserved across chunks, which is critical for tasks like summarization and question answering.
     - The LLM operates within its token limit, avoiding truncation or loss of information.
   - This approach balances efficiency and accuracy, making it suitable for processing diverse document types.

### 2. **Flexible File Reading with Modular Loaders**
   - The `ReadFile` class in [`helper/read_file.py`](helper/read_file.py) provides a modular and extensible framework for reading various file formats, including `.docx`, `.pdf`, `.xlsx`, `.csv`, and `.txt`.
   - Key discoveries include:
     - The ability to extract text and metadata (e.g., source, page number) from documents, which enhances traceability during downstream tasks.
     - The use of specialized loaders from the `langchain_community` library ensures robust handling of different file structures and formats.
     - This modular design allows for easy addition of support for new file types in the future.

### 3. **Vectorization for Semantic Search**
   - The integration of the `OllamaEmbeddings` model in [`helper/vector_store.py`](helper/vector_store.py) enables the conversion of text chunks into high-quality vector embeddings.
   - These embeddings are stored in the `Qdrant` vector database, which supports similarity-based retrieval with high accuracy.
   - Discoveries include:
     - The use of in-memory storage for low-latency operations, making the system responsive for real-time applications.
     - The embedding model (`nomic-embed-text:latest`) captures semantic meaning effectively, ensuring that retrieved chunks are contextually relevant to user queries.

### 4. **Preservation of Document Structure During Translation**
   - The `StructuredFileTranslator` class in [`actions/translate.py`](actions/translate.py) ensures that the structure of documents (e.g., tables, paragraphs) is preserved during translation.
   - This is particularly important for `.xlsx` and `.docx` files, where formatting plays a critical role in readability and usability.
   - The use of `GoogleTranslator` for translation provides reliable and accurate results, while the modular design allows for the integration of alternative translation APIs if needed.

### 5. **Streamlined Intent Detection**
   - The `detect_intent` function in [`main.py`](main.py) leverages the LLM to classify user queries into intents (`summarize`, `translate`, or `qa`).
   - This approach ensures that:
     - Queries are routed to the appropriate processing pipeline, optimizing resource utilization.
     - The system can handle diverse user requests without requiring explicit user input for task selection.

### 6. **Evaluation of Summarization Quality**
   - The `evaluate_summary` function in [`actions/summary.py`](actions/summary.py) uses ROUGE scores to quantitatively evaluate the quality of generated summaries.
   - This provides a feedback mechanism for improving the summarization pipeline and ensures that the output meets user expectations.

### 7. **Scalability and Extensibility**
   - The modular architecture of the system allows for easy scalability and extensibility:
     - New file formats can be supported by adding loaders to the `ReadFile` class.
     - Additional LLMs or embedding models can be integrated with minimal changes to the existing codebase.
   - This design ensures that the system can adapt to evolving user needs and technological advancements.

## Prerequisites

1. **Python**: Ensure Python 3.8 or higher is installed.
2. **Ollama**: Install and configure Ollama for LLM-based tasks.

### Installing Ollama

1. Download and install Ollama from the [official website](https://ollama.ai/).
2. Start the Ollama server:
   ```bash
   ollama serve
   ollama run llama3.2:3b
   ollama pull nomic-embed-text
   ```
3. Run llama3.2 model
    ```bash
    ollama run llama3.2:3b
    ```
4. Run Embedding model
    ```bash
    ollama pull nomic-embed-text
    ```


## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Dr.-X-Research-Assistant
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install --use-deprecated=legacy-resolver -r requirements.txt
   ```

4. Install additional system dependencies for `PyMuPDF` and `docx2txt` if required.

## Running the Project

1. Start the Streamlit application:
   ```bash
   streamlit run frontend.py
   ```

2. Open the application in your browser at `http://localhost:8501`.

3. Upload documents in supported formats (`.docx`, `.pdf`, `.xlsx`, `.csv`, `.txt`) through the web interface.

4. Use the chat interface to:
   - Summarize documents
   - Translate documents into a target language
   - Ask questions about the document content


## Notes

- The `data/` and `temp/` directories are ignored by Git as specified in the `.gitignore` file.
- Ensure that the Ollama server is running before starting the application.
- The application uses `Qdrant` for vector storage and retrieval.


