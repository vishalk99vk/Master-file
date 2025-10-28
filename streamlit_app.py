import pandas as pd
import streamlit as st
import sqlite3
from io import BytesIO

st.set_page_config(page_title="BigQuery CROSS JOIN Simulator", page_icon="🧾", layout="wide")

st.title("🧾 BigQuery CROSS JOIN Simulator (Auto Column Detection)")
st.write("""
Upload your **Shop_ID** and **SKU_Master** files (CSV or Excel).  
This version automatically adjusts if some columns are missing from your SKU master file.
""")

# --- Upload files ---
shop_file = st.file_uploader("📂 Upload Shop_ID File", type=["csv", "xlsx"])
sku_file = st.file_uploader("📂 Upload SKU_Master File", type=["csv", "xlsx"])

def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    else:
        raise ValueError("Unsupported file type")

if shop_file and sku_file:
    try:
        st.info("⚙️ Loading files...")
        shop_df = load_file(shop_file)
        sku_df = load_file(sku_file)

        if "Shop_Id" not in shop_df.columns:
            st.error("❌ The 'Shop_Id' column is missing in your Shop_ID file.")
        else:
            st.info("🚀 Creating in-memory SQLite database...")

            conn = sqlite3.connect(":memory:")
            shop_df.to_sql("shop", conn, index=False, if_exists="replace")
            sku_df.to_sql("sku", conn, index=False, if_exists="replace")

            # --- Columns expected from BigQuery ---
            expected_cols = [
                "Perfect_Store_Threshold", "Category_Heading", "Category_Name",
                "Shelf_Section", "Group_name", "SKU_Name", "NPD_Flag",
                "Regular_OSA", "SOS", "Core_Flag", "Ideal_OSA",
                "Overall_Ideal_OSA", "Ideal_SOS", "Overall_Ideal_SOS",
                "Ideal_OSA_NPD", "Overall_Ideal_OSA_NPD", "Shelf_Section_Image_Links"
            ]

            # --- Keep only columns that exist in the uploaded file ---
            available_cols = [col for col in expected_cols if col in sku_df.columns]
            missing_cols = [col for col in expected_cols if col not in sku_df.columns]

            if missing_cols:
                st.warning(f"⚠️ Missing columns in SKU_Master: {', '.join(missing_cols)}")

            # --- Dynamically build SQL SELECT statement ---
            select_columns = ", ".join([f"sku.{col}" for col in available_cols])
            sql_query = f"""
            SELECT shop.Shop_Id, {select_columns}
            FROM shop
            CROSS JOIN sku
            ORDER BY shop.Shop_Id ASC
            """

            st.info("🧩 Running CROSS JOIN in SQLite...")
            result_df = pd.read_sql_query(sql_query, conn)
            st.success(f"✅ CROSS JOIN completed successfully! Total rows: {len(result_df):,}")

            # --- Preview result ---
            st.dataframe(result_df.head(10))

            # --- Export to Excel ---
            buffer = BytesIO()
            result_df.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label="💾 Download Full Output as Excel",
                data=buffer,
                file_name="Output_Shop_SKU.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            conn.close()

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

else:
    st.info("⬆️ Please upload both files to begin.")
