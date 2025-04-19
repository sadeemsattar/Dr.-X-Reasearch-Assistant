import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter



class ProcessFile:
    def __init__(self, document, encoding_name="cl100k_base", chunk_size=1000, chunk_overlap=300):
        self.document = document
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def process(self):
        
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=lambda text: len(self.encoding.encode(text)),
        )

        chunks = splitter.split_documents(self.document)
        return chunks

      