import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.file_handler import SecureFileHandler
from utils.data_processor import DataProcessor
from utils.chatbot import ExcelChatbot
from utils.visualizations import ChartGenerator
from config.security import SecurityConfig
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Excel Data Analysis & Chatbot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Security initialization
security = SecurityConfig()

def main():
    st.title("🔒 Secure Excel Data Analysis & AI Chatbot")
    st.markdown("Upload Excel files securely and chat with your data using AI")
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    
    # Sidebar for file upload and controls
    with st.sidebar:
        st.header("📂 File Upload")
        
        # Security notice
        st.info("🔐 Your data is processed securely and never stored permanently")
        
        # File upload with security validation
        file_handler = SecureFileHandler()
        uploaded_file = st.file_uploader(
            "Choose an Excel file (.xlsx only)",
            type=['xlsx'],
            accept_multiple_files=False,
            help="Upload Excel files up to 50MB"
        )
        
        if uploaded_file:
            with st.spinner("🔍 Validating and processing file..."):
                validation_result = file_handler.validate_and_process(uploaded_file)
                
                if validation_result['success']:
                    st.session_state.data = validation_result['data']
                    st.session_state.processed_data = validation_result['processed_data']
                    st.success(f"✅ File loaded successfully!")
                    st.info(f"📊 {len(validation_result['data'])} rows × {len(validation_result['data'].columns)} columns")
                else:
                    st.error(f"❌ {validation_result['message']}")
                    st.session_state.data = None
        
        # Clear data button
        if st.button("🗑️ Clear All Data", type="secondary"):
            st.session_state.data = None
            st.session_state.chat_history = []
            st.session_state.processed_data = None
            st.success("Data cleared successfully!")
            st.experimental_rerun()
    
    # Main content area
    if st.session_state.data is not None:
        # Create tabs for different functionalities
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Overview", "📈 Visualizations", "🤖 AI Chat", "🔧 Advanced Analysis"])
        
        # Tab 1: Data Overview
        with tab1:
            show_data_overview()
        
        # Tab 2: Visualizations
        with tab2:
            show_visualizations()
        
        # Tab 3: AI Chatbot
        with tab3:
            show_chatbot()
        
        # Tab 4: Advanced Analysis
        with tab4:
            show_advanced_analysis()
            
    else:
        # Welcome screen when no data is loaded
        st.markdown("""
        ## 🚀 Welcome to Secure Excel Data Analysis & AI Chatbot
        
        ### Features:
        - 🔒 **Secure File Upload**: Advanced validation and malware protection
        - 📊 **Interactive Visualizations**: Dynamic charts with Plotly
        - 🤖 **AI-Powered Chatbot**: Ask questions about your data in natural language
        - 📈 **Advanced Analytics**: Statistical insights and data summaries
        - 🛡️ **Privacy First**: No data stored permanently, session-based processing
        
        ### Security Features:
        - ✅ File type validation and size limits
        - ✅ Content scanning for malicious files  
        - ✅ Session isolation between users
        - ✅ Encrypted API communications
        - ✅ Automatic data cleanup
        
        **👈 Start by uploading an Excel file using the sidebar**
        """)

def show_data_overview():
    """Display data overview and basic statistics"""
    if st.session_state.data is not None:
        data_processor = DataProcessor()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Data Preview")
            st.dataframe(st.session_state.data.head(100), use_container_width=True)
        
        with col2:
            st.subheader("📊 Data Summary")
            summary = data_processor.get_data_summary(st.session_state.data)
            
            st.metric("Total Rows", summary['total_rows'])
            st.metric("Total Columns", summary['total_columns'])
            st.metric("Missing Values", summary['missing_values'])
            
            # Show column types
            st.subheader("📝 Column Information")
            col_info = pd.DataFrame({
                'Column': st.session_state.data.columns,
                'Type': st.session_state.data.dtypes,
                'Non-Null': st.session_state.data.count()
            })
            st.dataframe(col_info, use_container_width=True)

def show_visualizations():
    """Display interactive visualizations"""
    if st.session_state.data is not None:
        chart_generator = ChartGenerator()
        
        st.subheader("📈 Interactive Visualizations")
        
        # Chart type selection
        chart_type = st.selectbox(
            "Select Chart Type",
            ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Box Plot", "Heatmap"]
        )
        
        numeric_columns = st.session_state.data.select_dtypes(include=['number']).columns.tolist()
        categorical_columns = st.session_state.data.select_dtypes(include=['object']).columns.tolist()
        
        if chart_type == "Bar Chart":
            chart_generator.create_bar_chart(st.session_state.data, categorical_columns, numeric_columns)
        elif chart_type == "Line Chart":
            chart_generator.create_line_chart(st.session_state.data, numeric_columns)
        elif chart_type == "Scatter Plot":
            chart_generator.create_scatter_plot(st.session_state.data, numeric_columns)
        elif chart_type == "Histogram":
            chart_generator.create_histogram(st.session_state.data, numeric_columns)
        elif chart_type == "Box Plot":
            chart_generator.create_box_plot(st.session_state.data, categorical_columns, numeric_columns)
        elif chart_type == "Heatmap":
            chart_generator.create_heatmap(st.session_state.data, numeric_columns)

def show_chatbot():
    """Display the AI chatbot interface"""
    if st.session_state.data is not None:
        st.subheader("🤖 Chat with Your Data")
        
        # Initialize chatbot
        try:
            chatbot = ExcelChatbot()
            
            # Chat interface
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
            
            # User input
            if prompt := st.chat_input("Ask a question about your data..."):
                # Add user message to history
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                
                with st.chat_message("user"):
                    st.write(prompt)
                
                # Generate AI response
                with st.chat_message("assistant"):
                    with st.spinner("🤔 Analyzing your data..."):
                        try:
                            response = chatbot.get_response(prompt, st.session_state.processed_data)
                            st.write(response)
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                        except Exception as e:
                            error_msg = "I apologize, but I encountered an error processing your question. Please try rephrasing it."
                            st.write(error_msg)
                            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        
        except Exception as e:
            st.error("Chatbot service is currently unavailable. Please check your OpenAI API configuration.")
            st.info("💡 To enable the chatbot, add your OpenAI API key to the Streamlit secrets.")

def show_advanced_analysis():
    """Display advanced analytical features"""
    if st.session_state.data is not None:
        data_processor = DataProcessor()
        
        st.subheader("🔧 Advanced Data Analysis")
        
        # Statistical analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Descriptive Statistics")
            numeric_data = st.session_state.data.select_dtypes(include=['number'])
            if not numeric_data.empty:
                st.dataframe(numeric_data.describe(), use_container_width=True)
            else:
                st.info("No numeric columns found for statistical analysis")
        
        with col2:
            st.subheader("🔍 Data Quality Report")
            quality_report = data_processor.generate_quality_report(st.session_state.data)
            
            for metric, value in quality_report.items():
                st.metric(metric.replace('_', ' ').title(), value)
        
        # Correlation analysis
        if not numeric_data.empty and len(numeric_data.columns) > 1:
            st.subheader("🔗 Correlation Analysis")
            correlation_matrix = numeric_data.corr()
            
            fig = px.imshow(correlation_matrix, 
                          text_auto=True, 
                          aspect="auto",
                          color_continuous_scale='RdBu_r',
                          title="Correlation Heatmap")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
```
