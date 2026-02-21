import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Daily Outfit Tracker")

st.title("👕 Daily Outfit Tracker")

# ----------------------------
# Initialize Files
# ----------------------------

if not os.path.exists("outfits.csv"):
    pd.DataFrame(columns=["Date", "Description"]).to_csv("outfits.csv", index=False)

if not os.path.exists("wardrobe.csv"):
    initial_data = pd.DataFrame({
        "Category": ["Top", "Bottom", "Shoes", "Accessory"],
        "Item": ["T-Shirt", "Jeans", "Sneakers", "Watch"]
    })
    initial_data.to_csv("wardrobe.csv", index=False)

outfits_df = pd.read_csv("outfits.csv")
wardrobe_df = pd.read_csv("wardrobe.csv")

# ----------------------------
# Add New Clothing Item
# ----------------------------

st.subheader("➕ Add New Clothing Item")

category = st.selectbox("Select Category", ["Top", "Bottom", "Shoes", "Accessory"])
new_item = st.text_input("Enter New Item Name")

if st.button("Add Item"):
    if new_item:
        new_row = pd.DataFrame([[category, new_item]],
                               columns=["Category", "Item"])
        wardrobe_df = pd.concat([wardrobe_df, new_row], ignore_index=True)
        wardrobe_df.to_csv("wardrobe.csv", index=False)
        st.success(f"{new_item} added to {category}!")
    else:
        st.warning("Please enter an item name.")

st.divider()

# ----------------------------
# Outfit Maker Section
# ----------------------------

st.subheader("🧩 Outfit Maker")

tops = wardrobe_df[wardrobe_df["Category"] == "Top"]["Item"].tolist()
bottoms = wardrobe_df[wardrobe_df["Category"] == "Bottom"]["Item"].tolist()
shoes = wardrobe_df[wardrobe_df["Category"] == "Shoes"]["Item"].tolist()
accessories = wardrobe_df[wardrobe_df["Category"] == "Accessory"]["Item"].tolist()

col1, col2 = st.columns(2)

with col1:
    selected_top = st.selectbox("Select Top", tops)
    selected_bottom = st.selectbox("Select Bottom", bottoms)

with col2:
    selected_shoes = st.selectbox("Select Shoes", shoes)
    selected_accessory = st.selectbox("Select Accessory", accessories)

description = f"{selected_top} with {selected_bottom}, {selected_shoes}, {selected_accessory}"

st.write("### 🪄 Outfit Preview")
st.success(description)

if st.button("Save Outfit"):
    new_data = pd.DataFrame([[datetime.today().date(), description]],
                            columns=["Date", "Description"])

    outfits_df = pd.concat([outfits_df, new_data], ignore_index=True)
    outfits_df.to_csv("outfits.csv", index=False)

    st.success("Outfit Saved Successfully!")

# ----------------------------
# Outfit History
# ----------------------------

st.divider()
st.subheader("📸 Outfit History")

for index, row in outfits_df.iterrows():
    st.write(f"**Date:** {row['Date']}")
    st.write(f"Outfit: {row['Description']}")
    st.divider()
