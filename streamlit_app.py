import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="BigQuery CROSS JOIN Simulator", page_icon="🧾", layout="centered")

st.title("🧾 BigQuery CROSS JOIN Simulator")
st.write("Upload your **Shop_ID** and **SKU_Master** files (CSV or Excel). The app will generate the same output as your BigQuery CROSS JOIN query.")

# --- File Upload ---
shop_file = st.file_uploader("📂 Upload Shop_ID File", type=["csv", "xlsx"])
sku_file = st.file_uploader("📂 Upload SKU_Master File", type=["csv", "xlsx"])

# --- Helper function to load files ---
def load_file(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file)
    else:
        st.error("Unsupported file type!")
        return None

if shop_file and sku_file:
    try:
        st.info("Processing... Please wait ⏳")

        # Load files
        shop_df = load_file(shop_file)
        sku_df = load_file(sku_file)

        # Add dummy key for CROSS JOIN
        shop_df["key"] = 1
        sku_df["key"] = 1

        # Perform CROSS JOIN
        combined_df = pd.merge(shop_df, sku_df, on="key").drop("key", axis=1)

        # Select BigQuery columns
        selected_columns = [
            "Shop_Id",
            "Perfect_Store_Threshold",
            "Category_Heading",
            "Category_Name",
            "Shelf_Section",
            "Group_name",
            "SKU_Name",
            "NPD_Flag",
            "Regular_OSA",
            "SOS",
            "Core_Flag",
            "Ideal_OSA",
            "Overall_Ideal_OSA",
            "Ideal_SOS",
            "Overall_Ideal_SOS",
            "Ideal_OSA_NPD",
            "Overall_Ideal_OSA_NPD",
            "Shelf_Section_Image_Links"
        ]
        selected_columns = [c for c in selected_columns if c in combined_df.columns]
        output_df = combined_df[selected_columns].sort_values(by="Shop_Id", ascending=True)

        # Display Preview
        st.success(f"CROSS JOIN completed successfully! ✅")
        st.write("### Preview of Result:")
        st.dataframe(output_df.head(10))

        # --- Download Button ---
        def to_excel_bytes(df):
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)
            return buffer

        excel_bytes = to_excel_bytes(output_df)

        st.download_button(
            label="💾 Download Output as Excel",
            data=excel_bytes,
            file_name="Output_Shop_SKU.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
else:
    st.info("⬆️ Please upload both files to begin.")
