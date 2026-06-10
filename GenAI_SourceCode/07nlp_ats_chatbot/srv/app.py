import os
from fastapi import FastAPI
import nltk
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
import pandas as pd

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

class AnubhavTrainingBot:
    def getDataFrame(self, file_path):
        try:
            df = pd.read_excel(file_path)
            df = df.dropna(subset=['Question', 'Answer'])
            df = df.reset_index(drop=True)
            return df
        except Exception as e:
            print(f"Error reading the CSV file: {e}")
            return pd.DataFrame(columns=['Question', 'Answer'])

    def process_question(self, user_input, dataframe):
        ##For simplicity, we will just echo back the question
        print(f"You asked {user_input}")
        ##get all the questions in the list
        questions = dataframe['Question'].tolist()
        #print(f"Questions in the dataset: {questions}")
        ##Add user's question as first line
        questions.append(user_input)
        ##Calculate TFIDF for whole data which has my question also
        vectorizer = TfidfVectorizer(tokenizer=word_tokenize, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(questions)
        ##print the matrix
        print(tfidf_matrix.toarray())
        ##Cosine Similarity
        try:
            cosine_sim = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            cosine_sim = None

        ##Index of the line no of the record which is most similar
        most_similar_idx = cosine_sim.argmax()
        #print(f"Most similar question index: {most_similar_idx}")

        ##Remove the question from dataset
        questions.pop()

        ##Return the answer
        answer = dataframe.iloc[most_similar_idx]['Answer']
        print(f"Answer: {answer}")

        ##return the matrix
        return answer
    
class InputQuestion(BaseModel):
    input: dict

app = FastAPI()
bot = AnubhavTrainingBot()

@app.post("/ask")
def ask_question(input_question: InputQuestion):
    user_input = input_question.input.get("question", "")
    print(f"User input: {user_input}")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "anubhav_trainings.xlsx")
    dataframe = bot.getDataFrame(file_path)
    answer = bot.process_question(user_input, dataframe)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)