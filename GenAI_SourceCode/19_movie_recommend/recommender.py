import pandas as pd
from dotenv import load_dotenv
import os 

#langchain
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

##loading enviornment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

#load data
data = pd.read_csv('./movies.csv')
print(data.head())

# Create new column called tagged_description which combines the id, title and description columns
data['tagged_description'] = data[['id', 'name', 'country', 'type', 'description']].astype(str).agg(' | '.join, axis=1)
print(data.head())

# Save the tagged_description column to a text file
data['tagged_description'].to_csv('tagged_descriptions.txt', index=False, header=False, encoding='utf-8')

# Load the text file
loader = TextLoader('tagged_descriptions.txt', encoding='utf-8')
documents = loader.load()

# IMPORTANT: Reduce chunk size to prevent token limit issues
text_splitter = CharacterTextSplitter(
    chunk_size=500,  # Reduced from 1000
    chunk_overlap=50,  # Reduced overlap
    separator="\n"  # Split by newline to keep movie entries together
)
chunks = text_splitter.split_documents(documents)

# print(f"Number of chunks created: {len(chunks)}")
# print(f"Sample chunk: {chunks[0].page_content[:200] if chunks else 'No chunks'}")

# Create embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Create a vector store
vector_store = Chroma.from_documents(chunks, embeddings)

# Create a retriever - REDUCED k to limit context size
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 8}  # Reduced from 10 to stay under token limit
)

# Test the retriever
test_query = "science fiction space"
test_results = retriever.get_relevant_documents(test_query)

# Create prompt template
prompt_template = """You are an expert movie recommendation engine. Based on the user's preferences, recommend AT LEAST 5 different movies from the provided context.

INSTRUCTIONS:
- Recommend exactly 5 movies that best match the user's request
- Rank them from most relevant to least relevant
- If fewer than 5 perfect matches exist, include similar movies that might interest the user
- Each movie entry in the context is formatted as: ID | Title | Description

MOVIE DATABASE:
{context}

USER REQUEST: {query}

Provide your 5 recommendations as comma separated values in the below text format:
[ID],[ID],[ID],[ID],[ID]
"""

prompt = PromptTemplate(
    template=prompt_template, 
    input_variables=["context", "query"]
)

# Create LLM
llm = ChatOpenAI(
    temperature=0.3, 
    model_name=OPENAI_MODEL, 
    openai_api_key=OPENAI_API_KEY,
    max_tokens=1500
)

# Modern LangChain approach using LCEL (LangChain Expression Language)
chain = prompt | llm | StrOutputParser()

# Custom function with modern invoke
def get_movie_recommendation(user_input):
    # Get relevant documents
    relevant_docs = retriever.get_relevant_documents(user_input)
    
    # Combine document contents with truncation
    context_parts = []
    total_chars = 0
    max_chars = 10000  # Limit to approximately 2500-3000 tokens
    
    for doc in relevant_docs:
        if total_chars + len(doc.page_content) < max_chars:
            context_parts.append(doc.page_content)
            total_chars += len(doc.page_content)
        else:
            break
    
    context = "\n\n".join(context_parts)
    
    print(f"\nContext size: {len(context)} characters (approx {len(context)//4} tokens)")
    
    try:
        # Use invoke with the modern chain
        response = chain.invoke({
            "context": context,
            "query": user_input
        })

        print(f"LLM Response: {response}")
        
        # Parse the response to extract movie IDs
        movie_ids = []
        if response and ',' in response:
            # Clean up the response and extract IDs
            cleaned_response = response.replace('[', '').replace(']', '').strip()
            movie_ids = [id.strip() for id in cleaned_response.split(',')]
            # Ensure we have at most 5 IDs
            movie_ids = movie_ids[:5]

        # Prepare the result
        if movie_ids:
            # Extract movie details from the dataframe
            recommended_movies = []
            for movie_id in movie_ids:
                # Find the movie in the dataframe
                movie = data[data['id'] == movie_id]
                if not movie.empty:
                    recommended_movies.append({
                        'id': movie_id,
                        'name': movie['name'].values[0],
                        'image': movie['image'].values[0] if 'image' in movie.columns else ''
                    })
            
            return {
                'result': recommended_movies
            }
        else:
            return {
                'result': "Could not parse movie recommendations. Please try again."
            }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'result': f"Error generating recommendations: {str(e)}"
        }

# Example usage
if __name__ == "__main__":
    #user_input = "I want to watch a science fiction movie with space exploration."
    user_input = "I want to watch a an indian series with college life and drama."
    recommendation = get_movie_recommendation(user_input)
    
    print("\n" + "="*70)
    print("MOVIE RECOMMENDATIONS:")
    print("="*70)
    print(recommendation['result'])
    
    