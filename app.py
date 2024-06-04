import requests
import pandas as pd
import io
import streamlit as st
from datetime import date

df1 = requests.get('https://api.orcascan.com/sheets/f5xG1-gqdcueAPfe?datetimeformat=DD/MM/YYYY HH:mm:ss&timezone=+00:00').content
df2 = requests.get('https://api.orcascan.com/sheets/rt7SbnAGBhSmb7EU?datetimeformat=DD/MM/YYYY HH:mm:ss&timezone=+00:00:').content
df3 = pd.read_csv(io.StringIO(df1.decode('utf-8')))
df4 = pd.read_csv(io.StringIO(df2.decode('utf-8')))

df3 = df3.groupby(["Name", "Bulk_or_Indiv"])[["Multiplier", "Scan_in", "Barcode"]].agg(Mulitplier = ("Multiplier", "max"), Scan_in = ("Scan_in", "sum"))
df4 = df4.groupby(["Name", "Bulk_or_Indiv"])[["Multiplier", "Scan_out", "Barcode"]].agg(Mulitplier = ("Multiplier", "max"), Scan_out = ("Scan_out", "sum"))

df5_2 = df3.merge(df4, on=['Name', 'Bulk_or_Indiv'], suffixes=[None, '_copy'])
df3 = df3.sort_values(by='Name', ascending=False)
df4 = df4.sort_values(by='Name', ascending=False)
df5 = pd.concat([df3,df4["Scan_out"]], axis=1)
df5=df5_2
df5 = df5[df5['Barcode'] != "0"]
if df5.index.name is None:
    df5 = df5[df5.index.notnull()]
df5["scan_qty"] = df5["Scan_in"] - df5["Scan_out"]
df5["indiv_qty"] = df5["scan_qty"]*df5["Multiplier"]
df6 = df5.groupby(["Name"])[["Bulk_or_Indiv", "indiv_qty"]].agg(bulkindiv = ("Bulk_or_Indiv", lambda x:"Indiv"), qty = ("indiv_qty", "sum"))

df7 = df6.rename(columns={'bulkindiv': 'Status', 'qty': 'Product Quantity'})
df7['Product Quantity'] = df7['Product Quantity'].astype("int64")
st.dataframe(df7, width=1000, height=600)

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
