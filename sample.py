import streamlit as st
import pandas as pd
from auth import check_credentials, register_user  # Importing backend functions
from urllib.parse import quote_plus
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
import requests

# Function to navigate between different "pages"
def navigate_to(page):
    st.session_state.page = page

# Initialize session state to track current page and login status
if "page" not in st.session_state:
    st.session_state.page = "login"  # Start with the login page
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login function
def login():
    username = st.session_state["login_username"]
    password = st.session_state["login_password"]
    
    if check_credentials(username, password):
        st.session_state.logged_in = True
        st.success("Successfully logged in!")
    else:
        st.error("Invalid username or password")

# Register function
def register():
    new_username = st.session_state["register_username"]
    new_password = st.session_state["register_password"]
    
    if register_user(new_username, new_password):
        st.success("User registered successfully! Redirecting to login page...")
        navigate_to("login")  # Redirect to login page after successful registration
    else:
        st.error("Failed to register user")

# Login page UI
def login_page():
    st.title("Login")

    # Input fields tied to session state to prevent page refresh from resetting the input
    st.text_input("Username", key="login_username")
    st.text_input("Password", type="password", key="login_password")

    # Use on_click to prevent triggering logic just by typing into inputs
    st.button("Login", on_click=login)

    st.write("Don't have an account?")
    st.button("Go to Register", on_click=lambda: navigate_to("register"))

# Registration page UI
def register_page():
    st.title("Register")

    # Input fields tied to session state to prevent page refresh from resetting the input
    st.text_input("New Username", key="register_username")
    st.text_input("New Password", type="password", key="register_password")

    # Use on_click to control when the register action is triggered
    st.button("Register", on_click=register)

    st.button("Back to Login", on_click=lambda: navigate_to("login"))

# Function to update Study Type based on Phases and Safety
def update_study_type(row):
    phases = row.get("Phases", "")
    
    if phases == "NA":
        return "PD"
    elif not phases or phases == "Not Available":
        return "PK"
    
    if row["Study Type"] == "INTERVENTIONAL":
        if "PHASE1" in phases or "PHASE 1" in phases:
            return "PK"
        elif any(phase in phases for phase in ["PHASE2", "PHASE 2", "PHASE3", "PHASE 3", "PHASE4", "PHASE 4"]):
            return "PD"
    
    elif row["Study Type"] == "OBSERVATIONAL":
        if "PHASE1" in phases or "PHASE 1" in phases:
            return "PK"
    
    return row["Study Type"]

# Function to fetch data for each condition
def fetch_data_for_condition(base_url, condition):
    data_list = []
    parameters = {
        "pageSize": 100,
        "query.term": quote_plus(condition)
    }
    response = requests.get(base_url, params=parameters)

    if response.status_code == 200:
        data = response.json()
        studies = data.get("studies", [])
        for study in studies:
            nctId = study["protocolSection"]["identificationModule"].get("nctId", "Unknown")
            overallStatus = study["protocolSection"]["statusModule"].get("overallStatus", "Unknown")
            startDate = study["protocolSection"]["statusModule"].get("startDateStruct", {}).get("date", "Unknown Date")
            conditions = ", ".join(study["protocolSection"]["conditionsModule"].get("conditions", ["No conditions listed"]))
            acronym = study["protocolSection"]["identificationModule"].get("acronym", "Unknown")

            interventions_list = study["protocolSection"].get("armsInterventionsModule", {}).get("interventions", [])
            interventions = ", ".join([intervention.get("name", "No intervention name listed") for intervention in interventions_list]) if interventions_list else "No interventions listed"

            locations_list = study["protocolSection"].get("contactsLocationsModule", {}).get("locations", [])
            locations = ", ".join([f"{location.get('city', 'No City')} - {location.get('country', 'No Country')}" for location in locations_list]) if locations_list else "No locations listed"

            primaryCompletionDate = study["protocolSection"]["statusModule"].get("primaryCompletionDateStruct", {}).get("date", "Unknown Date")
            studyFirstPostDate = study["protocolSection"]["statusModule"].get("studyFirstPostDateStruct", {}).get("date", "Unknown Date")
            lastUpdatePostDate = study["protocolSection"]["statusModule"].get("lastUpdatePostDateStruct", {}).get("date", "Unknown Date")
            studyType = study["protocolSection"]["designModule"].get("studyType", "Unknown")
            phases = ", ".join(study["protocolSection"]["designModule"].get("phases", ["Not Available"]))

            data_list.append({
                "NCT ID": nctId,
                "Acronym": acronym,
                "Overall Status": overallStatus,
                "Start Date": startDate,
                "Conditions": conditions,
                "Interventions": interventions,
                "Locations": locations,
                "Primary Completion Date": primaryCompletionDate,
                "Study First Post Date": studyFirstPostDate,
                "Last Update Post Date": lastUpdatePostDate,
                "Study Type": studyType,
                "Phases": phases,
            })
    else:
        st.error(f"Failed to fetch data for '{condition}'. Status code: {response.status_code} - {response.text}")

    return data_list

# Function to fetch data from API
def fetch_data(base_url, conditions):
    combined_data = []
    for condition in conditions:
        condition_data = fetch_data_for_condition(base_url, condition)
        combined_data.extend(condition_data)
    return combined_data

# Styling for DataFrame
def style_dataframe(df):
    numeric_cols = df.select_dtypes(include=['float', 'int']).columns.tolist()

    def highlight_null(s):
        return ['background-color: #f2f2f2' if pd.isnull(v) else '' for v in s]

    # Base styling for the dataframe
    styled_df = df.style \
        .set_table_styles([{
            'selector': 'thead th',
            'props': [('background-color', '#007acc'), ('color', 'white')]
        }]) \
        .set_properties(**{'border-color': '#007acc', 'color': 'black', 'background-color': '#f9f9f9'}) \
        .apply(highlight_null, axis=1) \
        .format(precision=2)

    if numeric_cols:
        styled_df = styled_df.background_gradient(subset=numeric_cols, cmap='coolwarm')

    return styled_df

# Function to update UI based on selected filter, including Safety
def update_ui_based_on_filter(df):
    study_filter = st.radio("Select Studies", ["All", "Pharmacodynamics (PD)", "Pharmacokinetics (PK)", "Safety"], index=0)

    if study_filter == "Pharmacodynamics (PD)":
        filtered_df = df[df["Study Type"] == "PD"]
    elif study_filter == "Pharmacokinetics (PK)":
        filtered_df = df[df["Study Type"] == "PK"]
    elif study_filter == "Safety":
        filtered_df = df[df["Conditions"].str.contains("safety", case=False, na=False) | 
                         df["Interventions"].str.contains("safety", case=False, na=False)]
    else:
        filtered_df = df

    styled_filtered_df = style_dataframe(filtered_df)
    st.write(f"### Rows containing '{study_filter}' studies")
    if not filtered_df.empty:
        st.dataframe(styled_filtered_df, use_container_width=True)
    else:
        st.write(f"No '{study_filter}' studies found.")

# Query input and display results based on conditions
def handle_query_input(conditions):
    query = st.text_area(f"Ask a query to the data fetched for {', '.join(conditions)}")

    if query and st.button("Submit Query", type="primary"):
        prompt = f"""
        1. Always show answer in tabular format if possible.
        2. Response should not be blank.
        3. Response should always be related to clinical trials.
        4. Format the response in table.
        """ + query

        first_input_prompt = PromptTemplate(
            input_variables=[prompt],
            template="Reply this question {first_input_prompt}",
        )

        llm = HuggingFaceHub(
            huggingfacehub_api_token="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",
            repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
            model_kwargs={"temperature": 0.5, "max_new_tokens": 512},
        )

        chain = LLMChain(llm=llm, prompt=first_input_prompt, verbose=False)

        with st.spinner("Processing your query..."):
            response = chain.run(prompt)

        st.write(response)

# Main application flow based on login status
if st.session_state.logged_in:
    st.title("ClinicalTrials.gov Integration")
    st.sidebar.header("Conditions Selection")
    conditions = st.sidebar.multiselect(
        "Select conditions to fetch data",
        ["Diabetes", "Asthma", "COVID-19", "Heart Disease", "Asthma in Children", "Breast Cancer", "Alzheimer's in Adults", "Asthma in Adults"]
    )

    if st.sidebar.button("Fetch Data") and conditions:
        base_url = "https://clinicaltrials.gov/api/v2/studies"
        data = fetch_data(base_url, conditions)
        df = pd.DataFrame(data)

        # Update study type based on phases and safety
        df["Study Type"] = df.apply(update_study_type, axis=1)
        st.session_state.df = df
        st.session_state.data_fetched = True
        st.session_state.conditions = conditions
        st.success("Data fetched successfully.")

    if "data_fetched" in st.session_state and st.session_state.data_fetched:
        df = st.session_state.df

        st.write("### Fetched Data")
        styled_df = style_dataframe(df)
        st.dataframe(styled_df, use_container_width=True)

        # Optionally, save the DataFrame to a CSV file
        df.to_csv(f"{'_'.join(conditions)}_clinical_trials_data.csv", index=False)

        # Count PK and PD studies
        pk_count = df["Study Type"].value_counts().get("PK", 0)
        pd_count = df["Study Type"].value_counts().get("PD", 0)

        # Display the counts
        st.write(f"### Pharmacokinetics Studies Count: {pk_count}")
        st.write(f"### Pharmacodynamics Studies Count: {pd_count}")

        update_ui_based_on_filter(df)
        handle_query_input(conditions)
else:
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()
