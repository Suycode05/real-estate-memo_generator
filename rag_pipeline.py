import os
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from financial_calculator import RealEstateFinancialCalculator
from dynamic_search import dynamic_web_search

load_dotenv()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

class InvestmentMemo(BaseModel):
    executive_summary: str = Field(...,min_length=50)
    property_details: str = Field(...)
    market_analysis: str = Field(...)
    pricing_analysis: str = Field(...,)
    rental_yield_potential: str = Field(...)
    infrastructure_growth: str = Field(...)
    risk_analysis: str = Field(...)
    investment_recommendation: Literal["Strong Buy", "Buy", "Hold", "Avoid"] = Field(...)
    confidence_score: int = Field(..., ge=0, le=100)
    key_sources: list[str] = Field(default_factory=list)

# 1.Load documents
def load_web_documents():
    urls=[
        "https://www.magicbricks.com/Property-Rates-Trends/ALL-RESIDENTIAL-rates-in-Allahabad",
        "https://www.magicbricks.com/blog/prayagraj-infrastructure-and-real-estate-developments/137974.html",

        "https://www.magicbricks.com/rera-registered-projects-Allahabad",
        "https://www.99acres.com/rera-registered-projects-in-allahabad-ffid",

        "https://www.magicbricks.com/news/property-prices-in-these-religious-cities-are-witnessing-record-high-rbmb/145092.html",
]
    
    all_docs=[]
    for url in urls:
        try:
            print(f"Loading {url}...")
            loader=WebBaseLoader(web_paths=[url], header_template=headers)
            documents=loader.load()
            all_docs.extend(documents)
            print(f"successfully loaded: {url[:70]}")
        except Exception as e:
            print(f"Error loading {url}: {e}")

    print(f"Total documents loaded: {len(all_docs)}")
    return all_docs

# 2.Split documents
def split_documents(documents):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200, separators=["\n\n", "\n", " ", "","."])
    chunks=text_splitter.split_documents(documents)
    return chunks

# 3.Create vector store
def create_vector_store(chunks):
    if not chunks:
        raise ValueError("No documents to create vector store.")
    print(f"Creating vector store") 
    embeddings=HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    vector_store=Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory="./chroma_db")
    return vector_store

# 4.Create Retriever
def get_retriever(vector_store):
    retriever=vector_store.as_retriever(search_kwargs={"k":12})
    return retriever

# 5. RAG Chain
def create_rag_chain(retriever):
    llm=ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)
    template="""You are a **Senior Real Estate Investment Analyst** with 15+ years experience in Tier-2 Indian cities. Generate a **professional Investment Memo** for the given query.
    Latest Real-time Web Search Results: {web_context}
    Static Knowledge Base: {context}
    Query: {query}

    Rules:
    - Be data-driven. Use actual numbers from context (price/sqft, rental trends, etc.)
    - Be balanced and realistic. Don't overhype.
    - Mention RERA status when possible.
    - Include specific locallity insights for Prayagraj.
    - For rental yield and financial metrics, calculate realistic estimates.

    Return in structured format."""

    prompt=ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    rag_chain=({"context": retriever | format_docs,"web_context":lambda x: dynamic_web_search(x), "query": RunnablePassthrough()} | prompt | llm.with_structured_output(InvestmentMemo))
    return rag_chain