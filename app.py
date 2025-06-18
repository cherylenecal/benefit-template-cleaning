import pandas as pd
import streamlit as st
from io import BytesIO

# Function to filter data
def filter_data(df):
    if 'Status Claim' in df.columns:
        df = df[df['Status_Claim'] == 'R']
    else:
        print("⚠️ Kolom 'Status Claim' tidak ditemukan. Data tidak difilter.")
    return df

# Main processing function
def move_to_template(df):
    # Step 1: Filter the data
    new_df = filter_data(df)

    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
    
    # # Step 3: Convert date columns to datetime
    # date_columns = ["TreatmentStart", "TreatmentFinish", "PaymentDate"]
    # for col in date_columns:
    #     new_df[col] = pd.to_datetime(new_df[col], errors='coerce')
    #     if new_df[col].isnull().any():
    #         st.warning(f"Invalid date values detected in column '{col}'. Coerced to NaT.")
            
    # Step 5: Transform to the new template
    new_df = new_df.drop(columns=["Status_Claim"], errors='ignore')
    new_df = new_df.drop(columns=["BAmount"], errors='ignore')

    df_transformed = new_df
    return df_transformed

# Save the processed data to Excel and return as BytesIO
def save_to_excel(df, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write the transformed data
        df.to_excel(writer, index=False, sheet_name='SC')
    output.seek(0)
    return output, filename

# Streamlit app
st.title("Benefit Template")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file:
    raw_data = pd.read_csv(uploaded_file)
    
    # Process data
    st.write("Processing data...")
    transformed_data = move_to_template(raw_data)
    
    # Show a preview of the transformed data
    st.write("Transformed Data Preview:")
    st.dataframe(transformed_data.head())

    # Compute summary statistics
    total_benefit = len(transformed_data)
    total_billed = int(transformed_data["Billed"].sum())
    total_accepted = int(transformed_data["Accepted"].sum())
    total_excess = int(transformed_data["ExcessTotal"].sum())
    total_unpaid = int(transformed_data["Unpaid"].sum())

    st.write("Claim Summary:")
    st.write(f"- Total Claims: {total_benefit:,}")
    st.write(f"- Total Billed: {total_billed:,}")
    st.write(f"- Total Accepted: {total_accepted:,}")
    st.write(f"- Total Excess: {total_excess:,}")
    st.write(f"- Total Unpaid: {total_unpaid:,}")

    # User input for filename
    filename = st.text_input("Enter the Excel file name (without extension):", "Transformed_Claim_Data")

    # Download link for the Excel file
    if filename:
        excel_file, final_filename = save_to_excel(transformed_data, filename=filename + ".xlsx")
        st.download_button(
            label="Download Excel File",
            data=excel_file,
            file_name=final_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
