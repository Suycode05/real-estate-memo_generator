import streamlit as st
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from rag_pipeline import get_retriever, create_rag_chain
from financial_calculator import RealEstateFinancialCalculator
from datetime import datetime
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

st.set_page_config(page_title="Prayagraj Real Estate AI", layout="wide", page_icon="🏠")

st.title("🏠 AI Real Estate Investment Memo Generator")
st.markdown("### Professional Analysis for Prayagraj Properties | Real-time Data")

with st.sidebar:
    st.header("📍 Property Details")
    location = st.text_input("Location/Area", "Civil Lines, Prayagraj")
    property_type = st.selectbox("Property Type", ["3BHK Apartment", "2BHK Apartment", "Villa", "Plot", "Commercial Space"])
    size = st.number_input("Size (sq ft)", min_value=500, value=1800)
    price = st.number_input("Price (₹ in Lakhs)", min_value=10.0, value=65.0)
    expected_rent = st.number_input("Expected Monthly Rent (₹)", min_value=5000, value=25000)
    purpose = st.selectbox("Investment Purpose", ["Rental Income", "Capital Appreciation", "Both"])
    
    st.divider()
    generate_button = st.button("🚀 Generate Professional Investment Memo", type="primary", use_container_width=True)

def create_pdf(memo, financials, location, property_type, price, size, expected_rent):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=20)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=10)
    
    story = []
    
    # Header
    story.append(Paragraph(f"Investment Memo: {property_type} in {location}", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %B %Y')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Recommendation
    story.append(Paragraph("Investment Recommendation", heading_style))
    story.append(Paragraph(f"<b>{memo.investment_recommendation}</b> (Confidence: {memo.confidence_score}%)", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(memo.executive_summary, styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Financial Metrics
    story.append(Paragraph("Financial Analysis", heading_style))
    data = [
        ["Metric", "Value"],
        ["Price per sq ft", f"₹{financials['price_per_sqft']}"],
        ["Cap Rate", f"{financials['cap_rate']}%"],
        ["Cash on Cash Return", f"{financials.get('cash_on_cash', 'N/A')}%"],
        ["Projected 5-Year ROI", f"{financials['projected_5yr_roi']}%"],
        ["Monthly Rent", f"₹{financials['monthly_rent_assumed']}"],
    ]
    
    table = Table(data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Risk Analysis
    story.append(Paragraph("Risk Analysis", heading_style))
    story.append(Paragraph(memo.risk_analysis, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

if generate_button:
    with st.spinner("Searching latest data & Generating Professional Memo..."):
        vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        )
        
        retriever = get_retriever(vectorstore)
        memo_generator = create_rag_chain(retriever)
        
        query = f"""Generate detailed investment memo for a {property_type} of {size} sq ft 
        in {location} priced at ₹{price} lakhs with expected monthly rent of ₹{expected_rent} 
        for {purpose} purpose."""
        
        response = memo_generator.invoke(query)
        
        calculator = RealEstateFinancialCalculator(price_lakhs=price, size_sqft=size, expected_monthly_rent=expected_rent)
        financials = calculator.get_summary(expected_rent)

        st.success("✅ Professional Investment Memo Generated!")

        col1, col2 = st.columns([7, 3])
        
        with col1:
            st.subheader("Executive Summary")
            st.write(response.executive_summary)
            
            st.subheader("Financial Analysis")
            st.write(f"**Price per sq ft**: ₹{financials['price_per_sqft']}")
            st.write(f"**Cap Rate**: {financials['cap_rate']}%")
            st.write(f"**Projected 5-Year ROI**: {financials['projected_5yr_roi']}%")

        with col2:
            st.metric("Recommendation", response.investment_recommendation)
            st.metric("Confidence", f"{response.confidence_score}%")

        st.divider()

        # Download Section
        st.subheader("📥 Download Report")
        
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            st.download_button("📄 Download as PDF", 
                             create_pdf(response, financials, location, property_type, price, size, expected_rent).getvalue(),
                             file_name=f"Investment_Memo_{location.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                             mime="application/pdf")

        with col_d2:
            st.download_button("📝 Download as Markdown", 
                             f"# Investment Memo - {location}\n\n{response.executive_summary}", 
                             file_name=f"Investment_Memo_{location.replace(' ', '_')}.md",
                             mime="text/markdown")

        with col_d3:
            st.download_button("💾 Download as JSON", 
                             json.dumps(response.model_dump(), indent=2), 
                             file_name=f"Investment_Memo_{location.replace(' ', '_')}.json",
                             mime="application/json")