import pandas as pd
import numpy as np
from typing import Dict, List, Any

class DataProcessor:
    """Advanced data processing and analysis utilities"""
    
    def __init__(self):
        pass
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive data summary"""
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'numeric_columns': len(df.select_dtypes(include=['number']).columns),
            'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
            'datetime_columns': len(df.select_dtypes(include=['datetime64']).columns)
        }
        
        return summary
    
    def generate_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data quality assessment report"""
        quality_metrics = {}
        
        # Missing data percentage
        missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        quality_metrics['missing_data_percentage'] = f"{missing_percentage:.2f}%"
        
        # Duplicate rows
        duplicate_count = df.duplicated().sum()
        quality_metrics['duplicate_rows'] = duplicate_count
        
        # Data completeness by column
        completeness = ((df.count() / len(df)) * 100).round(2)
        lowest_completeness = completeness.min()
        quality_metrics['lowest_column_completeness'] = f"{lowest_completeness:.2f}%"
        
        # Unique values ratio for categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            uniqueness_ratios = []
            for col in categorical_cols:
                ratio = (df[col].nunique() / len(df)) * 100
                uniqueness_ratios.append(ratio)
            
            avg_uniqueness = np.mean(uniqueness_ratios)
            quality_metrics['avg_categorical_uniqueness'] = f"{avg_uniqueness:.2f}%"
        else:
            quality_metrics['avg_categorical_uniqueness'] = "N/A"
        
        # Outliers in numeric columns (using IQR method)
        numeric_cols = df.select_dtypes(include=['number']).columns
        total_outliers = 0
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            total_outliers += len(outliers)
        
        quality_metrics['potential_outliers'] = total_outliers
        
        return quality_metrics
    
    def detect_data_types(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Detect and categorize column data types"""
        type_categories = {
            'numeric': [],
            'categorical': [],
            'datetime': [],
            'boolean': [],
            'text': [],
            'mixed': []
        }
        
        for col in df.columns:
            col_data = df[col].dropna()
            
            if pd.api.types.is_numeric_dtype(col_data):
                type_categories['numeric'].append(col)
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                type_categories['datetime'].append(col)
            elif pd.api.types.is_bool_dtype(col_data):
                type_categories['boolean'].append(col)
            elif col_data.dtype == 'object':
                # Try to determine if it's categorical or text
                unique_ratio = col_data.nunique() / len(col_data)
                avg_length = col_data.astype(str).str.len().mean()
                
                if unique_ratio < 0.1 and avg_length < 50:  # Likely categorical
                    type_categories['categorical'].append(col)
                elif avg_length > 100:  # Likely text
                    type_categories['text'].append(col)
                else:
                    type_categories['mixed'].append(col)
            else:
                type_categories['mixed'].append(col)
        
        return type_categories
    
    def generate_column_profiles(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Generate detailed profiles for each column"""
        profiles = {}
        
        for col in df.columns:
            col_data = df[col]
            profile = {
                'name': col,
                'dtype': str(col_data.dtype),
                'count': col_data.count(),
                'null_count': col_data.isnull().sum(),
                'null_percentage': (col_data.isnull().sum() / len(df)) * 100,
                'unique_count': col_data.nunique(),
                'unique_percentage': (col_data.nunique() / len(df)) * 100
            }
            
            if pd.api.types.is_numeric_dtype(col_data):
                # Numeric column statistics
                profile.update({
                    'mean': col_data.mean(),
                    'std': col_data.std(),
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'median': col_data.median(),
                    'q25': col_data.quantile(0.25),
                    'q75': col_data.quantile(0.75)
                })
                
                # Detect potential outliers
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                profile['outlier_count'] = len(outliers)
                
            elif col_data.dtype == 'object':
                # Text/categorical column statistics
                profile.update({
                    'most_frequent': col_data.mode().iloc[0] if len(col_data.mode()) > 0 else None,
                    'most_frequent_count': col_data.value_counts().iloc[0] if len(col_data.value_counts()) > 0 else 0
                })
                
                # String length statistics for text columns
                if col_data.dropna().astype(str).str.len().mean() > 10:
                    str_lengths = col_data.dropna().astype(str).str.len()
                    profile.update({
                        'avg_length': str_lengths.mean(),
                        'min_length': str_lengths.min(),
                        'max_length': str_lengths.max()
                    })
            
            profiles[col] = profile
        
        return profiles
    
    def suggest_visualizations(self, df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """Suggest appropriate visualizations based on data types and characteristics"""
        suggestions = {
            'recommended': [],
            'optional': []
        }
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Recommended visualizations
        if len(numeric_cols) >= 2:
            suggestions['recommended'].append({
                'type': 'scatter_plot',
                'title': 'Scatter Plot - Numeric Relationships',
                'description': 'Explore relationships between numeric variables',
                'columns_needed': 2,
                'column_types': ['numeric', 'numeric']
            })
            
            suggestions['recommended'].append({
                'type': 'correlation_heatmap',
                'title': 'Correlation Heatmap',
                'description': 'Show correlations between all numeric variables',
                'columns_needed': len(numeric_cols),
                'column_types': ['numeric']
            })
        
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            suggestions['recommended'].append({
                'type': 'bar_chart',
                'title': 'Bar Chart - Category Analysis',
                'description': 'Compare numeric values across categories',
                'columns_needed': 2,
                'column_types': ['categorical', 'numeric']
            })
            
            suggestions['recommended'].append({
                'type': 'box_plot',
                'title': 'Box Plot - Distribution by Category',
                'description': 'Show distribution of numeric values by category',
                'columns_needed': 2,
                'column_types': ['categorical', 'numeric']
            })
        
        if len(numeric_cols) > 0:
            suggestions['recommended'].append({
                'type': 'histogram',
                'title': 'Histogram - Distribution Analysis',
                'description': 'Show distribution of numeric variables',
                'columns_needed': 1,
                'column_types': ['numeric']
            })
        
        # Optional visualizations
        if len(categorical_cols) > 0:
            suggestions['optional'].append({
                'type': 'pie_chart',
                'title': 'Pie Chart - Category Proportions',
                'description': 'Show proportions of categorical variables',
                'columns_needed': 1,
                'column_types': ['categorical']
            })
        
        if len(numeric_cols) >= 3:
            suggestions['optional'].append({
                'type': '3d_scatter',
                'title': '3D Scatter Plot',
                'description': 'Explore relationships between three numeric variables',
                'columns_needed': 3,
                'column_types': ['numeric', 'numeric', 'numeric']
            })
        
        return suggestions
    
    def clean_data(self, df: pd.DataFrame, cleaning_options: Dict[str, bool] = None) -> pd.DataFrame:
        """Clean data based on specified options"""
        if cleaning_options is None:
            cleaning_options = {
                'remove_duplicates': True,
                'fill_numeric_missing': False,
                'fill_categorical_missing': False,
                'remove_outliers': False
            }
        
        cleaned_df = df.copy()
        
        # Remove duplicates
        if cleaning_options.get('remove_duplicates', False):
            initial_rows = len(cleaned_df)
            cleaned_df = cleaned_df.drop_duplicates()
            rows_removed = initial_rows - len(cleaned_df)
            if rows_removed > 0:
                print(f"Removed {rows_removed} duplicate rows")
        
        # Fill missing values in numeric columns
        if cleaning_options.get('fill_numeric_missing', False):
            numeric_cols = cleaned_df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                if cleaned_df[col].isnull().any():
                    median_value = cleaned_df[col].median()
                    cleaned_df[col].fillna(median_value, inplace=True)
        
        # Fill missing values in categorical columns
        if cleaning_options.get('fill_categorical_missing', False):
            categorical_cols = cleaned_df.select_dtypes(include=['object', 'category']).columns
            for col in categorical_cols:
                if cleaned_df[col].isnull().any():
                    mode_value = cleaned_df[col].mode().iloc[0] if len(cleaned_df[col].mode()) > 0 else 'Unknown'
                    cleaned_df[col].fillna(mode_value, inplace=True)
        
        return cleaned_df
