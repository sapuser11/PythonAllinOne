from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from langchain.memory import ConversationBufferMemory
import logging
import pandas as pd
import hana_ml
from hana_ml import dataframe
from cfenv import AppEnv
from hdbcli import dbapi
from datetime import datetime

##1. Load Environment Variables
load_dotenv()
##2. Load Cloud Foundry Environment Variables
env = AppEnv()

##3. Prepare Logging
FORMAT = "%(asctime)s:%(name)s:%(levelname)s - %(message)s"
# Use filename="file.log" as a param to logging to log to a file
logging.basicConfig(format=FORMAT, level=logging.INFO)

# Check if running locally or in Cloud Foundry
if env.name is None:
    ##4. Set Environment variables - locally
    os.environ["AICORE_HOME"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/profiles"
    os.environ["AICORE_PROFILE"] = "anubhav"
    os.environ["HANA_HOST"] = os.getenv("db_host")
    os.environ["HANA_PORT"] = os.getenv("db_port")
    os.environ["HANA_USER"] = os.getenv("db_user")
    os.environ["HANA_PASSWORD"] = os.getenv("db_password")

    #5. Running locally - use environment variables
    print("Running locally - using environment variables")
    hana = {
        'credentials': {
            'host': os.getenv("db_host"),
            'port': os.getenv("db_port"),
            'user': os.getenv("db_user"),
            'password': os.getenv("db_password"),
            'certificate': os.getenv("HANA_CERTIFICATE", None)  # Optional for local
        }
    }
    
    # Validate required environment variables
    required_vars = ['HANA_HOST', 'HANA_USER', 'HANA_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logging.error(f"Missing required environment variables: {missing_vars}")
        hana = None
    else:
        logging.info(f"Local HANA connection configured for host: {hana['credentials']['host']}")
        
else:
    ##4. HANA Service Configuration
    hana_service = 'hana'

    # Running in Cloud Foundry - use bound service
    print("Running in Cloud Foundry - using bound service")
    hana = env.get_service(label=hana_service)
    
    if hana is None:
        logging.error(f"HANA service '{hana_service}' not found in Cloud Foundry")
    else:
        logging.info(f"Cloud Foundry HANA service found: {hana_service}")

#hana = env.get_service(label=hana_service)


class issue_reporting_app():
    
    def __init__(self, input_message) -> None:

        self.info_dict={
            "category": 
            '''Classify the post in one of the following categories: \"PUBLIC CLEANLINESS\", \"ROADS & FOOTPATHS\", \
            \"FACILITY & PARK MAINTENANCE\", \"PESTS\", \"DRAINS & SEWERS\".
            If none of the categories fits, return \"OTHER\".''',                 

            "priority": 
            '''Identify the priority to be given to the reported issues into \"4-Low\", \"3-Medium\", \"2-High\", \"1-Very High\". .
                4-Low : the issue does not pose any problem with public safety and does not necessarily need to be handled urgently. 
                3-Medium : the issue does not cause any immediate danger, but it has significant and negative impact on the daily life of people in the neighborhood.
                2-High : the issue needs to be resolved quickly because it can potentially cause dangerous situations or disruptions. 
                1-Very High : the issue needs to be handled as soon as possible, as it is a matter of public safety. 
                ''',          

            "summary": 
            "Summarize the reported issue in 40 characters and a neutral tone.",

            "description": 
            "Summarize the reported issue in not more that 300 characters and a neutral tone.",

            "address":
            "Extract the address where the issue is taking place. Return the street only and omit the town or country",

            "location": 
            "Extract the coordinates where the issue has been notices. The format should be: float, float",

            "sentiment" : 
            '''Classify the sentiment of the post into \"NEUTRAL\", \"NEGATIVE\", \"VERY NEGATIVE\"
            1. NEUTRAL: if the post reports an issue politely, in a calm tone
            2. NEGATIVE: if the post shows irony, impatience, annoyance
            3. VERY NEGATIVE: the post is rude or it expresses rage, hatred towards the public authority
            '''
        }

        self.template_string = ''' Extract information from the social media post delimited by triple backticks.
            ```{post}``` 
            '''

        self.functions = [
            {
                "name": "post_analysis",
                "summary": "Extract information from the social media post",
                "parameters": {
                    "type": "object",
                    "properties": {

                        "category": {"type": "string", "description": self.info_dict["category"], 
                                     "enum":['PUBLIC CLEANLINESS','ROADS & FOOTPATHS','FACILITY & PARK MAINTENANCE',
                                             'PESTS', 'DRAINS & SEWERS','OTHER']},
                        "priority": {"type": "string", "description": self.info_dict["priority"], 
                                     "enum": ['4-Low','3-Medium', '2-High', '1-Very High'] },
                        "summary": {"type": "string", "description": self.info_dict["summary"]},
                        "description": {"type": "string", "description": self.info_dict["description"]},
                        "address": {"type": "string", "description": self.info_dict["address"]},
                        "location": {"type": "string", "description": self.info_dict["location"]},
                        "sentiment": {"type": "string", "description": self.info_dict["sentiment"],
                                      "enum": ['NEUTRAL','NEGATIVE', 'VERY NEGATIVE']},
                    },
                    "required": ["category", "priority"],
                },
            }
        ]

        
        dep_id = os.getenv("LLM_DEPLOYMENT_ID")
        print("deployment id : ", dep_id)
        if dep_id is None:
            dep_id = "dd43d1107ac0d426"
            
        proxy_client = get_proxy_client('gen-ai-hub')

        self.model = ChatOpenAI(proxy_model_name='gpt-35-turbo', proxy_client=proxy_client, deployment_id=dep_id)
        self.input_message = input_message
        self.message = """Before January 2025, getting to the office was a quick 25-minute drive for 6 km for me. 
        Now it’s at least 40 minutes. What’s going on with Bengaluru traffic? Did everyone suddenly decide to make 
        “going to the office” their New Year’s resolution, or have companies started dragging people back in?"""
        self.redditPostId = input_message["id"]
        self.author = input_message["author"]
        self.postingDate = input_message["postingDate"]
        self.response = None
        self.output = None
        self.last_issue_id = 0
        self.conn = None
        self.conn_context = None


    def get_uuid(self) -> str:
        """
        Generate a UUID using SAP HANA's SYSUUID() function.
        
        Returns:
            str: A UUID string generated by SAP HANA
            
        Raises:
            Exception: If database connection fails or query execution fails
        """
        try:
            # Ensure database connection is established
            if self.conn is None:
                self.set_db_connection()
                
            connection = self.conn
            cursor = connection.cursor()
            
            # Execute the SYSUUID() query
            cursor.execute("SELECT TO_NVARCHAR(SYSUUID) AS UUID FROM DUMMY")
            
            # Fetch the single result
            result = cursor.fetchone()
            
            # Close the cursor (connection stays open for reuse)
            cursor.close()
            
            # Return the UUID string
            if result:
                return result["UUID"]
            else:
                raise Exception("No UUID generated")
                
        except Exception as e:
            logging.error(f"Error generating UUID: {str(e)}")
            raise e
    
    def set_db_connection(self) -> None:

        if hana is not None:

            # Handle different data structures for local vs Cloud Foundry
            if env.name is None:  # Local environment - hana is a dict
                dbHost = hana['credentials']['host']
                dbPort = hana['credentials']['port']
                dbUser = hana['credentials']['user']
                dbPwd = hana['credentials']['password']
                ssl_cert = ""
            else:  # Cloud Foundry environment - hana is a service object
                dbHost = hana.credentials['host']
                dbPort = hana.credentials['port']
                dbUser = hana.credentials['user']
                dbPwd = hana.credentials['password']
                ssl_cert = hana.credentials['certificate']

            self.conn = dbapi.connect(
                address = dbHost,
                port = dbPort,
                user = dbUser,
                password = dbPwd,
                encrypt = 'true',
                sslTrustStore = ssl_cert
                )

            self.conn_context = hana_ml.dataframe.ConnectionContext(
                dbHost,
                dbPort,
                dbUser,
                dbPwd, 
                encrypt='true',
                sslValidateCertificate='false'
                )


    def hello(self):

        if hana is None:
            return "Can't connect to HANA service '{}' – check service name?".format(hana_service)
        else:
            self.set_db_connection()
            connection = self.conn
        cursor = connection.cursor()
        cursor.execute("select CURRENT_UTCTIMESTAMP from DUMMY")
        ro = cursor.fetchone()
        cursor.close()
        connection.close()

        return "Current time is: " + str(ro["CURRENT_UTCTIMESTAMP"])
    

    def ask_llm(self) -> None:

        post_prompt= ChatPromptTemplate.from_template(self.template_string)
        print(self.message)
        chain = (
            post_prompt
            | self.model.bind(function_call={"name": "post_analysis"}, functions=self.functions)
            | JsonOutputFunctionsParser()
        )

        response = chain.invoke({"post": self.message})
        print(response)
        self.response = response
        # self.response = {'category': 'ROADS & FOOTPATHS', 'priority': '3-Medium', 'summary': 'Traffic congestion in Bengaluru', 'description': 'The traffic congestion in Bengaluru has increased significantly, causing longer commute times for short distances. The situation has become a concern for many commuters, impacting their daily routines and productivity. It is important to address this issue to ensure smoother traffic flow and improved commuting experience for everyone.', 'address': 'Bengaluru', 'location': '12.9629, 77.5775', 'sentiment': 'NEGATIVE'}
        
    
    def prepare_content(self) -> None:
        self.message = "redditPostId: " + self.input_message["id"]+\
            ", author: "+self.input_message["author"]+", title: "+self.input_message["title"]+\
            ", message: "+self.input_message["longText"]+", postingDate: "+self.input_message["postingDate"]


    def prepare_output(self) -> None:
        output = pd.DataFrame(self.response, index=[0])
        output = output.rename(columns={
            'sentiment': 'SENTIMENT', 'location': 'LOCATION',\
            'summary': 'GENAISUMMARY', 'description': 'GENAIDESCRIPTION',\
            'priority': 'PRIORITY', 'category': 'CATEGORY'
        })

        output[['LAT', 'LONG']] = output['LOCATION'].str.split(',', n=1, expand=True).astype(float)
        posting_date = datetime.strptime(self.postingDate, '%Y-%m-%dT%H:%M:%S.%fZ')

        new_id = self.get_uuid()
        output = output.assign(ID = new_id, PROCESSOR = '', PROCESSDATE = '', PROCESSTIME = '',\
                               DECISION = '', PRIORITYDESC = '', MAINTENANCENOTIFICATIONID = '',\
                               REDDITPOSTID = self.redditPostId, REPORTEDBY = self.author,\
                               DATE = posting_date.date(), TIME = posting_date.time()
                               )
        output['DATE'] = pd.to_datetime(output['DATE'], format='%Y-%m-%d')
        output['TIME'] = pd.to_datetime(output['TIME'], format="%H:%M:%S").dt.time
        output = output.drop('LOCATION', axis=1)
        output = output[[
            "ID",
            "PROCESSOR",
            "PROCESSDATE",
            "PROCESSTIME",
            "REPORTEDBY",
            "DECISION",
            "REDDITPOSTID",
            "MAINTENANCENOTIFICATIONID",
            "LAT",
            "LONG",
            "GENAISUMMARY",
            "GENAIDESCRIPTION",
            "PRIORITY",
            "PRIORITYDESC",
            "SENTIMENT",
            "CATEGORY",
            "DATE",
            "TIME"]]
        print(output)
        self.output = output


    def write_table_to_hana(self, df, table_name, schema) -> None:
        #print(df)
        
        df_remote = dataframe.create_dataframe_from_pandas(
            connection_context = self.conn_context,
            schema = schema,
            pandas_df = df,
            table_name = table_name,
            force = True,
            replace = False,
            append = True,
            drop_exist_tab = True
        )
        
    ##New function which inserts the data into the db instead of create table again
        # Instead of your current approach, use this:
    def insert_dataframe_to_hana(self, df, schema, table_name):
        full_table_name = f'"{schema}"."{table_name}"'
        columns_str = ', '.join([f'"{col}"' for col in df.columns])
        
        for _, row in df.iterrows():
            values = []
            for value in row:
                if pd.isna(value):
                    values.append('NULL')
                elif isinstance(value, str):
                    values.append(f"'{value.replace(chr(39), chr(39)+chr(39))}'")
                else:
                    values.append(f"'{value}'")
            
        values_str = ', '.join(values)
        sql = f"INSERT INTO {full_table_name} ({columns_str}) VALUES ({values_str})"
        print(sql)
        self.conn_context.sql(sql)
        self.conn_context.connection.commit()

    def run_workflow(self):
        self.prepare_content()
        self.ask_llm()
        self.set_db_connection()
        self.prepare_output()
        #self.write_table_to_hana(self.output, "CUST_TICKETS", "DBADMIN")
        self.insert_dataframe_to_hana(self.output, 
                                      "USR_BI8PJTQYTZWPXDX4DCBIVKJXO",
                                      "CUST_TICKETS"
                                         )
        return self.response


if __name__ == '__main__':
    # Create a sample input message
    input_message = {
        "id": "rdt-223536658",
        "author": "sanjay singh",
        "title": "worst place to drive car",
        "longText": """Before January 2025, getting to the office was a quick 25-minute drive for 6 km for me. Now it’s at least 40 minutes. What’s going on with Bengaluru traffic? Did everyone suddenly decide to make 
        “going to the office” their New Year’s resolution, or have companies started dragging people back in?
        12.9629° N, 77.5775° E""",
        "postingDate": "2024-01-01T00:00:00.000Z"
    }
    app = issue_reporting_app(input_message)
    app.run_workflow()