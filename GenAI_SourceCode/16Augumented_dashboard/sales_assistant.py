from init_db import create_connection, read_data
import pandas as pd
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import json

class SalesDataAssistant:
    def __init__(self):
        self.df = read_data(create_connection())
        self.llm = self._set_llm()
        self.data_summary = self._get_data_summary()

    def _set_llm(self, model="gpt-3.5-turbo", temperature=0.1):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")    
        return ChatOpenAI(model=model, temperature=temperature, openai_api_key=api_key)
        

    def _get_data_summary(self):
        #Get unique values for categorical columns
        categorical_info = {}
        categorical_cols = ['customer_segment', 'country', 'customer_status', 'product', 'product_type']
        for col in categorical_cols:    
            categorical_info[col] = list(self.df[col].unique())[:10] ##Show first 10 unique values

        summary = {
            "columns": self.df.columns.tolist(),
            "shape": self.df.shape,
            "dtypes": self.df.dtypes.apply(lambda x: x.name).to_dict(),
            "categorical_values": categorical_info,
            "sample_data": self.df.head(5).to_dict(orient='records')
        }
        return summary
    

    ## Normal Questions from user in text format and result Text format    
    def answer_question(self, user_question):
        """Answer questions about the sales data"""
        system_prompt = f"""You are a helpful sales data analyst assistant. 
        You have access to a sales dataset with the following information:
        
        Dataset contains {self.data_summary['shape'][0]} rows and {self.data_summary['shape'][1]} columns.
        
        Columns and their data types:
        - order_id: Unique identifier for each order
        - date: Order date
        - sales_agent_last_name: Last name of sales agent
        - sales_agent_first_name: First name of sales agent  
        - customer: Customer name
        - customer_segment: {self.data_summary['categorical_values'].get('customer_segment', 'Various segments')}
        - country: {self.data_summary['categorical_values'].get('country', 'Various countries')}
        - latitude: Customer location latitude
        - longitude: Customer location longitude
        - customer_status: {self.data_summary['categorical_values'].get('customer_status', 'Various statuses')}
        - product: {self.data_summary['categorical_values'].get('product', 'Various products')}
        - product_type: {self.data_summary['categorical_values'].get('product_type', 'Various product types')}
        - no_customer_meetings: Number of customer meetings
        - units_sold: Quantity of units sold
        - order_value: Total monetary value of the order
        
        Sample data: {self.data_summary['sample_data']}
        
        Provide clear, accurate answers about the sales data. You can suggest specific calculations, 
        groupings, or analysis that would be helpful for the user's question."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_question)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_chart_data(self, chart_request):
        """Generate chart configuration based on user request"""
        chart_prompt = f"""You are a data visualization expert. Based on the sales dataset with specific columns, 
        generate a JSON configuration for creating a chart based on the user's request.
        
        Available columns in sales dataset:
        - order_id (unique identifier)
        - date (order date)
        - sales_agent_last_name, sales_agent_first_name (agent names)
        - customer (customer name)
        - customer_segment (customer segments: {self.data_summary['categorical_values'].get('customer_segment', 'various')})
        - country (countries: {self.data_summary['categorical_values'].get('country', 'various')})
        - latitude, longitude (geographic coordinates)
        - customer_status (status: {self.data_summary['categorical_values'].get('customer_status', 'various')})
        - product (products: {self.data_summary['categorical_values'].get('product', 'various')})
        - product_type (types: {self.data_summary['categorical_values'].get('product_type', 'various')})
        - no_customer_meetings (number of meetings)
        - units_sold (quantity sold)
        - order_value (monetary value)
        
        Return a JSON object with this structure:
        {{
            "chart_type": "bar/line/pie/scatter/map",
            "title": "Descriptive chart title",
            "x_axis": "column_name_for_x_axis",
            "y_axis": "column_name_for_y_axis", 
            "aggregation": "sum/count/avg/max/min",
            "group_by": "column_to_group_by_if_needed",
            "filters": "any_filters_to_apply",
            "description": "What insights this chart provides"
        }}
        
        For geographic data, suggest map visualizations using latitude/longitude.
        For time series, use date column with appropriate aggregation.
        For sales analysis, focus on order_value, units_sold as measures.
        
        User request: {chart_request}
        
        Return only the JSON object."""
        
        messages = [
            SystemMessage(content=chart_prompt),
            HumanMessage(content=chart_request)
        ]
        
        response = self.llm.invoke(messages)
        try:
            chart_config = json.loads(response.content)
            return chart_config
        except json.JSONDecodeError:
            return {"error": "Could not parse chart configuration", "raw_response": response.content}

    # Quick start function for your DataFrame
    def analyze_sales_data(df, question=None, chart_request=None):
        """Quick function to analyze your sales data"""
        assistant = SalesDataAssistant(df)
        
        results = {}
        
        if question:
            results['answer'] = assistant.answer_question(question)
        
        if chart_request:
            results['chart_config'] = assistant.generate_chart_data(chart_request)
        
        return results
    