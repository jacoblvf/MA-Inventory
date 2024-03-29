import requests
import pandas as pd
import io
import streamlit as st
from datetime import date

df1 = requests.get('https://api.orcascan.com/sheets/f5xG1-gqdcueAPfe?datetimeformat=DD/MM/YYYY HH:mm:ss&timezone=+00:00').content
df2 = requests.get('https://api.orcascan.com/sheets/rt7SbnAGBhSmb7EU?datetimeformat=DD/MM/YYYY HH:mm:ss&timezone=+00:00:').content
df3 = pd.read_csv(io.StringIO(df1.decode('utf-8')))
df4 = pd.read_csv(io.StringIO(df2.decode('utf-8')))
df5 = df3.sort_values(by='Barcode', ascending=False)
df6 = df4.sort_values(by='Barcode', ascending=False)
df7 = pd.concat([df3,df4["Scan_out"]], axis=1)
if df7.index.name is None:
    df7 = df7[df7.index.notnull()]
df7["scan_qty"] = df7["Scan_in"] - df7["Scan_out"]
df7["indiv_qty"] = df7["scan_qty"]*df7["Multiplier"]
df8 = df7.groupby(["Name"])[["Bulk_or_Indiv", "indiv_qty"]].agg(bulkindiv = ("Bulk_or_Indiv", lambda x:"Indiv"), qty = ("indiv_qty", "sum"))

df9 = df8.rename(columns={'bulkindiv': 'Status', 'qty': 'Product Quantity'})

st.dataframe(df9, width=1000, height=600)

refresh_button = st.button("Refresh")
if refresh_button:
    st.experimental_rerun()
    
@st.cache_data
def convert_df(df9):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df9.to_csv().encode('utf-8')

csv = convert_df(df9=df9)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name=str(date.today()) + ".csv",
    mime='text/csv',
)
