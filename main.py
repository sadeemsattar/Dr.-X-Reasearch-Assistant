import os
import time
import logging
from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from actions.translate import StructuredFileTranslator
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain_ollama import ChatOllama
import psutil




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DocumentAssistant")

def track_tokens(task_name="LLM Task"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            output, total_tokens = result if isinstance(result, tuple) else (result, None)
            duration = time.time() - start or 1e-5
            logger.info(f"{task_name} | Tokens: {total_tokens}, Time: {duration:.2f}s, TPS: {total_tokens / duration if total_tokens else 'N/A'}")
            return result
        return wrapper
    return decorator

# LLM Client
llm = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
retriever_llm = ChatOllama(
                base_url="http://localhost:11434",
                model="llama3.2:3b",
                verbose=True,
                callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
                temperature=0.4,
                num_ctx=512,
                num_thread=max(1, int(psutil.cpu_count() * 0.9)),
                stream=True,
            )

# Intent Detection
@track_tokens("Intent Detection")
def detect_intent(query):
    system_prompt = "You are an intent detection assistant. Classify the user's intent as one of: " \
    "summarize: when user want for summarization , translate: when user want to translate the document, qa."
    user_prompt = f"Classify the following user query:\n\n{query}\n\nRespond with only one word: summarize, translate, or qa."
    response = llm.chat.completions.create(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    content = response.choices[0].message.content.strip().lower()
    return content, response.usage.total_tokens

@track_tokens("Summarization")
def summarize(data):
    summaries = []
    for i, chunk in enumerate(data):
        response = llm.chat.completions.create(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes technical and academic content accurately."},
                {"role": "user", "content": f"Summarize the following passage:\n\n{chunk}"}
            ]
        )
        summaries.append(response.choices[0].message.content.strip())

    final_summary = "\n\n".join(summaries)
    print("\n📝 FINAL SUMMARY:\n", final_summary)
    return final_summary, response.usage.total_tokens
   

@track_tokens("Translation")
def translate(file_path, target_lang):
    translator = StructuredFileTranslator(file_path=file_path, target_lang=target_lang)
    translated_path = translator.translate()
    return f"✅ Translated file saved at: {translated_path}", None

# mantain conversation context
def get_context_retriever_chain(vector_store):
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
    retriever_chain = create_history_aware_retriever(retriever_llm, retriever, prompt)

    

    return retriever_chain


# get relevent data from vector store
def get_conversational_rag_chain(retriever_chain):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the user's questions based on the below context:\n\n{context}",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),llm
        ]
    )
    print("stuff_documents_chain", prompt)
    stuff_documents_chain = create_stuff_documents_chain(retriever_llm, prompt)
    

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)


#  get relevent document havine=g simillarity > 0.8
@track_tokens("QA (RAG)")
def answer_question(vector_store, question , chat_history):

    # retriever_chain = get_context_retriever_chain(vector_store)
    # conversational_rag_chain = get_conversational_rag_chain(retriever_chain)

    # response_stream = conversational_rag_chain.stream(
    #     {"chat_history": chat_history, "input": question}
    # )

    # for chunk in response_stream:
    #     content = chunk.get("answer", "")
    #     yield content

    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.8}
    )
    docs = retriever.invoke(question)
    prompt = f"""Use the following Context and Chat History to answer the user's question.

    Context:
    {docs}

    Chat History:
    {chat_history}

    Question: {question}

    Answer:"""
    response = llm.chat.completions.create(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip(), response.usage.total_tokens

def extract_language(query):
    prompt = f"""
        You are a helpful assistant. A user is asking to translate a document. 
        From the following query, extract the language the document should be translated **into**. 
        If no language is specified, assume English.

        Query: "{query}"

        Respond with only the name of the target language in lowercase (e.g., "english", "arabic").
    """
    response = llm.chat.completions.create(
        model="llama3.2:3b",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip().lower()

def detect_file_type(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    return {
        ".txt": "text/plain",
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".csv": "text/csv",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }.get(ext, None)
