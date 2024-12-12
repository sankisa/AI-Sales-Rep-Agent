import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import  TavilySearchResults
from io import StringIO
import PyPDF2
from docx import Document
import mimetypes

# Model and Agent tools
llm = ChatGroq(api_key=st.secrets["GROQ_API_KEY"])
parser = StrOutputParser()
search = TavilySearchResults(max_results=2)

# Function to parse text from PDF
def parse_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to parse text from DOCX
def parse_docx(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Function to parse a TXT file
def parse_txt(file):
    return file.read().decode("utf-8")

# Page Header
st.set_page_config(
    page_title="Sales Assistant Agent",
    page_icon="🤖",                                           
    initial_sidebar_state="expanded"   
)
st.sidebar.title("Sales Assistant Agent")
st.sidebar.markdown("Assistant Agent Powered by Groq & Tavily.")
# Add a section for experimentation
st.sidebar.subheader("Experimentation Settings")

# Input fields for LLM parameters
temperature = st.sidebar.slider(
    "Set LLM Temperature (0.0 for focused, 1.0 for creative):", 
    min_value=0.0, max_value=1.0, value=0.7, step=0.1
)
max_tokens = st.sidebar.slider(
    "Set Max Tokens (limit output length):", 
    min_value=50, max_value=1500, value=500, step=50
)

# Create a form container
with st.form("company_info", clear_on_submit=True):
    st.title("Insights Retrieval Form")
    product_name = st.text_input("Product Name: ")
    company_url = st.text_input("Company URL: ")
    targeted_company_name = st.text_input("Targeted Company Name: ")
    competitor_url = st.text_input("Competitor URL: ")
    product_category = st.text_input("Product Category: ")
    value_proposition = st.text_input("Value Proposition: ")
    targeted_customer = st.text_input("Targeted Customer: ")
    uploaded_file = st.file_uploader("Upload Product Overview (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    
   
    if uploaded_file is not None:
      # Handle file upload with mimetypes
        file_type, _ = mimetypes.guess_type(uploaded_file.name)

        text = ""
        if file_type == "application/pdf":
          text = parse_pdf(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
          text = parse_docx(uploaded_file)
        elif file_type == "text/plain":
          text = parse_txt(uploaded_file)

    #Display uploaded file text
        st.write(text)
    else:
        st.warning("No file uploaded yet.")  # Optional: Give feedback if no file is uploaded  
    
    # For the llm insights result
    company_insights = ""
    sales_pitch = ""
    
    # Add submit button to the form
    submit_button = st.form_submit_button("Generate Insights")
    # Handle submission
    if submit_button:

    # Perform a search using TavilySearchResults with user's query
        if product_name and company_url:
          #try:
            st.spinner("Getting related search results....")
            #search internet
            company_info = search.invoke(company_url)
            competitor_info = search.invoke(competitor_url)
            if not company_info or not competitor_info:
              st.warning("No data found for the given URLs. Please verify the URLs and try again")
          #except Exception as e:
            st.error(f"Failed to retireve search results: ")

        print(company_info)
        print(competitor_info)

        prompt = """ 
      You are a skilled business strategy analyst and market analyst, specializing in creating impactful proposals that drive sales. 
      Your task is to analyze the provided company and competitor information to craft a compelling and actionable business 
      document that effectively sells our product to the targeted company. Focus on aligning our product's unique value proposition
       with the target company's strategic objectives and market needs.

Key Deliverables:

Market Positioning: Compare how each company positions itself in the market. Highlight their unique value propositions, 
target audiences, and branding strategies.

Strengths and Weaknesses: Identify the primary strengths and weaknesses of both companies in terms of product offerings,
 innovation, customer engagement, and overall business operations

Company Strategy: Identify the company's strategic goals, current priorities, and potential areas for collaboration 
based on the provided data.

Competitor Analysis: Compare the company with its competitors, highlighting opportunities for differentiation. 
Emphasize where our product provides a competitive advantage.

Leadership Insights: Identify key decision-makers within the company, their roles, and potential interests related to our product's 
value proposition.

Competitive Edge: Highlight what gives each company an advantage in the market and where they may fall short compared to the other.

Product Fit and Strategy: Articulate how our product addresses the company's specific challenges, enhances its market position, and aligns with its strategic vision. Highlight key features that make our product the ideal solution.

Opportunities for Growth: Suggest areas where the Target Company can improve to outperform its competitor.
 
Draft a **Sales Pitch Letter** with the following structure:
   - A personalized salutation: Start with "Dear [Team/Decision-Maker at Targeted Company Nmae]" 
   - A clear introduction: Highlight our product's relevance to the target company's strategic goals.
   - Value proposition and key benefits: Summarize how the product aligns with the company's needs.
   - Call to action: Include a persuasive statement encouraging immediate action, such as scheduling a demo or arranging a meeting.
   - A polite closing: End the letter with "Best regards,"
   Insert a horizontal line or separator (e.g., `---`) between each section of the response

   References: Provide credible data points, links to articles, press releases, or industry trends to substantiate your insights and recommendations.
include some Key points to sell products to the targeted company

Additional Context:
Where relevant, incorporate financial data, recent market trends, and notable company or industry initiatives that demonstrate the urgency and necessity of adopting our product. Focus on creating a compelling business case that drives swift decision-making.
Share insights: Identify share market value for each year between 2020-2024 for both the companies and organize in a table
 
   
Ensure the tone is professional yet engaging, targeting senior decision-makers.

Inputs:

Company Data: {company_info}
Competitor Info: {competitor_info}
Product Name: {product_name}
Product Category: {product_category}
Value Proposition: {value_proposition}
Targeted Customer: {targeted_customer}
Targeted Company Name: {targeted_company_name}

"""

      # Prompt Template
        prompt_template = ChatPromptTemplate([("system", prompt)])
      # Chain
        chain = prompt_template | llm | parser

      # Result/Insights
   
        company_insights = chain.invoke(
          {
            "company_info": company_info, 
            "product_name": product_name, 
            "competitor_info": competitor_info,
            "product_category": product_category,
            "value_proposition": value_proposition,
            "targeted_customer": targeted_customer,
            "targeted_company_name": targeted_company_name

            
            })
    
 

    # Display results

st.markdown(company_insights)


