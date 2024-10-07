import os
from dotenv import load_dotenv
import streamlit as st
from datetime import date
from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from stock_api.utils import retrieve_from_endpoint
from langchain_core.tools import tool
# from stock_api.api import get_top_companies_by_tx_volume, get_company_overview, get_daily_tx, get_performance_since_ipo
# from langchain_core.tools import Tool

@tool
def get_top_companies_by_tx_volume(start_date: str, end_date: str, top_n: int = 5) -> str:
    """Get top companies by transaction volume"""
    url = f"https://api.sectors.app/v1/most-traded/?start={start_date}&end={end_date}&n_stock={top_n}"
    return retrieve_from_endpoint(url, SECTORS_API_KEY)

@tool
def get_company_overview(stock: str) -> str:
    """Get the overview of a stock, including email, address, phone number, market cap information, listing date etc"""
    url = f"https://api.sectors.app/v1/company/report/{stock}/?sections=overview"
    print(url)
    return retrieve_from_endpoint(url, SECTORS_API_KEY)

@tool
def get_daily_tx(stock: str, start_date: str, end_date: str) -> str:
    """Get daily transaction for a stock"""
    url = f"https://api.sectors.app/v1/daily/{stock}/?start={start_date}&end={end_date}"
    print(url)
    return retrieve_from_endpoint(url, SECTORS_API_KEY)

@tool
def get_performance_since_ipo(stock: str) -> str:
    """Get stock performance after IPO listing"""
    url = f"https://api.sectors.app/v1/listing-performance/{stock}/"
    print(url)
    return retrieve_from_endpoint(url, SECTORS_API_KEY)


# Define tools and LLM with descriptions
# tools = [
#     Tool.from_function(get_company_overview, name="get_company_overview", description="Get the overview of a stock, including email, address, phone number, market cap information, listing date etc."),
#     Tool.from_function(get_top_companies_by_tx_volume, name="get_top_companies_by_tx_volume", description="Get the top companies by transaction volume within a specified date range."),
#     StructuredTool.from_function(get_daily_tx, name="get_daily_tx", description="Get daily transaction data for a specified stock over a date range."),
#     Tool.from_function(get_performance_since_ipo, name="get_performance_since_ipo", description="Get the stock performance since its initial public offering (IPO).")
# ]

tools = [
    get_company_overview,
    get_top_companies_by_tx_volume,
    get_daily_tx,
    get_performance_since_ipo
]

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Your keys setup (you can replace this with secure storage methods for deployment)
SECTORS_API_KEY = os.getenv('SECTORS_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

llm = ChatGroq(
    temperature=0,
    model_name="llama3-groq-70b-8192-tool-use-preview",
    groq_api_key=GROQ_API_KEY,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""
            You are the financial robo-advisor, answer the following queries like a Financial Agent,
            being as factual and analytical as possible. Do not make up stuff.
            Try to cite your number as much as possible. Retrieve and show the corresponding data first
            such as the market cap number or data that correspond to the question before you make conclusion and show the answer.
            Your get_daily_tx tool will need the start and end dates, and if you need the start and end dates
            and they are not explicitly provided by the user, please infer a keyword from the query such.
            If the volume was about a single day (such as specific single date or yesterday),
            the start date and end date parameter should be the same date. Start and end date will be in the format YYYY-MM-DD.
            Whenever you return a list of names, return also the corresponding values for each name.

            For most of your queries such as company performance since the date of its initial public offering (IPO),
            these information should be available in your get_performance_since_ipo tool,
            but the listing performance data is accessible only for stocks listed after May 2005.
            Note that the endpoint for performance since IPO has only one required parameter, which is the stock.
            Every time you return the symbol of the stock, result also the number in question in a nice tabular format.

            Today's date is {date.today().strftime("%Y-%m-%d")}.
            """
        ),
        ("human", "{input}"),
        # msg containing previous agent tool invocations and corresponding tool outputs
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Header section with creative introduction
st.title("🤖 IDX Financial Robo-Advisor")
st.subheader("Analyze Indonesian Stock Market with Cutting-Edge Generative AI")
st.write("""
Welcome to your personalized financial advisor for the Indonesian Stock Exchange!<br>
<span style="color:gray;">
Powered by LLM `llama3-groq-70b-8192-tool-use-preview` and <strong>real-time data</strong> from 
<img src="https://sectors.app/app_assets/sectors_logo.svg" alt="Sectors.app Logo" width="20" style="vertical-align: middle;"> 
<strong>Sectors.app</strong>, our system helps you make informed investment decisions. Input your own custom query, and let the AI generate in-depth insights 
on stock trends, transactions, and market performance. Explore the power of financial analysis with just a few clicks!
</span>
""", unsafe_allow_html=True)


# Sidebar for input
query = st.text_area('Ask your financial query here:', placeholder="Example: What is the performance of GOTO since its IPO listing?")

if st.button('Submit'):
    if query.strip():  # Ensure the user entered a query
        with st.spinner("Generating insights..."):
            # Execute user query with generative AI
            result = agent_executor.invoke({"input": query})
            st.success("Query Executed Successfully!")

            # Display results
            st.write("## Financial Insights")
            st.write(result["output"])
    else:
        st.error("Please enter a query to proceed!")

# Add a visual element: Demo video of the application
st.write("---")
st.write("### 🎥 Demo of the IDX Financial Robo-Advisor")
st.video('https://youtu.be/TErKMU-PbL8') 

# Additional creative section: Summary of AI's capabilities
st.write("---")
st.subheader("Why Use This Robo-Advisor?")
st.write("""
1. **Comprehensive Analysis**: Get stock performance, transaction volume, market cap, and IPO performance in a single query.
2. **Real-Time Data**: Updated instantly, providing accurate market insights.
3. **Informed Decision-Making**: Support your decisions with AI-driven data and financial metrics.
4. **Personalized Insights**: Tailor your queries based on specific companies, date ranges, or stock performance metrics.
""")

# Footer section
st.write("### Built with 💻 by leveraging AI for smarter financial decision making.")
