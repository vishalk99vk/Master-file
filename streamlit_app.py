import pandas as pd
import streamlit as st
import sqlite3
from io import BytesIO
import tempfile

st.set_page_config(page_title="BigQuery CROSS JOIN Simulator", page_icon="🧾", layout="wide")

st.title("🧾 BigQuery CROSS JOIN Simulator (SQLite Optimized)")
st.write("""
Upload your **Shop_ID** and **SKU_Master** files (CSV or Excel).  
This version uses an internal SQLite database — perfect for large datasets that crash pandas.
""")

# --- Upload files ---
shop_file = st.file_uploader("📂 Upload Shop_ID File", type=["csv", "xlsx"])
sku_file = st.file_uploader("📂 Upload SKU_Master File", type=["csv", "xlsx"])

# --- Helper to load CSV or Excel ---
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

            # --- Create temp SQLite database ---
            conn = sqlite3.connect(":memory:")
            shop_df.to_sql("shop", conn, index=False, if_exists="replace")
            sku_df.to_sql("sku", conn, index=False, if_exists="replace")

            # --- Run CROSS JOIN SQL (BigQuery style) ---
            sql_query = """
            SELECT
              shop.Shop_Id,
              sku.Perfect_Store_Threshold,
              sku.Category_Heading,
              sku.Category_Name,
              sku.Shelf_Section,
              sku.Group_name,
              sku.SKU_Name,
              sku.NPD_Flag,
              sku.Regular_OSA,
              sku.SOS,
              sku.Core_Flag,
              sku.Ideal_OSA,
              sku.Overall_Ideal_OSA,
              sku.Ideal_SOS,
              sku.Overall_Ideal_SOS,
              sku.Ideal_OSA_NPD,
              sku.Overall_Ideal_OSA_NPD,
              sku.Shelf_Section_Image_Links
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
