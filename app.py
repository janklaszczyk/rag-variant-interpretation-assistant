from openai import OpenAI
from langchain import hub
import streamlit as st
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
import json
import os
from dotenv import load_dotenv

from function_calls import (
    get_consequence_info,
    tools,
    get_clinical_info,
    show_literature,
    get_gene_name,
)

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = "RAG_Variant_Interpretation_Assistant"

PERSIST_DIR = "./chroma_langchain_db"
COLLECTION_NAME = "variant_annotation_kb"
LLM = "gpt-3.5-turbo"

@st.cache_resource
def load_vectorstore():
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR,
    )
    return vectorstore

vectorstore = load_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatOpenAI(model=LLM, temperature=0)

RAG_PROMPT = ChatPromptTemplate.from_template(
    """
You are VariantAI, a helpful assistant for genomic variant interpretation.
Answer user questions using the provided context. If the answer is not in context, say you don’t know.

Context:
{context}

Question:
{question}
"""
)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.set_page_config(page_title="VariantAI", page_icon="🧬", layout="centered")
st.title("🧬 VariantAI - Genomic Variant Interpreter")
st.write(
    "This app combines powerful LLM models with a specialized genomic knowledge base to provide accurate, context-aware answers about genetic variants. \
Using Retrieval-Augmented Generation (RAG), it retrieves relevant scientific data from curated sources and integrates it with AI-driven natural language understanding \
to assist researchers and clinicians in variant analysis.*"
)
st.caption("*For research use only")
st.write(
    "External sources and tools used by VariantAI which can be easily evoked by the user prompt:"
)
col1, col2 = st.columns(2)
with col1:
    st.image(
        "https://docs.myvariant.info/en/latest/_images/myvariant.png",
        width=150,
    )
    st.write("- Gets clinical significance", )
    st.write("- Gets variant's gene", )
    st.write("- Gets genetic consequence", )
with col2:
    st.image(
        "https://localo.com/pl/assets/img/definitions/what-is-google-scholar.webp",
        width=200,
    )
    st.write("- Search literature", )
st.title("Chat:")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.sidebar.header("Settings")

if st.sidebar.button("🔄 Restart Chat"):
    st.session_state["messages"] = []
st.sidebar.download_button(
    "🔽 Download Chat",
    data=json.dumps(st.session_state["messages"]),
    file_name="chat_history.json",
)

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

if prompt := st.chat_input("Ask about a genetic variant..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    docs = retriever.get_relevant_documents(prompt)
    context_text = "\n\n".join([d.page_content for d in docs])
    rag_prompt = RAG_PROMPT.format(context=context_text, question=prompt)

    completion = client.chat.completions.create(
        model=LLM,
        messages=[
            {
                "role": "system",
                "content": "You are VariantAI, a genomic variant interpreter.",
            },
            {"role": "user", "content": str(rag_prompt)},
        ],
        tools=tools
    )

    message = completion.choices[0].message
    
    if getattr(message, "tool_calls", None):
        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            if fn_name == "show_literature":
                tool_result = show_literature(**fn_args)
            elif fn_name == "get_clinical_info":
                tool_result = get_clinical_info(**fn_args)
            elif fn_name == "get_consequence_info":
                tool_result = get_consequence_info(**fn_args)
            elif fn_name == "get_gene_name":
                tool_result = get_gene_name(**fn_args)
            else:
                tool_result = f"Unknown tool"

            completion_final = client.chat.completions.create(
                model=LLM,
                messages=[
                    {
                        "role": "system",
                        "content": "You are VariantAI, a genomic variant interpreter.",
                    },
                    {"role": "user", "content": rag_prompt},
                    message,
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    },
                ],
            )
            final_answer = completion_final.choices[0].message.content
            st.session_state.messages.append(
                {"role": "assistant", "content": final_answer}
            )
            st.chat_message("assistant").markdown(final_answer)

    else:
        st.session_state.messages.append(
            {"role": "assistant", "content": message.content}
        )
        st.chat_message("assistant").markdown(message.content)
