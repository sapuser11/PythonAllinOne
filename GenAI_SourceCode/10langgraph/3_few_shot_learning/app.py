from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
from langserve import add_routes
from openai import BaseModel
import streamlit as st
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

##Few shot learning examples to use my DB tables starring with ZATS
examples = [
    {
        "input": "give me all sales orders created today with order id, material (items) and price",
        "output": "SELECT VBELN, MATNE, NETWR FROM ZATS_SALES_ORDERS WHERE ERDAT = '20250824'"
    },
    {
        "input": "get me the total number of purchase orders in my sap system",
        "output": "SELECT COUNT(*) FROM ZATS_PURCHASE_ORDERS WHERE EKKO.BEDAT = '20250824'"
    },
    {
        "input": "what are all the total value in epm sales tables",
        "output": "SELECT SUM(gross_amount) as total_gross_amount FROM SNWD_SO"
    },
    {
        "input": "find all the flight bookings in S/4hana system for American Airlines 'AA'",
        "output": "SELECT count(*) as all_bookings FROM /dmo/bookings WHERE CARRID = 'AA'"
    },
    {
        "input": "join my sales and customer data to get total sales per customer",
        "output": "SELECT CUST, SUM(AMOUNT) as TotalAmount FROM ZATS_CUSTOMER INNER JOIN ZATS_SALES_ORDERS ON ZATS_CUSTOMER.CUST = ZATS_SALES_ORDERS.CUST GROUP BY CUST"
    }
]


# system_prompt = "generate programming code in following {language} language"
prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="{input}\n{output}"
)

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=prompt,
    suffix="{my_input}",
    input_variables=["my_input"]
)

##Create object of chatgpt llm
llm = ChatOpenAI(model_name="gpt-4.1-mini", max_tokens=1024)
stringParser=StrOutputParser()

##Create chain object
chain = few_shot_prompt | llm | stringParser

##Pass my Question
myprompt = few_shot_prompt.format(my_input="list all count of sales orders in anubhav training s4 system")

# myprompt = few_shot_prompt.format(my_input="who was the president back then")

response = llm.invoke(myprompt)
print(response.content)