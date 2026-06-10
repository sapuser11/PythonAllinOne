import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from dotenv import load_dotenv
from groq import Groq
from langchain_groq import ChatGroq

##Load Enviornment variable for API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# CLAUD_API_KEY = os.getenv("CLAUD_API_KEY")

##if condition to choose particular llm
if GROQ_API_KEY:
    llm = ChatGroq(api_key=GROQ_API_KEY, temperature=0.7, 
                   model="llama-3.3-70b-versatile")
# elif OPENAI_API_KEY:
#     llm = openai.ChatCompletion(api_key=OPENAI_API_KEY)
# elif CLAUD_API_KEY:
#     llm = Claude(api_key=CLAUD_API_KEY)
else:
    llm = None


def generate_restaurant_name_and_menu(cuisine):
    ##Chain 1: Generate Restaurant Name
    prompt_template_name = PromptTemplate(
        input_variables=["cuisine"],
        template="Generate a name for a {cuisine} restaurant with exact ONE name."
    )
    chain_1 = LLMChain(llm=llm, prompt=prompt_template_name, output_key="restaurant_name")

    ##Chain 2: Generate Restaurant Menu
    prompt_template_menu = PromptTemplate(
        input_variables=["restaurant_name"],
        template="Generate a menu for a {restaurant_name} restaurant. Return it as comma separated string."
    )
    chain_2 = LLMChain(llm=llm, prompt=prompt_template_menu, output_key="menu")

    ##Sequential Chain
    final_chain = SequentialChain(chains=[chain_1, chain_2],
                                  input_variables=["cuisine"],
                                  output_variables=["restaurant_name", "menu"]
                                  )

    response = final_chain({'cuisine': cuisine})
    return response

if __name__ == "__main__":
    cuisine = "Italian"
    print(generate_restaurant_name_and_menu(cuisine))