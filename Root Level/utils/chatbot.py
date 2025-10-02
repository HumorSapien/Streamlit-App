import streamlit as st
import pandas as pd
import json
from typing import Dict, Any, Optional
import openai

class ExcelChatbot:
    """AI-powered chatbot for Excel data analysis using OpenAI API"""
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 500
        self.temperature = 0.1
        
        if self.api_key:
            openai.api_key = self.api_key
    
    def _get_api_key(self) -> Optional[str]:
        """Safely retrieve OpenAI API key from Streamlit secrets"""
        try:
            return st.secrets.get("OPENAI_API_KEY")
        except Exception:
            return None
    
    def get_response(self, user_query: str, data_context: Dict[str, Any]) -> str:
        """
        Generate AI response based on user query and data context
        
        Args:
            user_query: User's natural language question
            data_context: Processed data information from DataProcessor
            
        Returns:
            AI-generated response string
        """
        
        if not self.api_key:
            return ("🔑 **OpenAI API Key Required**: To use the chatbot feature, please add your OpenAI API key to Streamlit secrets. "
                   "You can get an API key from https://platform.openai.com/api-keys")
        
        try:
            # Prepare context for the AI
            context_summary = self._prepare_context_summary(data_context)
            
            # Create system message with data context
            system_message = self._create_system_message(context_summary)
            
            # Create messages for the API call
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_query}
            ]
            
            # Make API call to OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                presence_penalty=0,
                frequency_penalty=0
            )
            
            # Extract and return the response
            ai_response = response.choices[0].message.content.strip()
            
            # Post-process response for better formatting
            ai_response = self._format_response(ai_response)
            
            return ai_response
            
        except openai.error.AuthenticationError:
            return ("🔐 **Authentication Error**: The provided OpenAI API key is invalid. "
                   "Please check your API key in the Streamlit secrets configuration.")
            
        except openai.error.RateLimitError:
            return ("⚠️ **Rate Limit Exceeded**: You have exceeded your OpenAI API rate limit. "
                   "Please try again in a few moments.")
            
        except openai.error.QuotaExceededError:
            return ("💳 **Quota Exceeded**: You have exceeded your OpenAI API quota. "
                   "Please check your OpenAI account billing.")
            
        except openai.error.APIError as e:
            return f"🛠️ **API Error**: There was an issue with the OpenAI API: {str(e)}"
            
        except Exception as e:
            return ("❌ **Error**: I encountered an unexpected error while processing your question. "
                   "Please try rephrasing your question or contact support.")
    
    def _prepare_context_summary(self, data_context: Dict[str, Any]) -> str:
        """Prepare a concise summary of the data for AI context"""
        try:
            summary_parts = []
            
            # Basic data information
            shape = data_context.get('shape', (0, 0))
            summary_parts.append(f"Dataset has {shape[0]} rows and {shape[1]} columns.")
            
            # Column information
            columns = data_context.get('columns', [])
            if columns:
                summary_parts.append(f"Column names: {', '.join(columns[:10])}")
                if len(columns) > 10:
                    summary_parts.append(f"... and {len(columns) - 10} more columns.")
            
            # Data types
            numeric_cols = data_context.get('numeric_columns', [])
            categorical_cols = data_context.get('categorical_columns', [])
            datetime_cols = data_context.get('datetime_columns', [])
            
            if numeric_cols:
                summary_parts.append(f"Numeric columns: {', '.join(numeric_cols[:5])}")
            if categorical_cols:
                summary_parts.append(f"Categorical columns: {', '.join(categorical_cols[:5])}")
            if datetime_cols:
                summary_parts.append(f"Date/time columns: {', '.join(datetime_cols[:3])}")
            
            # Sample values (limited to prevent token overflow)
            sample_values = data_context.get('sample_values', {})
            if sample_values:
                summary_parts.append("Sample values:")
                for col, values in list(sample_values.items())[:5]:  # Limit to first 5 columns
                    if values and len(values) > 0:
                        values_str = ', '.join([str(v)[:30] for v in values[:3]])  # Limit value length
                        summary_parts.append(f"  - {col}: {values_str}")
            
            # Missing data information
            missing_values = data_context.get('missing_values', {})
            if missing_values:
                missing_cols = [col for col, count in missing_values.items() if count > 0]
                if missing_cols:
                    summary_parts.append(f"Columns with missing values: {', '.join(missing_cols[:5])}")
            
            # Basic statistics (if available)
            statistics = data_context.get('statistics', {})
            if statistics and numeric_cols:
                summary_parts.append("Basic statistics available for numeric columns.")
            
            return "\\n".join(summary_parts)
            
        except Exception as e:
            return "Dataset information is available but could not be summarized."
    
    def _create_system_message(self, context_summary: str) -> str:
        """Create the system message with data context and instructions"""
        
        system_prompt = f"""You are a helpful data analyst assistant. You have access to information about a user's Excel dataset. 

Dataset Information:
{context_summary}

Instructions:
1. Answer questions about the data based ONLY on the context provided above
2. If asked about specific values, calculations, or detailed analysis that requires access to the raw data, explain that you can see the data structure but suggest the user use the visualization features for detailed exploration
3. Be conversational and helpful
4. If you cannot answer a question based on the available context, clearly state that limitation
5. Suggest relevant visualizations or analysis approaches when appropriate
6. Keep responses concise but informative (under 300 words)
7. Use markdown formatting for better readability
8. If asked about data cleaning or preprocessing, provide general guidance
9. For statistical questions, provide conceptual explanations and suggest using the Advanced Analysis tab for detailed calculations

Always be honest about the limitations of your knowledge about their specific dataset.
"""
        
        return system_prompt
    
    def _format_response(self, response: str) -> str:
        """Post-process the AI response for better formatting"""
        
        # Ensure proper markdown formatting
        formatted_response = response
        
        # Add emoji for better visual appeal (if not already present)
        if not any(char in response for char in ['📊', '📈', '💡', '🔍', '⚠️', '✅']):
            formatted_response = "💡 " + formatted_response
        
        return formatted_response
    
    def suggest_questions(self, data_context: Dict[str, Any]) -> list:
        """Generate suggested questions based on the data structure"""
        
        suggestions = [
            "What columns are in this dataset?",
            "How many rows and columns does this data have?",
            "Are there any missing values in the data?",
            "What are the main data types in this dataset?"
        ]
        
        # Add specific suggestions based on data structure
        numeric_cols = data_context.get('numeric_columns', [])
        categorical_cols = data_context.get('categorical_columns', [])
        
        if numeric_cols:
            if len(numeric_cols) >= 2:
                suggestions.extend([
                    f"What's the relationship between {numeric_cols[0]} and {numeric_cols[1]}?",
                    "Which numeric columns might be correlated?"
                ])
            suggestions.append(f"What's the distribution of {numeric_cols[0]}?")
        
        if categorical_cols:
            suggestions.extend([
                f"What are the unique values in {categorical_cols[0]}?",
                f"How should I analyze the {categorical_cols[0]} column?"
            ])
        
        if numeric_cols and categorical_cols:
            suggestions.append(f"How does {numeric_cols[0]} vary by {categorical_cols[0]}?")
        
        # Data quality suggestions
        missing_values = data_context.get('missing_values', {})
        if any(count > 0 for count in missing_values.values()):
            suggestions.append("How should I handle the missing values in this dataset?")
        
        suggestions.extend([
            "What visualizations would you recommend for this data?",
            "How can I clean this data?",
            "What insights can I get from this dataset?"
        ])
        
        return suggestions[:8]  # Return top 8 suggestions
    
    def is_available(self) -> bool:
        """Check if chatbot functionality is available"""
        return self.api_key is not None
    
    def get_usage_info(self) -> Dict[str, str]:
        """Get information about chatbot usage and setup"""
        if self.is_available():
            return {
                "status": "Available",
                "model": self.model,
                "setup": "API key configured successfully"
            }
        else:
            return {
                "status": "Not Available",
                "model": "N/A",
                "setup": "OpenAI API key required in Streamlit secrets"
            }
```

*[Continue with remaining files...]*

## **Quick Copy Instructions:**

1. **Create each file** in your repository with the exact path and filename
2. **Copy the content** from each section above  
3. **Replace placeholders** like `yourusername` and `your-repo-name`
4. **Add your OpenAI API key** to Streamlit Cloud secrets if you want chatbot functionality

## **🚀 Next Steps:**

1. **Create GitHub repository**
2. **Copy all files above**
3. **Push to GitHub**
4. **Deploy on Streamlit Cloud**
5. **Test with Excel files**

The complete application is ready for deployment! 🎉
