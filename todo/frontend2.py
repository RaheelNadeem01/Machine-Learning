import streamlit as st
from datetime import datetime
import requests

backend_url="http://web:8000"



def load_todos():
    if 'todos' not in st.session_state:
        st.session_state['todos'] = []

def add_todo():
    todo = st.session_state['new_todo']
    due_date = st.session_state['due_date']
    due_time = st.session_state['due_time']
    if todo and due_date and due_time:
        due_datetime = datetime.combine(due_date, due_time)
        st.session_state.todos.append({'task': todo, 'due': due_datetime})
        st.session_state['new_todo'] = ''
        st.session_state['due_date'] = datetime.now().date()
        st.session_state['due_time'] = datetime.now().time()

def delete_todo(index):
    st.session_state.todos.pop(index)

def main():
    st.title("To-Do App")
    st.write("A simple to-do list application with due times")

    load_todos()

    # Input for new to-do item
    st.text_input("Add a new task:", key='new_todo')

    # Input for due date
    st.date_input("Due date:", key='due_date', value=datetime.now().date())

    # Input for due time
    st.time_input("Due time:", key='due_time', value=datetime.now().time())

    # Add task button
    st.button("Add task", on_click=add_todo)

    # Display the to-do list
    st.write("### To-Do List")
    for i, todo in enumerate(st.session_state.todos):
        col1, col2, col3 = st.columns([0.6, 0.3, 0.1])
        with col1:
            st.write(todo['task'])
        with col2:
            st.write(todo['due'].strftime('%Y-%m-%d %H:%M'))
        with col3:
            st.button("Delete", key=f"delete_{i}", on_click=delete_todo, args=(i,))

if __name__ == "__main__":
    main()
    







    import streamlit as st
from datetime import datetime

# Placeholder for user credentials
user_credentials = {'Username': 'admin123','Password': 'password1'}

def load_todos():
    if 'todos' not in st.session_state:
        st.session_state['todos'] = []

def add_todo():
    todo = st.session_state['new_todo']
    due_date = st.session_state['due_date']
    due_time = st.session_state['due_time']
    if todo and due_date and due_time:
        due_datetime = datetime.combine(due_date, due_time)
        st.session_state.todos.append({'task': todo, 'due': due_datetime})
        st.session_state['new_todo'] = ''
        st.session_state['due_date'] = datetime.now().date()
        st.session_state['due_time'] = datetime.now().time()

def delete_todo(index):
    st.session_state.todos.pop(index)

def main():
    # User login
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in user_credentials and user_credentials[username] == password:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")

    if st.session_state['logged_in']:
        st.title("To-Do App")
        st.write(f"Welcome, {st.session_state['username']}!")
        st.write("A simple to-do list application with due times")

        load_todos()

        # Input for new to-do item
        st.text_input("Add a new task:", key='new_todo')

        # Input for due date
        st.date_input("Due date:", key='due_date', value=datetime.now().date())

        # Input for due time
        st.time_input("Due time:", key='due_time', value=datetime.now().time())

        # Add task button
        st.button("Add task", on_click=add_todo)

        # Display the to-do list
        st.write("### To-Do List")
        for i, todo in enumerate(st.session_state.todos):
            col1, col2, col3 = st.columns([0.6, 0.3, 0.1])
            with col1:
                st.write(todo['task'])
            with col2:
                st.write(todo['due'].strftime('%Y-%m-%d %H:%M'))
            with col3:
                st.button("Delete", key=f"delete_{i}", on_click=delete_todo, args=(i,))

        # Logout button
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.experimental_rerun()

if __name__ == "__main__":
    main()
