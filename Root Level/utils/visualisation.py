import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Optional, Dict, Any

class ChartGenerator:
    """Interactive chart generation using Plotly"""

    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
        self.default_height = 500
        self.default_width = None

    def create_bar_chart(self, df: pd.DataFrame, categorical_columns: List[str], numeric_columns: List[str]):
        """Create interactive bar chart"""

        if not categorical_columns or not numeric_columns:
            st.warning("Bar chart requires both categorical and numeric columns.")
            return

        col1, col2 = st.columns(2)

        with col1:
            x_column = st.selectbox("Select X-axis (Category)", categorical_columns, key="bar_x")
        with col2:
            y_column = st.selectbox("Select Y-axis (Values)", numeric_columns, key="bar_y")

        if x_column and y_column:
            # Option to aggregate data
            aggregation = st.selectbox(
                "Aggregation method",
                ["sum", "mean", "count", "median", "max", "min"],
                index=1,  # Default to mean
                key="bar_agg"
            )

            try:
                if aggregation == "count":
                    # Count occurrences
                    chart_data = df.groupby(x_column).size().reset_index(name='count')
                    y_col = 'count'
                else:
                    # Apply aggregation function
                    chart_data = df.groupby(x_column)[y_column].agg(aggregation).reset_index()
                    y_col = y_column

                # Create bar chart
                fig = px.bar(
                    chart_data,
                    x=x_column,
                    y=y_col,
                    title=f"{aggregation.capitalize()} of {y_col} by {x_column}",
                    color=y_col,
                    color_continuous_scale="viridis",
                    height=self.default_height
                )

                fig.update_layout(
                    xaxis_title=x_column,
                    yaxis_title=f"{aggregation.capitalize()} of {y_col}",
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)

                # Show summary statistics
                st.subheader("Summary Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Categories", len(chart_data))
                with col2:
                    st.metric("Max Value", f"{chart_data[y_col].max():.2f}")
                with col3:
                    st.metric("Min Value", f"{chart_data[y_col].min():.2f}")

            except Exception as e:
                st.error(f"Error creating bar chart: {str(e)}")

    def create_line_chart(self, df: pd.DataFrame, numeric_columns: List[str]):
        """Create interactive line chart"""

        if len(numeric_columns) < 2:
            st.warning("Line chart requires at least 2 numeric columns.")
            return

        col1, col2 = st.columns(2)

        with col1:
            x_column = st.selectbox("Select X-axis", numeric_columns, key="line_x")
        with col2:
            y_columns = st.multiselect("Select Y-axis (can select multiple)", 
                                     [col for col in numeric_columns if col != x_column], 
                                     key="line_y")

        if x_column and y_columns:
            try:
                fig = go.Figure()

                for i, y_col in enumerate(y_columns):
                    # Sort data by x-axis for proper line connection
                    sorted_data = df[[x_column, y_col]].dropna().sort_values(x_column)

                    fig.add_trace(go.Scatter(
                        x=sorted_data[x_column],
                        y=sorted_data[y_col],
                        mode='lines+markers',
                        name=y_col,
                        line=dict(color=self.color_palette[i % len(self.color_palette)])
                    ))

                fig.update_layout(
                    title=f"Line Chart: {', '.join(y_columns)} vs {x_column}",
                    xaxis_title=x_column,
                    yaxis_title="Values",
                    height=self.default_height,
                    hovermode='x unified'
                )

                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error creating line chart: {str(e)}")

    def create_scatter_plot(self, df: pd.DataFrame, numeric_columns: List[str]):
        """Create interactive scatter plot"""

        if len(numeric_columns) < 2:
            st.warning("Scatter plot requires at least 2 numeric columns.")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            x_column = st.selectbox("Select X-axis", numeric_columns, key="scatter_x")
        with col2:
            y_column = st.selectbox("Select Y-axis", 
                                  [col for col in numeric_columns if col != x_column], 
                                  key="scatter_y")
        with col3:
            # Option to color by a categorical column
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            color_column = st.selectbox("Color by (optional)", 
                                      ["None"] + categorical_cols, 
                                      key="scatter_color")

        if x_column and y_column:
            try:
                # Create scatter plot
                if color_column and color_column != "None":
                    fig = px.scatter(
                        df,
                        x=x_column,
                        y=y_column,
                        color=color_column,
                        title=f"Scatter Plot: {y_column} vs {x_column} (colored by {color_column})",
                        height=self.default_height,
                        opacity=0.7
                    )
                else:
                    fig = px.scatter(
                        df,
                        x=x_column,
                        y=y_column,
                        title=f"Scatter Plot: {y_column} vs {x_column}",
                        height=self.default_height,
                        opacity=0.7
                    )

                # Add trendline option
                add_trendline = st.checkbox("Add trendline", key="scatter_trend")
                if add_trendline:
                    # Calculate trendline
                    clean_data = df[[x_column, y_column]].dropna()
                    if len(clean_data) > 1:
                        z = np.polyfit(clean_data[x_column], clean_data[y_column], 1)
                        p = np.poly1d(z)

                        fig.add_trace(go.Scatter(
                            x=clean_data[x_column],
                            y=p(clean_data[x_column]),
                            mode='lines',
                            name='Trendline',
                            line=dict(color='red', dash='dash')
                        ))

                fig.update_layout(
                    xaxis_title=x_column,
                    yaxis_title=y_column
                )

                st.plotly_chart(fig, use_container_width=True)

                # Calculate and display correlation
                correlation = df[x_column].corr(df[y_column])
                st.metric("Correlation Coefficient", f"{correlation:.3f}")

            except Exception as e:
                st.error(f"Error creating scatter plot: {str(e)}")

    def create_histogram(self, df: pd.DataFrame, numeric_columns: List[str]):
        """Create interactive histogram"""

        if not numeric_columns:
            st.warning("Histogram requires numeric columns.")
            return

        col1, col2 = st.columns(2)

        with col1:
            selected_column = st.selectbox("Select column for histogram", numeric_columns, key="hist_col")
        with col2:
            bins = st.slider("Number of bins", min_value=5, max_value=100, value=30, key="hist_bins")

        if selected_column:
            try:
                fig = px.histogram(
                    df,
                    x=selected_column,
                    nbins=bins,
                    title=f"Distribution of {selected_column}",
                    height=self.default_height,
                    opacity=0.7
                )

                fig.update_layout(
                    xaxis_title=selected_column,
                    yaxis_title="Frequency",
                    bargap=0.1
                )

                st.plotly_chart(fig, use_container_width=True)

                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                data = df[selected_column].dropna()

                with col1:
                    st.metric("Mean", f"{data.mean():.3f}")
                with col2:
                    st.metric("Median", f"{data.median():.3f}")
                with col3:
                    st.metric("Std Dev", f"{data.std():.3f}")
                with col4:
                    st.metric("Count", len(data))

            except Exception as e:
                st.error(f"Error creating histogram: {str(e)}")

    def create_box_plot(self, df: pd.DataFrame, categorical_columns: List[str], numeric_columns: List[str]):
        """Create interactive box plot"""

        if not categorical_columns or not numeric_columns:
            st.warning("Box plot requires both categorical and numeric columns.")
            return

        col1, col2 = st.columns(2)

        with col1:
            x_column = st.selectbox("Select category column", categorical_columns, key="box_x")
        with col2:
            y_column = st.selectbox("Select numeric column", numeric_columns, key="box_y")

        if x_column and y_column:
            try:
                fig = px.box(
                    df,
                    x=x_column,
                    y=y_column,
                    title=f"Box Plot: {y_column} by {x_column}",
                    height=self.default_height
                )

                fig.update_layout(
                    xaxis_title=x_column,
                    yaxis_title=y_column
                )

                st.plotly_chart(fig, use_container_width=True)

                # Show statistics by category
                stats_by_category = df.groupby(x_column)[y_column].agg(['mean', 'median', 'std', 'count']).round(3)
                st.subheader(f"Statistics of {y_column} by {x_column}")
                st.dataframe(stats_by_category, use_container_width=True)

            except Exception as e:
                st.error(f"Error creating box plot: {str(e)}")

    def create_heatmap(self, df: pd.DataFrame, numeric_columns: List[str]):
        """Create correlation heatmap"""

        if len(numeric_columns) < 2:
            st.warning("Heatmap requires at least 2 numeric columns.")
            return

        # Allow user to select which columns to include
        selected_columns = st.multiselect(
            "Select columns for correlation heatmap",
            numeric_columns,
            default=numeric_columns[:10],  # Default to first 10 columns to avoid overcrowding
            key="heatmap_cols"
        )

        if len(selected_columns) < 2:
            st.warning("Please select at least 2 columns for the heatmap.")
            return

        try:
            # Calculate correlation matrix
            correlation_matrix = df[selected_columns].corr()

            # Create heatmap
            fig = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale='RdBu_r',
                title="Correlation Heatmap",
                height=max(400, len(selected_columns) * 40)
            )

            fig.update_layout(
                xaxis_title="Variables",
                yaxis_title="Variables"
            )

            st.plotly_chart(fig, use_container_width=True)

            # Find and display strong correlations
            st.subheader("Strong Correlations (|r| > 0.5)")
            strong_correlations = []

            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_val = correlation_matrix.iloc[i, j]
                    if abs(corr_val) > 0.5:
                        strong_correlations.append({
                            'Variable 1': correlation_matrix.columns[i],
                            'Variable 2': correlation_matrix.columns[j],
                            'Correlation': f"{corr_val:.3f}"
                        })

            if strong_correlations:
                strong_corr_df = pd.DataFrame(strong_correlations)
                st.dataframe(strong_corr_df, use_container_width=True)
            else:
                st.info("No strong correlations found (|r| > 0.5)")

        except Exception as e:
            st.error(f"Error creating heatmap: {str(e)}")

    def create_pie_chart(self, df: pd.DataFrame, categorical_columns: List[str]):
        """Create interactive pie chart"""

        if not categorical_columns:
            st.warning("Pie chart requires categorical columns.")
            return

        selected_column = st.selectbox("Select column for pie chart", categorical_columns, key="pie_col")

        if selected_column:
            try:
                # Get value counts
                value_counts = df[selected_column].value_counts()

                # Option to show only top N categories
                max_categories = st.slider("Maximum categories to show", 
                                         min_value=3, 
                                         max_value=min(20, len(value_counts)), 
                                         value=min(10, len(value_counts)),
                                         key="pie_max")

                # Take top N categories and group others as 'Others'
                if len(value_counts) > max_categories:
                    top_categories = value_counts.head(max_categories-1)
                    others_count = value_counts.tail(len(value_counts) - max_categories + 1).sum()

                    # Create new series with 'Others' category
                    display_data = pd.concat([top_categories, pd.Series([others_count], index=['Others'])])
                else:
                    display_data = value_counts

                fig = px.pie(
                    values=display_data.values,
                    names=display_data.index,
                    title=f"Distribution of {selected_column}",
                    height=self.default_height
                )

                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    textfont_size=12
                )

                st.plotly_chart(fig, use_container_width=True)

                # Show data table
                st.subheader("Category Counts")
                counts_df = pd.DataFrame({
                    'Category': display_data.index,
                    'Count': display_data.values,
                    'Percentage': (display_data.values / display_data.sum() * 100).round(2)
                })
                st.dataframe(counts_df, use_container_width=True)

            except Exception as e:
                st.error(f"Error creating pie chart: {str(e)}")

    def create_custom_chart(self, df: pd.DataFrame):
        """Allow users to create custom charts with more control"""

        st.subheader("🎨 Custom Chart Builder")

        col1, col2 = st.columns(2)

        with col1:
            chart_type = st.selectbox(
                "Chart Type",
                ["Scatter", "Bar", "Line", "Box", "Violin", "Area"],
                key="custom_type"
            )

        with col2:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            all_cols = df.columns.tolist()

        # Dynamic column selection based on chart type
        if chart_type in ["Scatter", "Line"]:
            x_col = st.selectbox("X-axis", all_cols, key="custom_x")
            y_col = st.selectbox("Y-axis", numeric_cols, key="custom_y")
            color_col = st.selectbox("Color by (optional)", ["None"] + categorical_cols, key="custom_color")

            if x_col and y_col:
                color_param = color_col if color_col != "None" else None

                if chart_type == "Scatter":
                    fig = px.scatter(df, x=x_col, y=y_col, color=color_param)
                else:  # Line
                    fig = px.line(df, x=x_col, y=y_col, color=color_param)

                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Bar":
            x_col = st.selectbox("X-axis", categorical_cols, key="custom_bar_x")
            y_col = st.selectbox("Y-axis", numeric_cols, key="custom_bar_y")

            if x_col and y_col:
                fig = px.bar(df, x=x_col, y=y_col)
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type in ["Box", "Violin"]:
            x_col = st.selectbox("Category", categorical_cols, key="custom_box_x")
            y_col = st.selectbox("Values", numeric_cols, key="custom_box_y")

            if x_col and y_col:
                if chart_type == "Box":
                    fig = px.box(df, x=x_col, y=y_col)
                else:  # Violin
                    fig = px.violin(df, x=x_col, y=y_col, box=True)

                st.plotly_chart(fig, use_container_width=True)
