import os
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import CTransformers
from langchain_huggingface import HuggingFaceEmbeddings
from config import INDEX_PATH, MODEL_PATH, PDF_PATH
from document_parser import extract_cv_sections

#Generate text embeddings (numeric representations) for semantic search
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

def initialize_ai():
    embeddings = get_embeddings()
    
    if os.path.exists(INDEX_PATH):
        vector_store = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        cv_data = extract_cv_sections(PDF_PATH)
        documents = [
            Document(
                page_content=content,
                metadata={"section": section}
            ) for section, content in cv_data.items()
        ]
        #creating searchable vector database
        vector_store = FAISS.from_documents(documents, embeddings)
        vector_store.save_local(INDEX_PATH)
    
    # Initialize CTransformers model
    llm = CTransformers(
        model=MODEL_PATH,
        model_type="mistral",
        config={'max_new_tokens': 512,
                'temperature': 0.1,
                'context_length': 2048,
                'gpu_layers': 0}
    )
    
    return vector_store, llm

# Initialize components
vector_store, llm = initialize_ai()
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

prompt_template = """[INST] Use this CV information:
{context}

Question: {question}
Provide a detailed answer using only the CV content: [/INST]"""

QA_PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# The complete Q&A pipeline:
# 1. Searches CV content (retriever)
# 2. Formats question + context (QA_PROMPT)
# 3. Generates answer (llm)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": QA_PROMPT},
    return_source_documents=True
)