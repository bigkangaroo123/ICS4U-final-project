import streamlit as st
import client_manager_db
import datetime

st.title("📂 Your Clients")

# -------------- Task Table -----------------
# 1st column: checkbox
# 2nd: task name
# 3rd: deadline
# 4th: notes

def task_table(client_name, project_name):
    st.subheader(f"📋 Task Table for {project_name} under {client_name}")

    # Add Task Button
    if st.button("Add Task"):
        task_name = st.text_input("Enter Task Name", placeholder="Task Name")
        deadline = st.date_input("Select Deadline", value=datetime.date.today())
        notes = st.text_area("Enter Notes", height=100)

        # Check if task data is filled before adding it to the database
        if task_name and deadline and notes:
            # Fetch client_id using client_name
            clients = client_manager_db.get_all_clients()
            client_id = None
            for client in clients:
                if client['client_name'] == client_name:
                    client_id = client['id']
                    break

            # Fetch project_id using project_name
            projects = client_manager_db.get_all_projects(client_id)
            project_id = None
            for project in projects:
                if project['project_name'] == project_name:
                    project_id = project['id']
                    break

            # Add task to the database
            if deadline < datetime.date.today():
                st.error("The deadline cannot be in the past.")
            else:
                client_manager_db.add_task_db(client_id, project_id, task_name, deadline, False, notes)
                st.success(f"Task '{task_name}' added to project '{project_name}' under client '{client_name}'!")
        else:
            st.error("Please fill all task details.")
    
    # Retrieve and display tasks from the database for the selected project
    tasks = client_manager_db.get_tasks_by_client_and_project(client_name, project_name)
    
    if tasks:
        for task in tasks:
            task_name = task['task_name']
            task_deadline = task['deadline']
            task_notes = task['notes']
            task_complete = task['complete']
            task_id = task['id']  # Get the task ID for deleting

            columns = st.columns([0.5, 3, 3, 4, 1])

            task_complete = columns[0].checkbox("", value=task_complete)

            task_deadline = columns[1].date_input("Deadline", value=task_deadline)
            task_name = columns[2].text_input("Task Name", value=task_name)
            task_notes = columns[3].text_area("Notes", value=task_notes, height=100)

            # Update the task completion status when checkbox is checked
            if task_complete != task['complete']:
                client_manager_db.update_task_db(task_id, task_name, task_deadline, task_complete, task_notes)

            # Delete task button
            if columns[4].button("🗑️", key=f"delete{task_id}"):
                # Handle deleting the task from the database
                client_manager_db.delete_task_db(task_id)
                st.success(f"Task '{task_name}' deleted successfully!")
                st.rerun()  # This refreshes the page

    else:
        st.info(f"No tasks found for project '{project_name}'.")

# -------------- Main Viewing Menu ----------------

selected_client = None

# Fetch clients directly from the database
clients = client_manager_db.get_all_clients()

if not clients:
    st.warning("No clients available. Add some clients first!")
else:
    client_names = [client['client_name'] for client in clients]

    # Select a client from the dropdown
    selected_client_name = st.selectbox("Select a client", client_names)

    # If a client is selected, proceed with displaying their projects and task table
    if selected_client_name:
        # Fetch selected client from the database
        selected_client = client_manager_db.get_client_by_name(selected_client_name)
        
        st.subheader(f"Client: {selected_client['client_name']}")
        st.write(f"Hourly Rate: ${selected_client['rate']}/hour")

        # Check if the selected client has projects
        projects = client_manager_db.get_all_projects(selected_client['id'])
        if not projects:
            st.info(f"No projects found for {selected_client['client_name']}.")
        else:
            # Display a dropdown with the client's projects
            selected_project = st.selectbox(f"Select a project for {selected_client['client_name']}", projects, format_func=lambda x: x['project_name'])
            # When a project is selected, display the task table
            if selected_project:
                task_table(selected_client['client_name'], selected_project['project_name'])
