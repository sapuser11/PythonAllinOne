import streamlit as st
import middleware

st.title("Restaurant Name and Menu Generator")

cuisine = st.sidebar.selectbox("Select Cuisine", ["Italian", "Chinese", "Indian", "Mexican", "Arabic"])

if cuisine:
    response = middleware.generate_restaurant_name_and_menu(cuisine)
    st.header("Restaurant Name:")
    st.write(response.get("restaurant_name"))
    st.write("**Menu Items**")
    menu_items = response.get("menu", "").split(",")
    for item in menu_items:
        st.write(f"- {item.strip()}")
else:
    st.warning("Please enter a cuisine type.")
