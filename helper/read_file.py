from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import UnstructuredExcelLoader


class ReadFile:
    def __init__(self, fileLocation):
        self.fileLocation = fileLocation

    def process(self, contentType):
        # matching the file types for loaders
        if contentType == "text/plain":
            loader = TextLoader(self.fileLocation)
            document = loader.load()
        elif contentType == "application/pdf":
            loader = PyPDFLoader(self.fileLocation)
            document = loader.load_and_split()
        elif (
            contentType
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            loader = Docx2txtLoader(self.fileLocation)
            document = loader.load()
        elif (
            contentType
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            loader = UnstructuredExcelLoader(self.fileLocation)
            document = loader.load()
        elif contentType == "text/csv":
            loader = CSVLoader(self.fileLocation)
            document = loader.load()
        else:
            # for unsupported file type
            return []
        
        for doc in document:
            doc.metadata["source"] = doc.metadata.get("source", self.fileLocation)
            doc.metadata["page"] = doc.metadata.get("page", 0)
                
        return document
