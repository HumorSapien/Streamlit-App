import streamlit as st
import hashlib
import re
import time
from typing import Dict, Any, Optional, List
import pandas as pd
import logging
from dataclasses import dataclass

@dataclass
class SecurityLimits:
    """Security limits and constants"""
    MAX_FILE_SIZE_MB: int = 50
    MAX_CELL_SIZE_CHARS: int = 10000
    MAX_COLUMNS: int = 1000
    MAX_ROWS: int = 1000000
    MAX_API_CALLS_PER_MINUTE: int = 10
    SESSION_TIMEOUT_HOURS: int = 2

class SecurityConfig:
    """Centralized security configuration and validation"""

    def __init__(self):
        self.limits = SecurityLimits()
        self.suspicious_patterns = self._load_suspicious_patterns()
        self.api_call_tracker = {}
        self._setup_logging()

    def _setup_logging(self):
        """Setup security logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _load_suspicious_patterns(self) -> List[str]:
        """Load patterns that indicate potentially malicious content"""
        return [
            # XSS patterns
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<form[^>]*>',

            # SQL injection patterns
            r'SELECT\s+.*\s+FROM',
            r'INSERT\s+INTO',
            r'UPDATE\s+.*\s+SET',
            r'DELETE\s+FROM',
            r'DROP\s+TABLE',
            r'DROP\s+DATABASE',
            r'UNION\s+SELECT',
            r'OR\s+1\s*=\s*1',
            r"'\s*OR\s*'.*'\s*=\s*'",

            # Command injection patterns
            r';\s*rm\s+-rf',
            r';\s*cat\s+/etc/',
            r';\s*wget\s+',
            r';\s*curl\s+',
            r'\|\s*nc\s+',
            r'&&\s*rm\s+',

            # Path traversal patterns
            r'\.\./',
            r'\.\.\\',
            r'/etc/passwd',
            r'/etc/shadow',
            r'C:\\Windows',

            # Other suspicious patterns
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'shell_exec\s*\(',
            r'base64_decode\s*\(',
        ]

    def validate_session_security(self) -> Dict[str, Any]:
        """Validate current session security status"""

        validation_result = {
            'secure': True,
            'warnings': [],
            'errors': []
        }

        # Check session state size
        if 'data' in st.session_state and st.session_state.data is not None:
            data_size = st.session_state.data.memory_usage(deep=True).sum()
            if data_size > 100 * 1024 * 1024:  # 100MB threshold
                validation_result['warnings'].append(
                    "Large dataset in session. Consider processing in smaller chunks."
                )

        # Check for session timeout
        if 'session_start' not in st.session_state:
            st.session_state.session_start = time.time()
        else:
            session_duration = time.time() - st.session_state.session_start
            if session_duration > self.limits.SESSION_TIMEOUT_HOURS * 3600:
                validation_result['warnings'].append(
                    "Session has been active for a long time. Consider refreshing for security."
                )

        return validation_result

    def validate_data_content(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive data content validation"""

        validation_result = {
            'safe': True,
            'warnings': [],
            'errors': [],
            'suspicious_columns': []
        }

        try:
            # Check data size limits
            if len(df) > self.limits.MAX_ROWS:
                validation_result['errors'].append(
                    f"Dataset has {len(df)} rows, exceeding limit of {self.limits.MAX_ROWS}"
                )
                validation_result['safe'] = False

            if len(df.columns) > self.limits.MAX_COLUMNS:
                validation_result['errors'].append(
                    f"Dataset has {len(df.columns)} columns, exceeding limit of {self.limits.MAX_COLUMNS}"
                )
                validation_result['safe'] = False

            # Check for suspicious content in string columns
            string_columns = df.select_dtypes(include=['object']).columns

            for col in string_columns:
                if self._scan_column_for_threats(df[col]):
                    validation_result['suspicious_columns'].append(col)
                    validation_result['warnings'].append(
                        f"Column '{col}' contains potentially suspicious content"
                    )

            # Check cell sizes
            for col in string_columns:
                max_cell_size = df[col].dropna().astype(str).str.len().max()
                if max_cell_size > self.limits.MAX_CELL_SIZE_CHARS:
                    validation_result['warnings'].append(
                        f"Column '{col}' contains very large cells (max: {max_cell_size} characters)"
                    )

            # Check for potential PII (basic patterns)
            pii_warnings = self._check_for_pii(df)
            if pii_warnings:
                validation_result['warnings'].extend(pii_warnings)

            self.logger.info(f"Data validation completed. Safe: {validation_result['safe']}, "
                           f"Warnings: {len(validation_result['warnings'])}")

            return validation_result

        except Exception as e:
            validation_result['safe'] = False
            validation_result['errors'].append(f"Validation error: {str(e)}")
            self.logger.error(f"Data validation failed: {str(e)}")
            return validation_result

    def _scan_column_for_threats(self, column: pd.Series) -> bool:
        """Scan a column for suspicious patterns"""

        try:
            # Convert to string and check against patterns
            column_str = column.dropna().astype(str)

            for pattern in self.suspicious_patterns:
                if column_str.str.contains(pattern, case=False, regex=True, na=False).any():
                    self.logger.warning(f"Suspicious pattern detected: {pattern}")
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error scanning column: {str(e)}")
            return True  # Err on the side of caution

    def _check_for_pii(self, df: pd.DataFrame) -> List[str]:
        """Check for potential personally identifiable information"""

        pii_warnings = []

        # Patterns for common PII
        pii_patterns = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }

        string_columns = df.select_dtypes(include=['object']).columns

        for col in string_columns:
            col_data = df[col].dropna().astype(str)

            for pii_type, pattern in pii_patterns.items():
                if col_data.str.contains(pattern, regex=True, na=False).any():
                    pii_warnings.append(
                        f"Column '{col}' may contain {pii_type} information. "
                        f"Please ensure you have permission to process this data."
                    )

        return pii_warnings

    def validate_api_usage(self, user_id: str = "default") -> Dict[str, Any]:
        """Validate API usage limits"""

        current_time = time.time()
        current_minute = int(current_time // 60)

        if user_id not in self.api_call_tracker:
            self.api_call_tracker[user_id] = {}

        user_tracker = self.api_call_tracker[user_id]

        # Clean old entries (older than 1 minute)
        old_minutes = [minute for minute in user_tracker.keys() if minute < current_minute - 1]
        for old_minute in old_minutes:
            del user_tracker[old_minute]

        # Count current minute calls
        current_calls = user_tracker.get(current_minute, 0)

        if current_calls >= self.limits.MAX_API_CALLS_PER_MINUTE:
            return {
                'allowed': False,
                'message': f"API rate limit exceeded. Maximum {self.limits.MAX_API_CALLS_PER_MINUTE} calls per minute.",
                'retry_after': 60 - (current_time % 60)
            }

        # Increment counter
        user_tracker[current_minute] = current_calls + 1

        return {
            'allowed': True,
            'remaining_calls': self.limits.MAX_API_CALLS_PER_MINUTE - (current_calls + 1)
        }

    def sanitize_input(self, input_text: str) -> str:
        """Sanitize user input to prevent injection attacks"""

        if not isinstance(input_text, str):
            input_text = str(input_text)

        # Remove or escape potentially dangerous characters
        sanitized = input_text

        # Remove script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)

        # Remove javascript: and vbscript: URLs
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'vbscript:', '', sanitized, flags=re.IGNORECASE)

        # Remove event handlers
        sanitized = re.sub(r'on\w+\s*=\s*["'][^"']*["']', '', sanitized, flags=re.IGNORECASE)

        # Limit length
        if len(sanitized) > 10000:  # 10KB limit for user input
            sanitized = sanitized[:10000]

        return sanitized.strip()

    def generate_security_report(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """Generate comprehensive security report"""

        report = {
            'timestamp': time.time(),
            'session_security': self.validate_session_security(),
            'system_status': {
                'limits_configured': True,
                'logging_enabled': True,
                'patterns_loaded': len(self.suspicious_patterns)
            }
        }

        if df is not None:
            report['data_security'] = self.validate_data_content(df)

        return report

    def get_security_recommendations(self, df: pd.DataFrame = None) -> List[str]:
        """Get security recommendations based on current state"""

        recommendations = []

        # General recommendations
        recommendations.extend([
            "🔒 Always ensure your OpenAI API key is stored securely in Streamlit secrets",
            "🔄 Regularly clear session data when working with sensitive information",
            "📊 Avoid uploading files containing personal or sensitive information",
            "🛡️ Use HTTPS connections when deploying the application",
            "📝 Review data content before sharing analysis results"
        ])

        # Data-specific recommendations
        if df is not None:
            validation = self.validate_data_content(df)

            if validation['warnings']:
                recommendations.append(
                    "⚠️ Review flagged columns before proceeding with analysis"
                )

            if len(df) > 10000:
                recommendations.append(
                    "📈 Consider sampling large datasets for faster processing"
                )

            string_cols = df.select_dtypes(include=['object']).columns
            if len(string_cols) > 0:
                recommendations.append(
                    "🔍 Be cautious when sharing text columns that may contain sensitive information"
                )

        return recommendations

    @staticmethod
    def is_production_environment() -> bool:
        """Check if running in production environment"""
        try:
            # Check for common production indicators
            return (
                'STREAMLIT_SERVER_PORT' in st.secrets or
                'PRODUCTION' in st.secrets or
                hasattr(st, '_is_running_in_cloud') and st._is_running_in_cloud
            )
        except Exception:
            return False

    def log_security_event(self, event_type: str, details: str, severity: str = "INFO"):
        """Log security-related events"""

        log_message = f"SECURITY {severity}: {event_type} - {details}"

        if severity == "ERROR":
            self.logger.error(log_message)
        elif severity == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
