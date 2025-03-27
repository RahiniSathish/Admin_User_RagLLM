import streamlit as st
import requests

SERVER = "http://localhost:8000"
st.title("Chat with Knowledge Base")
if "token" not in st.session_state:
    st.session_state.token = None
with st.sidebar:
    st.markdown("Login or Register")
    choice = st.radio("Select", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submit = st.button("Submit")

    if submit:
        endpoint = "/login" if choice == "Login" else "/register"
        payload = {"email": email, "password": password}
        try:
            r = requests.post(SERVER + endpoint, json=payload)
            if r.status_code == 200:
                data = r.json()
                if "access_token" in data:
                    st.session_state.token = data["access_token"]
                    st.success("Logged in successfully!")
                else:
                    st.success(data.get("message", "Registered. Waiting for admin approval."))
            else:
                try:
                    error_data = r.json()
                    st.error(f" {error_data.get('detail', 'Something went wrong')}")
                    st.text(f"Full response: {r.text}")
                except Exception:
                    st.error("Failed to decode backend response.")
                    st.text(f" Raw response: {r.text}")
        except Exception as e:
            st.error(f"Network error: {e}")


if st.session_state.token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    st.success("Access granted")
    
    r = requests.get(f"{SERVER}/me", headers=headers)
    if r.status_code == 200:
        role = r.json().get("role")
        st.sidebar.markdown(f"**Role:** {role}")


        
        if role == "Admin":
            st.markdown("Admin Dashboard")

            st.markdown("Approve a User")
            email_to_approve = st.text_input("Email to approve")
            role_to_assign = st.selectbox("Assign Role", ["Admin", "User"])
            if st.button("Approve User"):
                approve_resp = requests.post(f"{SERVER}/admin/approve", params={
                    "email": email_to_approve,
                    "role_name": role_to_assign
                }, headers=headers)
                if approve_resp.status_code == 200:
                    st.success(approve_resp.json().get("message"))
                else:
                    st.error(approve_resp.json().get("detail", "Approval failed"))

            st.markdown("Delete a User")
            email_to_delete = st.text_input("Email to delete")
            if st.button("Delete User"):
                delete_resp = requests.delete(f"{SERVER}/admin/delete-user", params={"email": email_to_delete}, headers=headers)
                if delete_resp.status_code == 200:
                    st.success(delete_resp.json().get("message"))
                else:
                    st.error(delete_resp.json().get("detail", "Deletion failed"))

        else:
            st.info(f" You are logged in as: `{role}` — limited access.")

        
        file = st.file_uploader("Upload a document")
        if file and st.button("Upload"):
            try:
                r = requests.post(f"{SERVER}/upload", headers=headers, files={"file": (file.name, file.getvalue())})
                st.write(r.json())
            except Exception as e:
                st.error(f"Upload failed: {e}")

        
        question = st.text_input("Ask a question")
        if st.button("Ask"):
            try:
                r = requests.get(f"{SERVER}/query", headers=headers, params={"q": question})
                if r.status_code == 200:
                    st.write(r.json()["answer"])
                else:
                    st.error(r.json().get("detail", "Query failed"))
            except Exception as e:
                st.error(f" Query error: {e}")
