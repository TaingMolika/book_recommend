import pandas as pd
import requests
import json
import streamlit as st

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import deepseek_api

@st.cache_data
def load_data():
    return pd.read_csv('raw_data.csv')

books_df = load_data()

def call_deepseek(user_query, books_df):
    books = books_df[['Title', 'Description', 'Price', 'Availability', 'Rating', 'Product Link']].to_dict(orient='records')
    
    books_text = ""
    for book in books[:30]:  # Limit to 30 books to control prompt size
        books_text += (
            f"- Title: {book['Title']}\n"
            f"  Description: {book['Description']}\n"
            f"  Price: {book['Price']}\n"
            f"  Availability: {book['Availability']}\n"
            f"  Rating: {book['Rating']}\n"
            f"  Link: {book['Product Link']}\n\n"
        )

    messages = [
        {
            "role": "system",
            "content": "You are a helpful book recommendation assistant. Only recommend books from the following list:\n" + books_text
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": deepseek_api,
            "Content-Type": "application/json",
            # "HTTP-Referer": "https://yourwebsite.com",  # optional
            # "X-Title": "YourSiteName",  # optional
        },
        data=json.dumps({
            "model": "deepseek/deepseek-r1-0528:free",
            "messages": messages
        })
    )

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.text}"

st.title("📚 AI Book Recommendation Chatbot")

user_query = st.text_input("Ask for a book recommendation:")

if st.button("Ask"):
    if user_query:
        with st.spinner('Thinking...'):
            response = call_deepseek(user_query, books_df)
        st.write(response)
