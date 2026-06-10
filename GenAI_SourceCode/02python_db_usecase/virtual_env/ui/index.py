import streamlit as st
from db import init_db as dbcon
import invoice_generator as invgen

st.title("Welcome to Anubhav Trainings")

##a variable to store courses selected
if "selected_courses" not in st.session_state:
    st.session_state.selected_courses = []



##connect to database - better coding we can add cache
@st.cache_resource
def get_db_connection():
    #connect to the database and create a table if it doesn't exist
    reuseconn = dbcon.main()
    dbcon.create_table_anubhav(reuseconn)
    training_courses_data = {
        "UI5" : {"trainer": "Anubhav", "hours": 40, "price": 380},
        "CPI" : {"trainer": "Anurag", "hours": 35, "price": 400},
        "AOH" : {"trainer": "Anubhav", "hours": 40, "price": 400},
        "CDS" : {"trainer": "Ananya", "hours": 50, "price": 480},
        "BTP" : {"trainer": "Saurabh", "hours": 30, "price": 580},
        "SAC" : {"trainer": "Rohan", "hours": 45, "price": 300},
        "CAPM" : {"trainer": "Sonia", "hours": 60, "price": 900},
        "RAP" : {"trainer": "Anubhav", "hours": 40, "price": 850}
    }
    #load sample data into the database
    dbcon.execute_dml(reuseconn, training_courses_data)
    return reuseconn

def print_order_details():
    if st.session_state.selected_courses:
        for course in st.session_state.selected_courses:
            st.write(f"Course: {course[1]}, Trainer: {course[2]}, Price: {course[3]} USD, Duration: {course[4]} hours")
    else:
        st.write("No courses selected.")


myconn = get_db_connection()

##add a form which contains fields and buttons
with st.form("Select Courses"):
    st.subheader("Choose your favourite courses from Anubhav trainings")
    course_name = st.text_input("Enter module you want to learn", placeholder="UI5, CPI, AOH, CDS, BTP, SAC, CAPM, RAP")
    learn = st.form_submit_button("👍 Lets go")
    order = st.form_submit_button("🛒 Order Now")

    if learn:
        my_query = f"SELECT * FROM public.anubhav_training WHERE course_name = upper('{course_name}');"
        data = dbcon.execute_dql(myconn, my_query)
        if data:
            course = data[0]
            st.session_state.selected_courses.append(course)
            st.success(f"✅ You have selected {course[1]} with trainer {course[2]} for {course[3]} USD and duration of {course[4]} hours.")
        else:
            st.error("❌ Course not found. Please check the name and try again.")

    if order:
        if st.session_state.selected_courses:
            st.subheader("Your Selected Courses:")
            print_order_details()
            invgen.generate_invoice(st.session_state.selected_courses, "demo.pdf")
            st.success("🛒 Your order has been placed successfully!")
        else:
            st.error("❌ No courses selected. Please select a course before ordering.")

# num = st.number_input("Enter a number")

# if st.button("Wallah"):
#     if num > 5:
#         st.success(f"✅ the {num} is above 5")
#     else:
#         st.error(f"❌ the {num} is below 5")
