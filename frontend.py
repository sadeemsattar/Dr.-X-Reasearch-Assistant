
import time
import logging
import streamlit as st
from openai import OpenAI
# from helper.llm import LangchainLocal
from helper.read_file import ReadFile
from helper.process_file import ProcessFile
from helper.vector_store import Vectorstore
from langchain_core.messages import AIMessage, HumanMessage
from main import (
    detect_intent,
    summarize,
    translate,
    answer_question,
    extract_language,
    detect_file_type
)
from actions.summary import evaluate_summary



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DocumentAssistant")

# LLM Client
llm = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


def clear_cache():
    keys = list(st.session_state.keys())
    for key in keys:
        st.session_state.pop(key)


def process_prompt():
    if st.sidebar.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.chat_dialog_history = []
    st.sidebar.button("📜 New Chat", use_container_width=True, on_click=clear_cache)

    # langchain_local = LangchainLocal(st.session_state)

    for message in st.session_state.chat_dialog_history:
        with st.chat_message("AI" if isinstance(message, AIMessage) else "Human"):
            st.write(message.content)

    if not st.session_state.chat_dialog_history:
        with st.chat_message("AI"):
            st.write("Hello! How can I help you today? 🤖")

    if prompt := st.chat_input("Ask a question about your documents"):
        with st.chat_message("Human"):
            st.write(prompt)
        with st.chat_message("AI"):
            intent, _ = detect_intent(query=prompt)


            if intent == "summarize":
                print("Summarize Tool")
                output, _ = summarize(st.session_state.text)
                score = evaluate_summary(output, st.session_state.text)
            elif intent == "translate":
                print("Translate Tool")
                target_lang = extract_language(prompt)
                output, _ = translate(st.session_state.file, target_lang)
            elif intent == "qa":
                print("Question Answering Tool")
                output, _ = answer_question(st.session_state.vectorstore, prompt, st.session_state.chat_dialog_history)
                
            else:
                output = "Sorry, I couldn't understand your request."

            print(f"\n🧠 Intent: {intent}\n📄 Output:\n{output}\n")
           

            response = st.write(
                output
            )
        st.session_state.chat_dialog_history.extend([
            HumanMessage(content=prompt),
            AIMessage(content=output)
        ])


def initialize_session_state():
    if "chat_dialog_history" not in st.session_state:
        st.session_state.chat_dialog_history = []
    if "disabled" not in st.session_state:
        st.session_state.disabled = True
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = []
    if "file" not in st.session_state:
        st.session_state.file = None
    if "text" not in st.session_state:
        st.session_state.text = None
    if "error" not in st.session_state:
        st.session_state.error = False


def initialize_ui():
    st.set_page_config(
        page_title="Dr. X Reasearch Assistant",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None,
    )
    st.title("Chat With Dr. X Reasearch Assistant ")
    initialize_session_state()


def process_documents():
    if st.session_state.disabled:
        st.write("🔒 Please upload and process your Documents to unlock the question field.")
        set_input_tab()
    else:
        process_prompt()


def set_input_tab():
    tab1 = st.tabs(["Documents"])[0]

    with tab1:
        documents = st.file_uploader(
            "Upload the Documents here:",
            accept_multiple_files=True,
            type=["xlsx", "xls", "csv", "docx", "pdf", "txt"],
        )
        if documents and st.button("Process", type="secondary", use_container_width=True):
            st.toast(
                "Hang tight! The documents are being processed. This might take a few minutes.",
                icon="🤖",
            )
            with st.spinner("Processing..."):
                if st.session_state.disabled:
                    process_uploaded_documents(documents)
                    st.session_state.disabled = False
                    st.rerun()


def process_uploaded_documents(documents):
    text_chunks = []
    import os

    TEMP_DIR = "temp"
    os.makedirs(TEMP_DIR, exist_ok=True)


    if documents is not None:
        for doc in documents:
            st.write(f"Processing {doc.name}...")  

            file_path = os.path.join(TEMP_DIR, doc.name)
            with open(file_path, "wb") as f:
                f.write(doc.getbuffer())

            # Read and process the file
            file_content = ReadFile(file_path).process(doc.type)
            st.session_state.file = file_path
            data = ProcessFile(file_content).process()
            st.session_state.text = data
            text_chunks.extend(data)

    get_vectorstore_instance = Vectorstore()
    st.session_state.vectorstore = get_vectorstore_instance.get_vectorstore(
        text_chunks
    )

    if st.session_state.vectorstore is None:
        st.error("Unable to parse the document. It may be empty or in an unsupported format. Upload a new document and try again.")
        st.stop()



def main():
    initialize_ui()
    process_documents()


if __name__ == "__main__":
    main()
