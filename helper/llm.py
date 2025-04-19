from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain.callbacks.manager import CallbackManager
from langchain_ollama import ChatOllama

import psutil



class LangchainLocal:
    def __init__(self, session_state, model="llama3.2:3b"):
        self.session_state = session_state
        self.llm = ChatOllama(
                base_url="http://localhost:11434",
                model=model,
                verbose=True,
                callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
                temperature=0.4,
                num_ctx=512,
                num_thread=max(1, int(psutil.cpu_count() * 0.9)),
                stream=True,
            )
        

    def get_context_retriever_chain(self, vector_store):
        retriever = vector_store.as_retriever()

        # Create a prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                (
                    "human",
                    "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation, keep it concise",
                ),
            ]
        )

        print("retriever_chain", prompt)
        retriever_chain = create_history_aware_retriever(self.llm, retriever, prompt)

        

        return retriever_chain

    def get_conversational_rag_chain(self, retriever_chain):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Answer the user's questions based on the below context:\n\n{context}",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        print("stuff_documents_chain", prompt)
        stuff_documents_chain = create_stuff_documents_chain(self.llm, prompt)
      

        return create_retrieval_chain(retriever_chain, stuff_documents_chain)


    def get_response(self, user_input, chat_history, vectorstore):
        retriever_chain = self.get_context_retriever_chain(vectorstore)
        conversational_rag_chain = self.get_conversational_rag_chain(retriever_chain)

        response_stream = conversational_rag_chain.stream(
            {"chat_history": chat_history, "input": user_input}
        )

        for chunk in response_stream:
            content = chunk.get("answer", "")
            yield content