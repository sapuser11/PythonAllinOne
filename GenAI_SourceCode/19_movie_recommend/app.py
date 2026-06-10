import streamlit as st
import requests
import json

st.title('ATS Movie Recommendation System')

# User input
user_query = st.text_input('What kind of movie do you want to watch?', 'i want to watch fresh detective movie')

if st.button('Get Recommendations'):
    # Prepare the request payload
    payload = {
        "query": user_query
    }
    
    # Make API call
    try:
        response = requests.post('http://localhost:8000/recommend', json=payload)
        #response = requests.post('https://ats-movie-recommend-noisy-serval-ik.cfapps.us10-001.hana.ondemand.com/recommend', json=payload)
        data = response.json()
        
        # Check if recommendations are available
        if 'recommendations' in data and data['recommendations']:
            st.subheader('Recommended Movies:')
            
            # Display movies in a grid (3 columns)
            cols = st.columns(3)
            
            for i, movie in enumerate(data['recommendations']):
                with cols[i % 3]:
                    st.image(movie['image'], caption=movie['name'], width=200)
                    st.write(f"**{movie['name']}**")
                    st.write(f"ID: {movie['id']}")
                    st.write("---")
        else:
            st.error('No recommendations found.')
    except Exception as e:
        st.error(f'Error: {str(e)}')