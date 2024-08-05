
import streamlit as st
import requests

BASE_URL = "http://api:8000"  

def login_user(username, password):
    response = requests.get(
        f"{BASE_URL}/user",
        params={"name": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()
    else:
        return None

def create_todo(token, content):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/todos/",
        json={"content": content},
        headers=headers,
    )
    return response.status_code

def delete_todo(token, todo_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/todos/{todo_id}/",
        headers=headers,
    )
    return response.status_code

def list_todos(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/todos/",
        headers=headers,
    )
    if response.status_code == 200:
        return response.json()
    else:
        return None

def main():
    st.title("My Todo App")

    # Login Form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.success(f"Logged in as {user['name']}")
            st.session_state.token = user['name']
        else:
            st.error("Invalid credentials")

    # Todo Operations
    if "token" in st.session_state:
        st.subheader("Add a new Todo")
        content = st.text_input("Content")
        if st.button("Add Todo"):
            status_code = create_todo(st.session_state.token, content)
            if status_code == 200:
                st.success("Todo added successfully")
            else:
                st.error("Failed to add Todo")

        st.subheader("Your Todos")
        todos = list_todos(st.session_state.token)
        if todos:
            for todo in todos:
                st.write(f"ID: {todo['id']} - Content: {todo['content']}")
                if st.button(f"Delete {todo['id']}"):
                    delete_status = delete_todo(st.session_state.token, todo['id'])
                    if delete_status == 200:
                        st.success("Todo deleted successfully")
                    else:
                        st.error("Failed to delete Todo")
        else:
            st.info("No todos available.")

if __name__ == "__main__":
    main()
