#Scenario7: In this scenario, we answer questions based on tabular data by leveraging the ontologies generated in Scenario 6
#please make sure you install the following packages
#!pip install rdflib hdbcli langchain_aws langchain_core
from xml.etree import ElementTree as ET
import boto3
from langchain_core.prompts import PromptTemplate
from hdbcli import dbapi
from langchain_aws import ChatBedrock
from typing import Dict, List
import pandas as pd
import os
import dotenv

def setup(): 
    dotenv.load_dotenv()  # Load environment variables from .env file

    # Initialize Bedrock runtime client
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',  # Specify Bedrock runtime service
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),  # Pass AWS credentials
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION_NAME")  # Set AWS region
    )
    # Set up AWS Bedrock client
    anthropic = ChatBedrock(
        model_id=os.getenv("INFERENCE_PROFILE_ARN"),  # Use inference profile ARN as model ID
        client=bedrock_client,  # Use configured Bedrock client
        model_kwargs={  # Model parameters
            "temperature": 0.3,  # Controls response randomness (0-1) - CHANGE: Reduced from 0.5 to 0.3
            "max_tokens": 4096  # Maximum length of response - CHANGE: Increased from 2048 to 4096
        }
    )

    conn = dbapi.connect(
        user=os.getenv("HANA_USER"),  # Database username
        password=os.getenv("HANA_PASSWORD"),  # Database password
        address=os.getenv("HANA_HOST"),  # DB address
        port=443  # Connection port
    )

    return anthropic, conn

"""""
Alternatively, if you wish to use Anthropic from SAP GenAI Hub, you can use the following setup() function:
#Here are the necessary Packages

#!%pip install generative-ai-hub-sdk[all]

import pandas as pd
from xml.etree import ElementTree as ET
from langchain_core.prompts import PromptTemplate
from hdbcli import dbapi
from typing import Dict, List
from gen_ai_hub.proxy.langchain.amazon import ChatBedrock
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
import os

# Set up the AI core credentials
os.environ['AICORE_AUTH_URL'] = "<Your AI Core Auth URL>" #TODO
os.environ['AICORE_CLIENT_ID'] = "<Your AI Core Client ID>"#TODO
os.environ['AICORE_RESOURCE_GROUP'] = 'default'
os.environ['AICORE_CLIENT_SECRET'] = "<Your AI Core Client Secret>"#TODO
os.environ['AICORE_BASE_URL'] = "<Your AI Core Base URL>" #TODO

def setup(): 
    
    proxy_client = get_proxy_client('gen-ai-hub') # Get the proxy client

    anthropic = ChatBedrock(
        model_name="anthropic--claude-3.5-sonnet",
        proxy_client=proxy_client # Pass the proxy client to ChatBedrock
    )

    conn = dbapi.connect(
        user="HANA_ADMIN", #TODO Add your credentials
        password="HANA_ADMIN_PW",#TODO Add your credentials
        address='instance',#TODO Add your credentials
        port=443,
    )

    return anthropic, conn

"""""
def extract_metadata(question: str, conn) -> List[Dict]:
    """Extract relevant metadata from RDF triples using SPARQL"""
    cursor = conn.cursor()
    
    try:
        # Execute SPARQL query to get all relevant triples
        sparql_query = """
        SELECT ?s ?p ?o
        WHERE {
            ?s ?p ?o.
            FILTER(STRSTARTS(STR(?s), "http://flight_anubhavtrainings.com/")) #TODO
        }
        """
        
        resp = cursor.callproc('SPARQL_EXECUTE', (sparql_query, 'Metadata headers describing Input and/or Output', '?', None))
        
        if resp and len(resp) >= 3 and resp[2]:
            # Parse the XML response
            xml_response = resp[2]
            results = parse_sparql_results(xml_response)
            
            # Convert to our standard format
            metadata = []
            for row in results:
                metadata.append({
                    's': row.get('s', ''),
                    'p': row.get('p', ''),
                    'o': row.get('o', '')
                })
            return metadata
        return []
    
    except Exception as e:
        print(f"Error executing SPARQL query: {e}")
        return []
    finally:
        cursor.close()

def analyze_metadata(metadata: List[Dict], question: str, anthropic) -> Dict:
    """Analyze the metadata to identify tables, columns, and relationships"""
    # Convert metadata to a format the LLM can understand
    metadata_str = "\n".join([f"{item['s']} {item['p']} {item['o']}" for item in metadata])
    
    prompt_template = """Given the following RDF metadata about database tables and columns, analyze the user's question and identify:
    1. The main table(s) involved with their schema (SFLIGHT)
    2. The columns needed (including any aggregation functions)
    3. Any filters or conditions
    4. Any joins required

    Important Rules:
    - Always include the schema name (SFLIGHT) before table names
    - When using GROUP BY, include the grouping columns in SELECT
    - Never include any explanatory text in the SQL output
    - For airline codes like American Airlines, use 'AA' in filters

    For each column, include:
    - The column name (prefix with table alias if needed)
    - Any aggregation function (SUM, COUNT, etc.)
    - Any filter conditions
    - Whether it's a grouping column

    For tables, include:
    - The full table name with schema (e.g., SFLIGHT.SBOOK)
    - Any relationships to other tables

    Metadata:
    {metadata}

    Question: {question}

    Return your analysis in this exact format (without any additional explanations):
    Tables: [schema.table]
    Columns: [column names with aggregations like SUM(LOCCURAM)]
    Filters: [filter conditions]
    Joins: [join conditions]
    GroupBy: [columns to group by]
    """
    
    prompt = PromptTemplate.from_template(prompt_template).invoke({
        "metadata": metadata_str,
        "question": question
    })
    
    # We'll use the LLM to extract the key components
    analysis = anthropic.invoke(prompt)
    return parse_analysis(analysis.content)

def parse_analysis(analysis_text: str) -> Dict:
    """Parse the LLM's analysis into a structured format"""
    components = {
        "tables": [],
        "columns": [],
        "filters": [],
        "joins": [],
        "group_by": []
    }
    
    # Remove any "Explanation:" text
    analysis_text = analysis_text.split("Explanation:")[0].strip()
    
    def clean_brackets(text: str) -> str:
        """Remove all types of brackets and clean text"""
        return text.replace('[', '').replace(']', '').replace('(', '').replace(')', '').strip()
    
    def extract_aggregation(text: str) -> tuple:
        """Extract aggregation function and column from text like 'SUM(COLUMN)'"""
        text = text.strip()
        if '(' in text and ')' in text:
            # Handle cases like 'SUM(LOCCURAM)' or '[SUM(LOCCURAM)'
            agg_part = text.split('(')[0].replace('[', '').strip().upper()
            col_part = text.split('(')[1].split(')')[0].replace('[', '').replace(']', '').strip()
            return (agg_part, col_part)
        else:
            # Regular column
            clean_text = clean_brackets(text)
            return (None, clean_text) if clean_text else (None, '')
    
    # Parse each section
    for line in analysis_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('Tables:'):
            tables_text = line.split(':', 1)[1].strip()
            # Clean and split tables
            tables = [clean_brackets(t.strip()) for t in tables_text.split(',') if clean_brackets(t.strip())]
            components['tables'] = [t for t in tables if t and t.lower() not in ['none', '']]
            
        elif line.startswith('Columns:'):
            cols_text = line.split(':', 1)[1].strip()
            # Handle columns with potential aggregations
            for col_part in cols_text.split(','):
                col_part = col_part.strip()
                if col_part:
                    agg, col = extract_aggregation(col_part)
                    if col:  # Only add if column name is not empty
                        components['columns'].append((agg, col))
                        
        elif line.startswith('Filters:'):
            filters_text = line.split(':', 1)[1].strip()
            filters = [clean_brackets(f.strip()) for f in filters_text.split(' AND ') if clean_brackets(f.strip())]
            components['filters'] = [f for f in filters if f and f.lower() not in ['none', '']]
            
        elif line.startswith('Joins:'):
            joins_text = line.split(':', 1)[1].strip()
            joins = [clean_brackets(j.strip()) for j in joins_text.split(',') if clean_brackets(j.strip())]
            components['joins'] = [j for j in joins if j and j.lower() not in ['none', '']]
            
        elif line.startswith('GroupBy:'):
            group_text = line.split(':', 1)[1].strip()
            group_bys = [clean_brackets(g.strip()) for g in group_text.split(',') if clean_brackets(g.strip())]
            components['group_by'] = [g for g in group_bys if g and g.lower() not in ['none', '']]
    
    # Ensure schema is included in table names
    components['tables'] = [f"SFLIGHT.{t.split('.')[-1]}" if '.' not in t else t for t in components['tables']]
    
    # Ensure grouping columns are included in SELECT
    for group_col in components['group_by']:
        # Check if this exact (None, group_col) pair exists
        col_exists = any(col == (None, group_col) for col in components['columns'])
        if not col_exists:
            components['columns'].append((None, group_col))
    
    return components

def parse_sparql_results(xml_response: str) -> List[Dict]:
    """Parse SPARQL XML results into a list of dictionaries"""
    try:
        root = ET.fromstring(xml_response)
        results = []
        
        for result in root.findall('.//{http://www.w3.org/2005/sparql-results#}result'):
            row = {}
            for binding in result:
                var_name = binding.attrib['name']
                value = binding[0]  # uri or literal
                if value.tag.endswith('uri'):
                    row[var_name] = value.text
                elif value.tag.endswith('literal'):
                    row[var_name] = value.text
            results.append(row)
        return results
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []

def generate_sql(components: Dict) -> str:
    """Generate clean SQL query from the analyzed components - FIXED VERSION"""
    # Validate components
    if not components["tables"]:
        raise ValueError("No tables identified for SQL generation")
    
    # Enhanced cleaning function
    def clean_component(component):
        if not component:
            return ""
        # Remove all types of brackets and extra whitespace
        cleaned = str(component).replace('[', '').replace(']', '').replace('(', '').replace(')', '').strip()
        return cleaned
    
    # Build SELECT clause
    select_parts = []
    
    # Process the columns properly
    for agg, col in components["columns"]:
        # Clean both aggregation and column
        clean_agg = clean_component(agg) if agg else None
        clean_col = clean_component(col)
        
        if not clean_col or clean_col.lower() in ['none', '']:
            continue
            
        if clean_agg and clean_agg.upper() in ['SUM', 'COUNT', 'AVG', 'MAX', 'MIN']:
            select_parts.append(f"{clean_agg.upper()}({clean_col}) AS {clean_agg.upper()}_{clean_col}")
        else:
            select_parts.append(clean_col)
    
    # Add GROUP BY columns to SELECT if not already present
    for group_col in components.get("group_by", []):
        clean_group_col = clean_component(group_col)
        if clean_group_col and clean_group_col not in [clean_component(col[1]) for col in components["columns"]]:
            select_parts.insert(0, clean_group_col)  # Add grouping columns first
    
    if not select_parts:  # Default to all columns if none specified
        select_parts.append("*")

    select_clause = ", ".join(select_parts)
    print(f"SELECT CLAUSE: {select_clause}")
    
    # Build FROM clause
    from_table = clean_component(components["tables"][0])
    if not from_table.startswith("SFLIGHT."):
        from_table = f"SFLIGHT.{from_table}"
    from_clause = from_table
    
    # Handle joins - only add if they are meaningful
    join_clauses = []
    for join in components.get("joins", []):
        clean_join = clean_component(join)
        # Skip empty joins, 'None', or just 'INNER JOIN' without conditions
        if clean_join and clean_join.lower() not in ['none', 'inner join', '']:
            join_clauses.append(f"INNER JOIN SFLIGHT.SCUSTOM ON {clean_join}")
    
    print(f"JOIN CLAUSES: {join_clauses}")
    
    # Build WHERE clause
    where_clauses = []
    for filter_cond in components.get("filters", []):
        clean_filter = clean_component(filter_cond)
        if clean_filter and clean_filter.lower() != 'none':
            where_clauses.append(clean_filter)
    
    where_clause = " AND ".join(where_clauses) if where_clauses else ""
    where_clause = where_clause.replace(",", " AND")
    print(f"WHERE CLAUSE: {where_clause}")
    
    # Build GROUP BY clause
    group_by_columns = []
    for g in components.get("group_by", []):
        clean_g = clean_component(g)
        if clean_g and clean_g.lower() not in ['none', '']:
            group_by_columns.append(clean_g)
    
    group_by_clause = ", ".join(group_by_columns) if group_by_columns else ""
    print(f"GROUP BY CLAUSE: {group_by_clause}")
    
    # Construct the SQL
    sql = f"SELECT {select_clause} FROM {from_clause}"
    
    # Only add joins if they exist
    if join_clauses:
        sql += " " + " ".join(join_clauses)
    
    if where_clause:
        sql += f" WHERE {where_clause}"
    
    if group_by_clause:
        sql += f" GROUP BY {group_by_clause}"
    
    # Final formatting
    sql = sql.strip()
    if not sql.endswith(';'):
        sql += ';'
    
    print(f"GENERATED SQL: {sql}")
    return sql

def execute_sql(sql_query: str, conn) -> pd.DataFrame:
    """Execute the generated SQL query and return results"""
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()

def generate_response_structured(question: str, results: pd.DataFrame, anthropic) -> str:
    """Generate a natural language response from the query results"""
    if results.empty:
        return "No results found for your query."
    
    prompt_template = """Convert the following query results into a natural language response to the user's question. 
    Keep the response concise but informative. Include relevant numbers and comparisons where appropriate.
    
    Question: {question}
    
    Results:
    {results}
    
    Response:
    """
    
    prompt = PromptTemplate.from_template(prompt_template).invoke({
        "question": question,
        "results": results.to_string()
    })
    
    response = anthropic.invoke(prompt)
    return response.content

def process_question(question: str, conn, anthropic) -> str:
    """Main function to process a user question with better error handling"""
    try:
        # Step 1: Extract relevant metadata using SPARQL
        metadata = extract_metadata(question, conn)
        
        if not metadata:
            return "Could not retrieve database metadata."
        
        # Step 2: Analyze the metadata and question
        components = analyze_metadata(metadata, question, anthropic)
        
        print("ANALYZED COMPONENTS:", components)
        # Step 3: Generate SQL query
        sql_query = generate_sql(components)
    
        # Step 4: Execute SQL
        results = execute_sql(sql_query, conn)
        
        # Step 5: Generate response
        response = generate_response_structured(question, results, anthropic)
        
        return response
    except Exception as e:
        return f"Error processing question: {str(e)}"


# Test the fix
def process_workflow(question):
    anthropic, conn = setup()
    #question = "What is the total revenue from American Airlines flights in 2022?"
    response = process_question(question, conn, anthropic)
    print("FINAL RESPONSE:", response)
    return response

#process_workflow("What is the total revenue from American Airlines flights in 2022?")