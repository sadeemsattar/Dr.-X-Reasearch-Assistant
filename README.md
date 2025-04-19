# Dr. X Research Assistant

Dr. X Research Assistant is an AI-powered tool designed to assist with document processing tasks such as summarization, translation, and question answering. It supports multiple document formats and provides a user-friendly interface for interaction.

## Features

- **Summarization**: Generate concise summaries of technical and academic content.
- **Translation**: Translate documents into multiple languages.
- **Question Answering**: Answer questions based on the content of uploaded documents.
- **Document Processing**: Supports `.docx`, `.pdf`, `.xlsx`, `.csv`, and `.txt` file formats.

## Prerequisites

1. **Python**: Ensure Python 3.8 or higher is installed.
2. **Ollama**: Install and configure Ollama for LLM-based tasks.

### Installing Ollama

1. Download and install Ollama from the [official website](https://ollama.ai/).
2. Start the Ollama server:
   ```bash
   ollama serve
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
   pip install -r requirements.txt
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

## .gitignore

The following files and directories are ignored by Git:

```
data/
temp/
.venv/
```

## Notes

- The `data/` and `temp/` directories are ignored by Git as specified in the `.gitignore` file.
- Ensure that the Ollama server is running before starting the application.
- The application uses `Qdrant` for vector storage and retrieval.

