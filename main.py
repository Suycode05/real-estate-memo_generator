from rag_pipeline import load_web_documents, split_documents, create_vector_store, get_retriever, create_rag_chain

if __name__ == "__main__":
    print("Loading documents...")
    documents = load_web_documents()

    print("Splitting documents...")
    chunks = split_documents(documents)

    print("Creating vector store...")
    vector_store = create_vector_store(chunks)

    retriever = get_retriever(vector_store)
    rag_chain = create_rag_chain(retriever)

    query="Generate a complete professional investment memo for a 3BHK apartment (approximately 1800 sq ft) in Civil Lines, Prayagraj priced at ₹65 lakhs for rental investment purpose. Include realistic rental yield estimation."
    print("Generating Investment Memo...")
    response = rag_chain.invoke(query)
    print("="*70)
    print("Executive Summary:")
    print("-"*30)
    print(response.executive_summary)
    print("\nPricing Analysis:")
    print(response.pricing_analysis)
    print("\nRental Yield Potential:")
    print(response.rental_yield_potential)
    print("\nRecommendation:", response.investment_recommendation)
    print("\nConfidence Score:", response.confidence_score)
    print("="*70)
