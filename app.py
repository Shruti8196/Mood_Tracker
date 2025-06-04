import streamlit as st
from streamlit_autorefresh import st_autorefresh
import gspread
from datetime import datetime, date
from collections import Counter
import plotly.express as px
import os
import base64
import pytz  

# Define PST timezone
pst = pytz.timezone("America/Los_Angeles")

# Refresh every 10 seconds (10,000 milliseconds), Mood inputs may come from various sources, not just Streamlit note submissions, so the bar chart should reflect all mood updates in real time
# st_autorefresh(interval=10000, key="refresh")

# Constants
SHEET_ID = "1jsjM4WVoMQLNmc8LrtVV7X4ASr8f3952S30yIvNKSAQ"

# Decode and write the key from secrets
key_b64 = st.secrets["gcp"]["gcp_key_base64"]
key_json = base64.b64decode(key_b64).decode("utf-8")
with open("gcp_key1.json", "w") as f:
    f.write(key_json)

# Authenticate with service account
gc = gspread.service_account(filename="gcp_key1.json")

# Open the Google Sheet by ID
sh = gc.open_by_key(SHEET_ID)

# Select the first worksheet
worksheet = sh.get_worksheet(0)

# Function to log mood
def log_mood(mood: str, note: str = ""):
    timestamp = datetime.now(pytz.utc).astimezone(pst).strftime("%Y-%m-%d %H:%M:%S")
    worksheet.append_row([timestamp, mood, note])

def get_mood_counts_for_date(selected_date):
    all_values = worksheet.get_all_values()
    date_str = selected_date.strftime("%Y-%m-%d")
    moods = [row[1] for row in all_values[1:] if row[0].split()[0] == date_str]
    return Counter(moods)

# Streamlit UI
st.title("Mood Tracker")

moods = {
    "😊": "Happy",
    "😠": "Angry",
    "😕": "Confused",
    "🎉": "Celebratory"
}

# Mood selection
selected_mood = st.selectbox("Select mood", options=list(moods.keys()), format_func=lambda x: f"{x}  {moods[x]}")

# Optional note
note = st.text_input("Add a note (optional)")

# Submit button
if st.button("Log Mood"):
    log_mood(selected_mood, note)
    st.success("Mood logged!")

# Select Date
st.subheader("View Mood Counts by Date")
selected_date = st.date_input("Select date", value=datetime.now(pytz.utc).astimezone(pst).date(),format="MM/DD/YYYY")
counts = get_mood_counts_for_date(selected_date)

# If moods were logged in, we can display them
if counts:
    fig = px.bar(
        x=list(counts.keys()),
        y=list(counts.values()),
        labels={'x': 'Mood', 'y': 'Count'},
        title=f"Mood Counts for {selected_date.strftime('%m/%d/%Y')}",
        color_discrete_sequence=["#63b3ed"]
    )
    st.plotly_chart(fig)
else:
    st.write("No moods logged on this date.")
    
