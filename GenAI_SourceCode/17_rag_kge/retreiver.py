# Anubhav Trainings : But runtime implementation of Bedrock to generate the SPARQL query and answer the question
from langchain_core.language_models.base import BaseLanguageModel  # Base class for language models
from pydantic import BaseModel, Field  # For data validation and settings management
import boto3  # AWS SDK for Python
from langchain_aws import ChatBedrock  # LangChain integration for AWS Bedrock
from langchain_core.prompts import PromptTemplate  # For creating prompt templates
from typing_extensions import TypedDict, Annotated  # For type hints
from hdbcli import dbapi  # SAP HANA database connector
from dotenv import load_dotenv  # For loading environment variables from .env file
import os
import json  # CHANGE 1: Added json import

load_dotenv()  # Load environment variables from .env file

# Define configuration model for AWS Bedrock using Pydantic
class CustomBedrockLLMConfig(BaseModel):
    # Required model ID field with description
    model_id: str = Field(..., description=os.getenv("MODEL_ID"))  # e.g., "anthropic.claude-3-sonnet-20240229-v1:0"
    # Required AWS access key field
    aws_access_key_id: str = Field(..., description=os.getenv("AWS_ACCESS_KEY_ID"))
    # Required AWS secret key field
    aws_secret_access_key: str = Field(..., description=os.getenv("AWS_SECRET_ACCESS_KEY"))
    # Required AWS region field
    aws_region_name: str = Field(..., description=os.getenv("AWS_REGION_NAME"))
    # Inference profile ARN field (optional)
    inference_profile_arn: str = Field(None, description=os.getenv("INFERENCE_PROFILE_ARN"))

# Custom language model implementation for AWS Bedrock
class CustomBedrockLLM(BaseLanguageModel):
    # Class variable to hold configuration
    config: CustomBedrockLLMConfig

    # Constructor method
    def __init__(self, **kwargs):
        # Call parent class constructor
        super().__init__(**kwargs)
        # Initialize configuration with provided keyword arguments
        self.config = CustomBedrockLLMConfig(**kwargs)

    # CHANGE 2: Fixed the _call method to use direct Bedrock invocation
    def _call(self, query):
        # Create AWS session with credentials
        session = boto3.Session(
            aws_access_key_id=self.config.aws_access_key_id,  # Set access key
            aws_secret_access_key=self.config.aws_secret_access_key,  # Set secret key
            region_name=self.config.aws_region_name  # Set AWS region
        )

        # Create Bedrock client from session
        bedrock_client = session.client('bedrock-runtime')  # CHANGE: Use bedrock-runtime instead of bedrock

        # CHANGE 3: Use proper direct invocation method
        try:
            # Convert query to string if it's a PromptValue object
            if hasattr(query, 'to_string'):
                prompt_text = query.to_string()
            elif hasattr(query, 'text'):
                prompt_text = query.text
            else:
                prompt_text = str(query)

            # Prepare the request body for Claude models
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt_text
                    }
                ]
            }

            # Make the API call with inference profile ARN as model ID
            response = bedrock_client.invoke_model(
                modelId=self.config.inference_profile_arn,  # Use inference profile ARN directly
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract content from Claude response
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0].get('text', '')
            else:
                print(f"Unexpected response format: {response_body}")
                return None

        except Exception as e:
            print(f"Direct Bedrock invocation failed: {e}")
            return None

    # Implementation of required LangChain interface methods
    def __call__(self, query):
        return self._call(query)

    def agenerate_prompt(self, input_prompt):
        return input_prompt

    def apredict(self, query):
        return self._call(query)

    def apredict_messages(self, messages):
        return self._call(messages[0].content)

    def generate_prompt(self, input_prompt):
        return input_prompt

    def invoke(self, query):
        return self._call(query)

    def predict(self, query):
        return self._call(query)

    def predict_messages(self, messages):
        return self._call(messages[0].content)

# AWS credentials configuration (NOTE: These should be secured properly in production)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")  # AWS access key ID
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")  # AWS secret access key
AWS_DEFAULT_REGION = os.getenv("AWS_REGION_NAME")  # AWS region name

# Initialize Bedrock runtime client
bedrock_client = boto3.client(
    service_name='bedrock-runtime',  # Specify Bedrock runtime service
    aws_access_key_id=AWS_ACCESS_KEY_ID,  # Pass AWS credentials
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION  # Set AWS region
)

# CHANGE 4: Modified ChatBedrock configuration to use inference profile ARN
try:
    anthropic = ChatBedrock(
        model_id=os.getenv("INFERENCE_PROFILE_ARN"),  # Use inference profile ARN as model ID
        client=bedrock_client,  # Use configured Bedrock client
        model_kwargs={  # Model parameters
            "temperature": 0.3,  # Controls response randomness (0-1) - CHANGE: Reduced from 0.5 to 0.3
            "max_tokens": 4096  # Maximum length of response - CHANGE: Increased from 2048 to 4096
        }
    )
    print("✓ ChatBedrock configured with inference profile")
except Exception as e:
    print(f"❌ Failed to configure ChatBedrock: {e}")
    # Fallback to custom implementation
    anthropic = None

# Establish connection to SAP HANA database
conn = dbapi.connect(
    user=os.getenv("HANA_USER"),  # Database username
    password=os.getenv("HANA_PASSWORD"),  # Database password
    address=os.getenv("HANA_HOST"),  # DB address
    port=443  # Connection port
)

# Define template for SPARQL query generation
#give example in template and try different LLMs
template = '''Given an input question, your task is to create a syntactically correct SPARQL query to retrieve information from an RDF graph. The graph may contain variations in spacing, underscores, dashes, capitalization, reversed relationships, and word order. You must account for these variations using the `REGEX()` function in SPARQL. In the RDF graph, subjects are represented as "s", objects are represented as "o", and predicates are represented as "p". Account for underscores.

Example Question: "What are SAP HANA Hotspots"
Example SPARQL Query: SELECT ?s ?p ?o
WHERE {{
    ?s ?p ?o .
    FILTER(
        REGEX(str(?s), "SAP_HANA_Hotspots", "i") ||
        REGEX(str(?o), "SAP_HANA_Hotspots", "i")
    )
}}

Retrieve only triples beginning with "http://anubhavtrainings.com/"
Use the following format:
Question: f{input}
S: Subject to look for in the RDF graph
P: Predicate to look for in the RDF graph
O: Object to look for in the RDF graph
SPARQL Query: SPARQL Query to run, including s-p-o structure
'''

# Create prompt template from the template string
query_prompt_template = PromptTemplate.from_template(template)

# Define type for state dictionary using TypedDict
class State(TypedDict):
    question: str  # The input question
    s: str  # Subject for SPARQL query
    p: str  # Predicate for SPARQL query
    o: str  # Object for SPARQL query
    query: str  # The generated query

# Define output type for structured LLM response
class QueryOutput(TypedDict):
    """Generated SPARQL query."""
    query: Annotated[str, ..., "Syntactically valid SPARQL query."]

# CHANGE 5: Modified write_query function to handle both ChatBedrock and custom implementation
def write_query(state: State):
    """Generate SPARQL query to fetch information."""
    # Format the prompt with the input question
    prompt = query_prompt_template.invoke({"input": state["question"]})
    
    try:
        if anthropic:
            # Try using ChatBedrock first
            structured_llm = anthropic.with_structured_output(QueryOutput)
            result = structured_llm.invoke(prompt)
        else:
            # Fallback to custom implementation
            custom_llm = CustomBedrockLLM(
                model_id=os.getenv("MODEL_ID"),
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                aws_region_name=AWS_DEFAULT_REGION,
                inference_profile_arn=os.getenv("INFERENCE_PROFILE_ARN")
            )
            response = custom_llm._call(prompt)
            # Parse response as needed
            result = {"query": response}
        
        # Print and return the query
        print(result["query"])
        return {"query": result["query"]}
        
    except Exception as e:
        print(f"Error in query generation: {e}")
        return {"query": ""}

# Function to execute SPARQL query against HANA database
def execute_sparql(query_response):
    print()  # Print empty line for spacing
    
    # Create database cursor
    cursor = conn.cursor()
    
    try:
        # Execute SPARQL stored procedure
        resp = cursor.callproc('SPARQL_EXECUTE', (
            query_response["query"],  # The SPARQL query
            'Metadata headers describing Input and/or Output',  # Description
            '?',  # Output placeholder
            None  # Additional options
        ))

        # Process response if available
        if resp:
            # Extract metadata and results
            metadata_headers = resp[3]  # Response metadata
            query_response = resp[2]    # Actual query results
            
            # Print results
            print("Query Response:", query_response)
            print("Response Metadata:", metadata_headers)
            return query_response
        else:
            print("No response received from stored procedure.")

    except Exception as e:
        print("Error executing stored procedure:", e)
    finally:
        # Ensure cursor is closed
        cursor.close()

# Function to summarize query results into natural language
def summarize_info(question, query_response):
    # Define prompt template for summarization
    prompt = """Answer the user question below given the following relational information in XML format. Use as much as the query response as possible to give a full, detailed explanation. Interpret the URI and predicate information using context. Don't use phrases like 'the entity identified by the URI,' just say what the entity is.
    Also make sure the output is readable in a format that can be display through an HTML file, add appropriate formatting.
    Please remove unnecessary information. Do not add information about the triples. Do not add the source of the data.
    Do not include details about what they are identified as or what kind of entity they are unless asked. Do not add any suggestions unless explicitly asked. Simply give a crisp and direct answer to what has been asked!
    If you do not have an answer, please say so. DO NOT HALLUCINATE!
    User Question: {question}
    Information: {information}
    """    
    # Create prompt template
    summarize = PromptTemplate.from_template(prompt)
    
    # Format the prompt with question and results
    prompt_input = summarize.invoke({
        "question": question,
        "information": query_response
    })

    # Define output type for summarization
    class QuestionAnswer(TypedDict):
        """Generated answer."""
        final_answer: Annotated[str, ..., "Answer to user's question."]

    # CHANGE 6: Modified to handle both ChatBedrock and custom implementation
    try:
        if anthropic:
            # Configure LLM for structured output
            translate_llm = anthropic.with_structured_output(QuestionAnswer)
            final_answer = translate_llm.invoke(prompt_input)
        else:
            # Fallback to custom implementation
            custom_llm = CustomBedrockLLM(
                model_id=os.getenv("MODEL_ID"),
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                aws_region_name=AWS_DEFAULT_REGION,
                inference_profile_arn=os.getenv("INFERENCE_PROFILE_ARN")
            )
            response = custom_llm._call(prompt_input)
            final_answer = {"final_answer": response}
        
        # Print and return the answer
        print(final_answer["final_answer"])
        return final_answer["final_answer"]
    except Exception as e:
        print(f"Error in summarization: {e}")

def process_workflow(question):
    sparql = write_query({"question": question})  # Generate SPARQL query
    response = execute_sparql(sparql)  # Execute query
    return summarize_info(question, response)  # Generate and print answer

# Main execution flow
# question = "What are Hdbkpic?"  # The question to answer
# process_workflow(question)  # Run the workflow to get the answer