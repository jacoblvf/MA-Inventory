import requests
import pandas as pd
import io
import streamlit as st
from datetime import date

df1 = requests.get('https://api.orcascan.com/sheets/f5xG1-gqdcueAPfe?datetimeformat=DD/MM/YYYY HH:mm:ss&timezone=+00:00').content
df2 = requests.get('https://api.orcascan.com/sheets/rt7SbnAGBhSmb7EU?datetimeformat=DD/MM/YYYY HH:mm:ss&timezone=+00:00:').content
df3 = pd.read_csv(io.StringIO(df1.decode('utf-8')))
df4 = pd.read_csv(io.StringIO(df2.decode('utf-8')))

df3 = df3.groupby(["Name", "Bulk_or_Indiv"])[["Multiplier", "Scan_in"]].agg(Multiplier = ("Multiplier", "max"), Scan_in = ("Scan_in", "sum"))
df4 = df4.groupby(["Name", "Bulk_or_Indiv"])[["Multiplier", "Scan_out"]].agg(Multiplier = ("Multiplier", "max"), Scan_out = ("Scan_out", "sum"))

df3 = df3.reset_index()
df4 = df4.reset_index()

df5_2 = df3.merge(df4, on=['Name', 'Bulk_or_Indiv'], suffixes=[None, '_copy'])
df3 = df3.sort_values(by='Name', ascending=False)
df4 = df4.sort_values(by='Name', ascending=False)
df5 = pd.concat([df3,df4["Scan_out"]], axis=1)
df5=df5_2

df5["scan_qty"] = df5["Scan_in"] - df5["Scan_out"]
df5["indiv_qty"] = df5["scan_qty"]*df5["Multiplier"]
df6 = df5.groupby(["Name"])[["Bulk_or_Indiv", "indiv_qty"]].agg(bulkindiv = ("Bulk_or_Indiv", lambda x:"Indiv"), qty = ("indiv_qty", "sum"))

df7 = df6.rename(columns={'bulkindiv': 'Status', 'qty': 'Product Quantity'})
df7['Product Quantity'] = df7['Product Quantity'].astype("int64")
st.dataframe(df7, width=1000, height=600)

df8 = requests.get('https://docs.google.com/spreadsheets/d/e/2PACX-1vT0UBnLF6IU5M1U6y-FuYd98Ge9vJsaIUl-94r1YGmyCLueMaxdBxQikU2m6GUkqEHU4lR_2PXZvh4-/pubhtml?gid=592029174&single=true').content

df9 = df7.merge(df8, on=['Name'], suffixes=[None, '_copy'])
df9['Total Stock Price'] = df9['Product Quantity'] * df9['Cost']

refresh_button = st.button("Refresh")
if refresh_button:
    st.experimental_rerun()
    
@st.cache_data
def convert_df(df7):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df7.to_csv().encode('utf-8')

csv = convert_df(df7=df7)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name=str(date.today()) + ".csv",
    mime='text/csv',
)

CORRECT_PASSCODE = "247123"

def convert_df_to_csv(df9):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()

# Title of the app
st.title("Password Protected Stock Price Download")

# Input field for the passcode
passcode = st.text_input("Enter Passcode:", type="password")

# Button to check passcode and enable download
if st.button("Download CSV"):
    if passcode == CORRECT_PASSCODE:
        st.success("Passcode is correct! You can download the CSV file now.")
        
        # Convert DataFrame to CSV
        csv = convert_df_to_csv(df9)
