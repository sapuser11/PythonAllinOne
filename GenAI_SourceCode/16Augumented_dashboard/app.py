import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import io
from datetime import datetime

# Import your existing SalesDataAssistant class
from sales_assistant import SalesDataAssistant  # Adjust import name as needed
     
# Streamlit App Configuration
st.set_page_config(
    page_title="Anubhav Trainings Sales Data Augmented AI",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'assistant' not in st.session_state:
    st.session_state.assistant = None

def create_chart(chart_config, filtered_df):
    """Create different types of charts based on configuration"""
    try:
        chart_type = chart_config.get('chart_type', 'bar').lower()
        title = chart_config.get('title', 'Chart')
        x_axis = chart_config.get('x_axis')
        y_axis = chart_config.get('y_axis')
        aggregation = chart_config.get('aggregation', 'sum')
        group_by = chart_config.get('group_by')
        
        # Prepare data for plotting
        if group_by and group_by in filtered_df.columns:
            if aggregation == 'sum':
                plot_df = filtered_df.groupby([x_axis, group_by])[y_axis].sum().reset_index()
            elif aggregation == 'count':
                plot_df = filtered_df.groupby([x_axis, group_by]).size().reset_index(name=y_axis)
            elif aggregation == 'avg':
                plot_df = filtered_df.groupby([x_axis, group_by])[y_axis].mean().reset_index()
            else:
                plot_df = filtered_df.groupby([x_axis, group_by])[y_axis].sum().reset_index()
        else:
            if aggregation == 'sum':
                plot_df = filtered_df.groupby(x_axis)[y_axis].sum().reset_index()
            elif aggregation == 'count':
                plot_df = filtered_df.groupby(x_axis).size().reset_index(name=y_axis)
            elif aggregation == 'avg':
                plot_df = filtered_df.groupby(x_axis)[y_axis].mean().reset_index()
            else:
                plot_df = filtered_df.groupby(x_axis)[y_axis].sum().reset_index()
        
        # Create different chart types
        if chart_type == 'bar':
            fig = px.bar(plot_df, x=x_axis, y=y_axis, title=title, 
                        color=group_by if group_by else None)
        elif chart_type == 'line':
            fig = px.line(plot_df, x=x_axis, y=y_axis, title=title,
                         color=group_by if group_by else None)
        elif chart_type == 'pie':
            fig = px.pie(plot_df, names=x_axis, values=y_axis, title=title)
        elif chart_type == 'area':
            fig = px.area(plot_df, x=x_axis, y=y_axis, title=title,
                         color=group_by if group_by else None)
        elif chart_type == 'scatter':
            fig = px.scatter(plot_df, x=x_axis, y=y_axis, title=title,
                           color=group_by if group_by else None)
        else:
            fig = px.bar(plot_df, x=x_axis, y=y_axis, title=title)
        
        fig.update_layout(height=500)
        return fig, plot_df
        
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None, None

def download_chart(fig, filename="sales_chart"):
    """Create download button for chart"""
    img_bytes = fig.to_image(format="png")
    st.download_button(
        label="📥 Download Chart as PNG",
        data=img_bytes,
        file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        mime="image/png"
    )

def main():
    # Header
    st.title("📊 Sales Data AI Assistant")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🔧 Configuration")
                    
        # Initialize assistant
        if st.session_state.assistant is None:
            try:
                with st.spinner("Connecting to database and initializing AI assistant..."):
                    st.session_state.assistant = SalesDataAssistant()  # df parameter not used
                st.success("✅ AI Assistant initialized!")
                st.success(f"✅ Data loaded: {st.session_state.assistant.data_summary['shape'][0]:,} rows × {st.session_state.assistant.data_summary['shape'][1]} columns")
            except Exception as e:
                st.error(f"Error initializing assistant: {str(e)}")
        
        # Show data info if assistant is loaded
        if st.session_state.assistant is not None:
            # Show data preview
            with st.expander("📊 Data Preview"):
                sample_data = st.session_state.assistant.data_summary['sample_data']
                st.dataframe(pd.DataFrame(sample_data))
                
            with st.expander("📋 Data Summary"):
                st.write(f"**Rows:** {st.session_state.assistant.data_summary['shape'][0]:,}")
                st.write(f"**Columns:** {st.session_state.assistant.data_summary['shape'][1]}")
                st.write("**Available Columns:**")
                cols = st.session_state.assistant.data_summary['columns']
                for i in range(0, len(cols), 3):
                    col_display = st.columns(3)
                    for j, col in enumerate(cols[i:i+3]):
                        col_display[j].code(col)
        else:
            st.warning("⚠️ Please enter your OpenAI API key to connect to the database.")
    
    # Main interface
    if st.session_state.assistant is not None:
        # Output type selection
        output_type = st.radio(
            "🎯 Choose Output Type:",
            ["Answer", "Chart"],
            horizontal=True
        )
        
        if output_type == "Answer":
            # Question answering interface
            st.subheader("💬 Ask Questions About Your Sales Data")
            
            # Pre-defined questions
            example_questions = [
                "What's the total order value by customer segment?",
                "Total customer meetings done by each sales agent by last name?",
                "How many unique customers by country?",
                "What's the average order value by product type?",
                "Show sales trends over time"
            ]
            
            selected_example = st.selectbox("Or choose an example question:", 
                                          ["Custom question..."] + example_questions)
            
            if selected_example != "Custom question...":
                user_question = selected_example
            else:
                user_question = st.text_area("Enter your question:", height=100)
            
            if st.button("🤔 Get Answer") and user_question and st.session_state.assistant:
                with st.spinner("Analyzing your question..."):
                    try:
                        answer = st.session_state.assistant.answer_question(user_question)
                        st.write("**Answer:**")
                        st.write(answer)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            elif not st.session_state.assistant:
                st.warning("⚠️ Please enter your OpenAI API key in the sidebar first")
        
        else:  # Chart option
            st.subheader("📈 Generate Interactive Charts")
            
            # Chart request input
            col1, col2 = st.columns([3, 1])
            
            with col1:
                chart_request = st.text_area(
                    "Describe the chart you want:",
                    placeholder="e.g., 'Show total order value by customer segment as a bar chart'",
                    height=100
                )
            
            with col2:
                chart_type_override = st.selectbox(
                    "Force Chart Type:",
                    ["Auto", "bar", "line", "pie", "area", "scatter"]
                )
            
           
            # Generate chart button
            if st.button("📊 Generate Chart") and chart_request and st.session_state.assistant:
                with st.spinner("Creating your chart..."):
                    try:
                        # Get chart configuration from AI (it handles data filtering internally)
                        chart_config = st.session_state.assistant.generate_chart_data(chart_request)
                        
                        # Override chart type if specified
                        if chart_type_override != "Auto":
                            chart_config['chart_type'] = chart_type_override
                        
                            if 'error' not in chart_config:
                                # Show AI-generated configuration
                                with st.expander("🤖 AI Generated Chart Configuration"):
                                    st.json(chart_config)
                                
                                st.success("✅ Chart configuration generated successfully!")
                                st.info(f"📊 Chart Type: {chart_config.get('chart_type', 'N/A')}")
                                st.info(f"📈 Title: {chart_config.get('title', 'N/A')}")
                                st.info(f"🔢 X-Axis: {chart_config.get('x_axis', 'N/A')}")
                                st.info(f"🔢 Y-Axis: {chart_config.get('y_axis', 'N/A')}")

                                filtered_df = st.session_state.assistant.df
                                
                                # Aggregate if required
                                if chart_config.get('aggregation') == 'sum':
                                    plot_df = (
                                        filtered_df.groupby(chart_config['x_axis'])[chart_config['y_axis']]
                                        .sum()
                                        .reset_index()
                                    )
                                elif chart_config.get('aggregation') == 'count':
                                    plot_df = (
                                        filtered_df.groupby(chart_config['x_axis'])[chart_config['y_axis']]
                                        .count()
                                        .reset_index()
                                    )
                                else:
                                    plot_df = filtered_df
                                
                                chart_type = chart_config.get("chart_type", "bar")

                                if chart_type == "pie":
                                    fig = px.pie(
                                        plot_df,
                                        names=chart_config.get("x_axis"),
                                        values=chart_config.get("y_axis"),
                                        title=chart_config.get("title", "Generated Chart")
                                    )
                                else:
                                    # Create chart using Plotly
                                    fig = getattr(px, chart_config.get('chart_type', 'bar'))(
                                        plot_df,
                                        x=chart_config.get('x_axis'),
                                        y=chart_config.get('y_axis'),
                                        title=chart_config.get('title', 'Generated Chart')
                                    )
                                
                                # Display the chart in Streamlit
                                st.plotly_chart(fig, use_container_width=True)

                            else:
                                st.error("❌ Error generating chart configuration")
                                st.write(chart_config)

                    except Exception as e:
                        st.error(f"Error generating chart: {str(e)}")
            elif not st.session_state.assistant:
                st.warning("⚠️ Please enter your OpenAI API key in the sidebar first")
    
    else:
        st.info("🔑 Please enter your OpenAI API key in the sidebar to connect to the database and start analyzing your sales data!")
        
        # Show usage example
        st.subheader("🚀 How to Use")
        st.markdown("""
        1. **Enter OpenAI API Key** in the sidebar
        2. **Wait for database connection** and AI assistant initialization
        3. **Choose output type**: Answer (Q&A) or Chart (Visualizations)
        4. **Ask questions** or **request charts** about your sales data
        5. **Download** configurations and results
        """)
        
        # Show expected data format
        st.subheader("📊 Your Sales Data Structure")
        expected_columns = [
            "order_id", "date", "sales_agent_last_name", "sales_agent_first_name",
            "customer", "customer_segment", "country", "latitude", "longitude",
            "customer_status", "product", "product_type", "no_customer_meetings",
            "units_sold", "order_value"
        ]
        
        st.write("The app will analyze data with these columns:")
        for i in range(0, len(expected_columns), 3):
            cols = st.columns(3)
            for j, col in enumerate(expected_columns[i:i+3]):
                if j < len(cols):
                    cols[j].code(col)

if __name__ == "__main__":
    main()