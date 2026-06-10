from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.orchestration.models.content_filtering import ContentFiltering, InputFiltering, OutputFiltering
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.azure_content_filter import AzureContentFilter, AzureThreshold
from gen_ai_hub.orchestration.service import OrchestrationService
from gen_ai_hub.orchestration.exceptions import OrchestrationError

from dotenv import load_dotenv
import os
from cfenv import AppEnv

##1. Load Environment Variables
load_dotenv()
##2. Load Cloud Foundry Environment Variables
env = AppEnv()

# Check if running locally or in Cloud Foundry
if env.name is None:
    ##4. Set Environment variables - locally
    os.environ["AICORE_HOME"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/profiles"
    os.environ["AICORE_PROFILE"] = "anubhav"

class orchestration_app():
    
    def __init__(self) -> None:
 
        dep_id = os.getenv("ORCH_DEPLOYMENT_ID")
        print("deployment id : ", dep_id)
        if dep_id is None:
            dep_id = "d37a1439317adb4a"
            
        self.proxy_client = get_proxy_client('gen-ai-hub')

        # Input filtering
        input_filter=AzureContentFilter(
            hate=AzureThreshold.ALLOW_SAFE,
            violence=AzureThreshold.ALLOW_SAFE,
            sexual=AzureThreshold.ALLOW_SAFE,   
            self_harm=AzureThreshold.ALLOW_SAFE
        )
        ##output filtering
        output_filter=AzureContentFilter(
            hate=AzureThreshold.ALLOW_SAFE,
            violence=AzureThreshold.ALLOW_SAFE_LOW,
            sexual=AzureThreshold.ALLOW_SAFE,   
            self_harm=AzureThreshold.ALLOW_SAFE_LOW_MEDIUM
        )

        ##Create the configuration for orchestration service
        self.orch_config=OrchestrationConfig(
            template=Template(
                messages=[
                    SystemMessage("You are a responsible AI assistent."),
                    UserMessage("Please analyse the following post for any inappropriate content: {{?post_content}}")
                ]
            ),
            llm=LLM(name="gpt-4o"),
            filtering=ContentFiltering(
                input_filtering=InputFiltering(filters=[input_filter]),
                output_filtering=OutputFiltering(filters=[output_filter])
            )
        )

        ##Initialize the orchestration service
        self.orch_service=OrchestrationService(
            config=self.orch_config,
            deployment_id=dep_id,
            proxy_client=self.proxy_client
        )


    def ask_llm(self, user_input) -> None:
        try:
            response = self.orch_service.run(
                config=self.orch_config,
                template_values=[TemplateValue(name="post_content", value=user_input)],
            )
            print("Response: ", response.content)

        except OrchestrationError as e:
            print(f"Orchestration error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    def run_workflow(self):
        #self.ask_llm("I want to kill myself")        
        #self.ask_llm("what is a punishment for child")        
        self.ask_llm("How to spread the hate among people")        


if __name__ == '__main__':
    app = orchestration_app()
    app.run_workflow()