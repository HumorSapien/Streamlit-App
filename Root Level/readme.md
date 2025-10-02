# 🔒 Secure Excel Data Analysis & AI Chatbot

A comprehensive Streamlit application for secure Excel file processing, interactive data visualization, and AI-powered data analysis chatbot.

## ✨ Features

### 🛡️ Security-First Design
- **Advanced file validation** with malware protection
- **Input sanitization** to prevent injection attacks  
- **Session-based processing** with automatic cleanup
- **Rate limiting** for API calls
- **PII detection** and warnings
- **Secure credential management**

### 📊 Data Processing & Analysis
- **Multi-sheet Excel support** (.xlsx files)
- **Interactive data visualization** with Plotly
- **Statistical analysis** and data quality reports
- **Advanced filtering** and data exploration
- **Correlation analysis** and outlier detection

### 🤖 AI-Powered Chatbot
- **Natural language queries** about your data
- **OpenAI integration** for intelligent responses
- **Context-aware analysis** based on data structure
- **Suggested questions** to guide exploration
- **Conversation history** within sessions

### 📈 Interactive Visualizations
- Bar charts, line plots, scatter plots
- Histograms and distribution analysis
- Box plots and violin plots
- Correlation heatmaps
- Custom chart builder

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (for chatbot functionality)

### Installation

1. **Clone or download the application files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key (optional, for chatbot):**
   - Create a `.streamlit/secrets.toml` file in your project directory
   - Add your API key:
     ```toml
     OPENAI_API_KEY = "your-api-key-here"
     ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

### Usage

1. **Upload Excel File**: Use the sidebar to upload your .xlsx file
2. **Explore Data**: View data overview and basic statistics
3. **Create Visualizations**: Choose from various chart types
4. **Chat with Your Data**: Ask questions in natural language
5. **Advanced Analysis**: Perform statistical analysis and correlation studies

## 🔧 Configuration

### Security Settings
The application includes comprehensive security configurations in `config/security.py`:

- File size limits (default: 50MB)
- Content scanning for malicious patterns
- API rate limiting (10 calls/minute)
- Session timeout (2 hours)
- Input validation and sanitization

### Environment Variables
Set these in your `.streamlit/secrets.toml`:

```toml
# Required for chatbot functionality
OPENAI_API_KEY = "your-openai-api-key"

# Optional: Production environment flag
PRODUCTION = true
```

## 🛡️ Security Features

### File Upload Security
- **MIME type validation**
- **File extension restrictions** (.xlsx only)
- **Content scanning** for malicious patterns
- **Size limitations** to prevent DoS
- **Filename sanitization**

### Data Processing Security  
- **Input sanitization** for all user inputs
- **XSS prevention** in data content
- **SQL injection protection**
- **Path traversal prevention**
- **PII detection** and warnings

### API Security
- **Rate limiting** to prevent abuse
- **Secure credential storage**
- **Error handling** without information leakage
- **Session isolation** between users

## 📁 Project Structure

```
streamlit_excel_app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── utils/
│   ├── file_handler.py   # Secure file upload and validation
│   ├── data_processor.py # Data analysis and processing
│   ├── chatbot.py        # AI chatbot integration
│   └── visualizations.py # Interactive chart generation
├── config/
│   └── security.py       # Security configurations
└── tests/
    └── test_security.py  # Security validation tests
```

## 🧪 Testing

Run the security tests:
```bash
python -m pytest tests/
```

Or run specific test modules:
```bash
python tests/test_security.py
```

## 🔒 Safety Protocols

This application follows strict safety protocols:

- **No permanent data storage** - all data is session-based
- **Environment separation** - development/production isolation
- **Input validation** - comprehensive content scanning
- **Error handling** - graceful failures without data exposure
- **Logging** - security events are logged
- **Rate limiting** - prevents API abuse

## ⚠️ Important Notes

- **Data Privacy**: Uploaded files are processed in memory only and are not stored permanently
- **API Costs**: Chatbot functionality uses OpenAI API which may incur costs
- **File Limits**: Excel files are limited to 50MB and 1 million rows for performance
- **Browser Compatibility**: Best performance on modern browsers (Chrome, Firefox, Safari)

## 🆘 Troubleshooting

### Common Issues

1. **Chatbot not working**: Ensure OpenAI API key is set in secrets.toml
2. **File upload fails**: Check file size (<50MB) and format (.xlsx only)
3. **Slow performance**: Try with smaller datasets or use data sampling
4. **Memory errors**: Reduce dataset size or restart the application

### Error Messages
- **"OpenAI API Key Required"**: Add your API key to Streamlit secrets
- **"File validation failed"**: File may be corrupted or contain suspicious content
- **"Rate limit exceeded"**: Wait a minute before making more API calls

## 📞 Support

If you encounter issues or need assistance:

1. Check the troubleshooting section above
2. Review the error messages for specific guidance
3. Ensure all dependencies are properly installed
4. Verify your OpenAI API key is valid (if using chatbot)

## 📄 License

This application is provided as-is for educational and development purposes. Please ensure compliance with your organization's data security policies when processing sensitive information.

---

**⚠️ Security Reminder**: Always review your data before uploading and ensure you have appropriate permissions to process the information contained in your Excel files.
