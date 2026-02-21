import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from collections import Counter
import json

st.set_page_config(page_title="Outfit Designer & Tracker", layout="wide")

st.title("👔 Outfit Designer & Tracker")
st.markdown("*Design, track, and analyze your personal style*")

# ----------------------------
# Initialize Files
# ----------------------------

if not os.path.exists("outfits.csv"):
    pd.DataFrame(columns=["Date", "Description", "Rating", "Notes", "Weather", "Occasion", "ID"]).to_csv("outfits.csv", index=False)

if not os.path.exists("wardrobe.csv"):
    initial_data = pd.DataFrame({
        "ID": ["1", "2", "3", "4"],
        "Category": ["Top", "Bottom", "Shoes", "Accessory"],
        "Item": ["T-Shirt", "Jeans", "Sneakers", "Watch"],
        "Color": ["blue", "blue", "white", "black"],
        "Style": ["casual", "casual", "casual", "casual"],
        "Season": ["Year-round", "Year-round", "Year-round", "Year-round"],
        "Times Used": [0, 0, 0, 0]
    })
    initial_data.to_csv("wardrobe.csv", index=False)


outfits_df = pd.read_csv("outfits.csv")
wardrobe_df = pd.read_csv("wardrobe.csv")

# Ensure all required columns exist
required_wardrobe_cols = ["ID", "Category", "Item", "Color", "Style", "Season", "Times Used"]
for col in required_wardrobe_cols:
    if col not in wardrobe_df.columns:
        wardrobe_df[col] = 0 if col == "Times Used" else ""

required_outfits_cols = ["Date", "Description", "Rating", "Notes", "Weather", "Occasion", "ID"]
for col in required_outfits_cols:
    if col not in outfits_df.columns:
        outfits_df[col] = 0 if col in ["Rating", "ID"] else ""

# Convert Times Used to numeric
wardrobe_df["Times Used"] = pd.to_numeric(wardrobe_df["Times Used"], errors='coerce').fillna(0).astype(int)
outfits_df["Rating"] = pd.to_numeric(outfits_df["Rating"], errors='coerce').fillna(0)

# Save updated dataframes to ensure columns persist
wardrobe_df.to_csv("wardrobe.csv", index=False)
outfits_df.to_csv("outfits.csv", index=False)

# Helper functions
def get_next_item_id():
    if len(wardrobe_df) == 0:
        return "1"
    return str(int(wardrobe_df["ID"].max()) + 1)

def update_item_usage(item_id):
    """Increment usage count for an item"""
    global wardrobe_df
    wardrobe_df.loc[wardrobe_df["ID"] == item_id, "Times Used"] = \
        pd.to_numeric(wardrobe_df.loc[wardrobe_df["ID"] == item_id, "Times Used"], errors='coerce').fillna(0).astype(int) + 1
    wardrobe_df.to_csv("wardrobe.csv", index=False)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", 
    ["Dashboard", "Outfit Maker", "Wardrobe Manager", "Outfit History", "Analytics", "Settings"])

# ----------------------------
# DASHBOARD PAGE
# ----------------------------
if page == "Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Outfits", len(outfits_df))
    with col2:
        st.metric("Wardrobe Items", len(wardrobe_df))
    with col3:
        avg_rating = outfits_df['Rating'].astype(float).mean() if 'Rating' in outfits_df.columns and len(outfits_df) > 0 else 0
        st.metric("Avg Rating", f"{avg_rating:.1f}/5" if avg_rating > 0 else "N/A")
    with col4:
        recent_outfits = len(outfits_df[outfits_df['Date'] == str(datetime.today().date())])
        st.metric("Today's Outfits", recent_outfits)
    
    st.divider()
    
    # Quick stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Most Used Items")
        if len(wardrobe_df) > 0:
            top_items = wardrobe_df.nlargest(5, 'Times Used')[['Item', 'Times Used']]
            if len(top_items) > 0:
                st.bar_chart(top_items.set_index('Item'))
    
    with col2:
        st.subheader("⭐ Recent High-Rated Outfits")
        if len(outfits_df) > 0 and 'Rating' in outfits_df.columns:
            try:
                high_rated = outfits_df.dropna(subset=['Rating'])
                high_rated['Rating'] = pd.to_numeric(high_rated['Rating'])
                top_outfits = high_rated.nlargest(3, 'Rating')[['Date', 'Description', 'Rating']]
                for idx, row in top_outfits.iterrows():
                    st.write(f"📅 {row['Date']} | ⭐ {row['Rating']}")
                    st.write(f"*{row['Description']}*")
                    st.divider()
            except:
                st.info("No ratings yet")
        else:
            st.info("No outfits recorded yet")

# ----------------------------
# OUTFIT MAKER PAGE
# ----------------------------
elif page == "Outfit Maker":

    st.subheader("🧩 Create Your Outfit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tops = wardrobe_df[wardrobe_df["Category"] == "Top"][["ID", "Item", "Color"]].copy()
        tops_display = [f"{row['Item']} ({row['Color']})" for _, row in tops.iterrows()]
        selected_top_idx = st.selectbox("Select Top", range(len(tops_display)), format_func=lambda i: tops_display[i])
        selected_top_id = tops.iloc[selected_top_idx]["ID"]
        selected_top = tops.iloc[selected_top_idx]["Item"]
        
        bottoms = wardrobe_df[wardrobe_df["Category"] == "Bottom"][["ID", "Item", "Color"]].copy()
        bottoms_display = [f"{row['Item']} ({row['Color']})" for _, row in bottoms.iterrows()]
        selected_bottom_idx = st.selectbox("Select Bottom", range(len(bottoms_display)), format_func=lambda i: bottoms_display[i])
        selected_bottom_id = bottoms.iloc[selected_bottom_idx]["ID"]
        selected_bottom = bottoms.iloc[selected_bottom_idx]["Item"]
    
    with col2:
        if len(wardrobe_df[wardrobe_df["Category"] == "Shoes"]) > 0:
            shoes = wardrobe_df[wardrobe_df["Category"] == "Shoes"][["ID", "Item", "Color"]].copy()
            shoes_display = [f"{row['Item']} ({row['Color']})" for _, row in shoes.iterrows()]
            selected_shoes_idx = st.selectbox("Select Shoes", range(len(shoes_display)), format_func=lambda i: shoes_display[i])
            selected_shoes_id = shoes.iloc[selected_shoes_idx]["ID"]
            selected_shoes = shoes.iloc[selected_shoes_idx]["Item"]
        else:
            selected_shoes = "No shoes"
            selected_shoes_id = None
        
        if len(wardrobe_df[wardrobe_df["Category"] == "Accessory"]) > 0:
            accessories = wardrobe_df[wardrobe_df["Category"] == "Accessory"][["ID", "Item", "Color"]].copy()
            acc_display = [f"{row['Item']} ({row['Color']})" for _, row in accessories.iterrows()]
            selected_acc_idx = st.selectbox("Select Accessory", range(len(acc_display)), format_func=lambda i: acc_display[i])
            selected_acc_id = accessories.iloc[selected_acc_idx]["ID"]
            selected_accessory = accessories.iloc[selected_acc_idx]["Item"]
        else:
            selected_accessory = "No accessories"
            selected_acc_id = None
    
    st.divider()
    
    # Outfit details
    col1, col2 = st.columns(2)
    with col1:
        occasion = st.selectbox("Occasion", ["Casual", "Work", "Evening", "Sport", "Party", "Other"])
        weather = st.selectbox("Weather", ["Sunny", "Rainy", "Snowy", "Cloudy", "Hot", "Cold"])
    with col2:
        notes = st.text_area("Additional Notes", placeholder="e.g., Colors match well, very comfortable...")
    
    st.divider()
    
    # Outfit Preview
    st.subheader("🎨 Outfit Preview")
    description = f"{selected_top} + {selected_bottom} + {selected_shoes} + {selected_accessory}"
    
    preview_col1, preview_col2 = st.columns([3, 1])
    with preview_col1:
        st.info(f"**{description}**")
    
    # Save outfit
    if st.button("💾 Save Outfit", use_container_width=True, type="primary"):
        new_id = str(int(outfits_df['ID'].max()) + 1) if len(outfits_df) > 0 else "1"
        new_data = pd.DataFrame([[
            datetime.today().date(), 
            description,
            0,
            notes,
            weather,
            occasion,
            new_id
        ]], columns=["Date", "Description", "Rating", "Notes", "Weather", "Occasion", "ID"])
        
        outfits_df = pd.concat([outfits_df, new_data], ignore_index=True)
        outfits_df.to_csv("outfits.csv", index=False)
        
        # Update usage stats
        for item_id in [selected_top_id, selected_bottom_id, selected_shoes_id, selected_acc_id]:
            if item_id and pd.notna(item_id):
                update_item_usage(str(item_id))
        
        st.success(f"✅ Outfit saved! ({occasion}, {weather})")

# ----------------------------
# WARDROBE MANAGER PAGE
# ----------------------------
elif page == "Wardrobe Manager":
    tab1, tab2, tab3 = st.tabs(["Add Item", "View Wardrobe", "Manage Items"])
    
    with tab1:
        st.subheader("➕ Add New Clothing Item")
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("Select Category", ["Top", "Bottom", "Shoes", "Accessory", "Outerwear", "Other"])
            new_item = st.text_input("Item Name", placeholder="e.g., Blue V-Neck T-Shirt")
            color = st.selectbox("Color", ["Blue", "Red", "Black", "White", "Gray", "Green", "Yellow", "Pink", "Purple", "Orange", "Brown", "Multicolor", "Other"])
        
        with col2:
            style = st.selectbox("Style", ["Casual", "Formal", "Sport", "Vintage", "Bohemian", "Minimalist", "Other"])
            season = st.selectbox("Season", ["Year-round", "Spring", "Summer", "Fall", "Winter", "Summer/Winter"])
            condition = st.selectbox("Condition", ["Like New", "Good", "Fair", "Need Repair"])
        
        if st.button("Add Item to Wardrobe", use_container_width=True, type="primary"):
            if new_item:
                new_id = get_next_item_id()
                new_row = pd.DataFrame([[new_id, category, new_item, color.lower(), style.lower(), season, 0]],
                                       columns=["ID", "Category", "Item", "Color", "Style", "Season", "Times Used"])
                wardrobe_df = pd.concat([wardrobe_df, new_row], ignore_index=True)
                wardrobe_df.to_csv("wardrobe.csv", index=False)
                st.success(f"✅ {new_item} added to {category}!")
            else:
                st.warning("❌ Please enter an item name.")
    
    with tab2:
        st.subheader("👕 Your Wardrobe")
        
    # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            categories = ["All"] + sorted(wardrobe_df["Category"].dropna().unique().tolist())
            filter_category = st.selectbox("Filter by Category", categories)
        with col2:
            colors = ["All"] + sorted([c for c in wardrobe_df["Color"].dropna().unique().tolist() if c])
            filter_color = st.selectbox("Filter by Color", colors)
        with col3:
            styles = ["All"] + sorted([s for s in wardrobe_df["Style"].dropna().unique().tolist() if s])
            filter_style = st.selectbox("Filter by Style", styles)
        
        # Apply filters
        filtered_df = wardrobe_df.copy()
        if filter_category != "All":
            filtered_df = filtered_df[filtered_df["Category"] == filter_category]
        if filter_color != "All":
            filtered_df = filtered_df[filtered_df["Color"] == filter_color]
        if filter_style != "All":
            filtered_df = filtered_df[filtered_df["Style"] == filter_style]
        
        st.divider()
        
        # Display wardrobe
        if len(filtered_df) > 0:
            display_cols = ["Item", "Category", "Color", "Style", "Season", "Times Used"]
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
            
            st.metric("Items Matching Filters", len(filtered_df))
        else:
            st.info("No items match your filter criteria")
    
    with tab3:
        st.subheader("🗑️ Manage Wardrobe Items")
        
        if len(wardrobe_df) > 0:
            item_to_delete = st.selectbox("Select item to delete/edit", 
                                         [f"{row['Item']} ({row['Color']}, {row['Category']})" for _, row in wardrobe_df.iterrows()],
                                         key="delete_select")
            
            selected_idx = wardrobe_df[wardrobe_df['Item'] == item_to_delete.split(' (')[0]].index[0]
            selected_item = wardrobe_df.iloc[selected_idx]
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Delete Item", use_container_width=True):
                    wardrobe_df = wardrobe_df.drop(selected_idx).reset_index(drop=True)
                    wardrobe_df.to_csv("wardrobe.csv", index=False)
                    st.success(f"✅ {selected_item['Item']} deleted!")
                    st.rerun()
            
            with col2:
                if st.button("✏️ Edit Item", use_container_width=True):
                    st.session_state.editing = True
            
            if st.session_state.get('editing', False):
                st.divider()
                st.subheader("Edit Item Details")
                
                new_color = st.text_input("Color", value=selected_item['Color'].capitalize(), placeholder="e.g., Blue, Sage Green, Navy...")
                new_style = st.selectbox("Style", ["Casual", "Formal", "Sport", "Vintage", "Bohemian", "Minimalist", "Other"],
                                        index=["Casual", "Formal", "Sport", "Vintage", "Bohemian", "Minimalist", "Other"].index(selected_item['Style'].capitalize()) if selected_item['Style'].capitalize() in ["Casual", "Formal", "Sport", "Vintage", "Bohemian", "Minimalist", "Other"] else 0)
                new_season = st.selectbox("Season", ["Year-round", "Spring", "Summer", "Fall", "Winter", "Summer/Winter"],
                                         index=["Year-round", "Spring", "Summer", "Fall", "Winter", "Summer/Winter"].index(selected_item['Season']) if selected_item['Season'] in ["Year-round", "Spring", "Summer", "Fall", "Winter", "Summer/Winter"] else 0)
                
                if st.button("Save Changes", use_container_width=True, type="primary"):
                    wardrobe_df.loc[selected_idx, 'Color'] = new_color.lower()
                    wardrobe_df.loc[selected_idx, 'Style'] = new_style.lower()
                    wardrobe_df.loc[selected_idx, 'Season'] = new_season
                    wardrobe_df.to_csv("wardrobe.csv", index=False)
                    st.success("✅ Item updated!")
                    st.session_state.editing = False
                    st.rerun()

# ----------------------------
# OUTFIT HISTORY PAGE
# ----------------------------
elif page == "Outfit History":
    st.subheader("📸 Outfit History")
    
    if len(outfits_df) == 0:
        st.info("No outfits recorded yet. Go to Outfit Maker to create one!")
    else:
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_occasion = st.selectbox("Filter by Occasion", ["All"] + outfits_df["Occasion"].unique().tolist() if "Occasion" in outfits_df.columns else ["All"])
        with col2:
            filter_weather = st.selectbox("Filter by Weather", ["All"] + outfits_df["Weather"].unique().tolist() if "Weather" in outfits_df.columns else ["All"])
        with col3:
            sort_by = st.selectbox("Sort by", ["Recent First", "Oldest First", "Highest Rated", "Most Popular"])
        
        # Apply filters
        display_df = outfits_df.copy()
        if filter_occasion != "All" and "Occasion" in display_df.columns:
            display_df = display_df[display_df["Occasion"] == filter_occasion]
        if filter_weather != "All" and "Weather" in display_df.columns:
            display_df = display_df[display_df["Weather"] == filter_weather]
        
        # Sort
        if sort_by == "Oldest First":
            display_df = display_df.sort_values('Date')
        elif sort_by == "Highest Rated":
            display_df = display_df.sort_values('Rating', ascending=False)
        elif sort_by == "Most Popular":
            display_df = display_df.sort_values('Times Used', ascending=False) if 'Times Used' in display_df.columns else display_df
        else:
            display_df = display_df.sort_values('Date', ascending=False)
        
        st.divider()
        
        # Display outfits
        for index, row in display_df.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{row['Date']}** | {row.get('Occasion', 'N/A')} | {row.get('Weather', 'N/A')}")
                st.write(f"*{row['Description']}*")
                if pd.notna(row.get('Notes', '')) and row.get('Notes', '') != '':
                    st.caption(f"📝 {row['Notes']}")
            
            with col2:
                # Rating
                current_rating = float(row.get('Rating', 0)) if pd.notna(row.get('Rating', 0)) else 0
                new_rating = st.selectbox(f"Rating", range(0, 6), value=int(current_rating), key=f"rating_{index}")
                if new_rating != current_rating:
                    outfits_df.loc[outfits_df['ID'] == row['ID'], 'Rating'] = new_rating
                    outfits_df.to_csv("outfits.csv", index=False)
                    st.rerun()
            
            with col3:
                if st.button("🗑️", key=f"delete_{index}", use_container_width=True):
                    outfits_df = outfits_df.drop(index).reset_index(drop=True)
                    outfits_df.to_csv("outfits.csv", index=False)
                    st.success("✅ Outfit deleted!")
                    st.rerun()
            
            st.divider()

# ----------------------------
# ANALYTICS PAGE
# ----------------------------
elif page == "Analytics":
    st.subheader("📊 Wardrobe Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Outfits", len(outfits_df))
    with col2:
        st.metric("Wardrobe Size", len(wardrobe_df))
    with col3:
        avg_rating = outfits_df['Rating'].astype(float).mean() if 'Rating' in outfits_df.columns and len(outfits_df) > 0 else 0
        st.metric("Average Rating", f"{avg_rating:.1f}/5" if avg_rating > 0 else "N/A")
    with col4:
        days_tracked = len(outfits_df['Date'].unique()) if len(outfits_df) > 0 else 0
        st.metric("Days Tracked", days_tracked)
    
    st.divider()
    
    # Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("👕 Most Used Items")
        if len(wardrobe_df) > 0:
            top_items = wardrobe_df.nlargest(10, 'Times Used')
            if len(top_items) > 0 and top_items['Times Used'].sum() > 0:
                st.bar_chart(top_items.set_index('Item')['Times Used'])
            else:
                st.info("No usage data yet")
    
    with chart_col2:
        st.subheader("📂 Items by Category")
        if len(wardrobe_df) > 0:
            category_counts = wardrobe_df['Category'].value_counts()
            st.bar_chart(category_counts)
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["Color Distribution", "Style Analysis", "Seasonal Breakdown"])
    
    with tab1:
        st.subheader("🎨 Colors in Your Wardrobe")
        if len(wardrobe_df) > 0:
            color_counts = wardrobe_df['Color'].value_counts()
            st.bar_chart(color_counts)
            
            st.markdown("**Color Breakdown:**")
            for color, count in color_counts.items():
                st.write(f"• {color.capitalize()}: {count} items")
    
    with tab2:
        st.subheader("✨ Style Distribution")
        if len(wardrobe_df) > 0:
            style_counts = wardrobe_df['Style'].value_counts()
            st.bar_chart(style_counts)
            
            st.markdown("**Style Breakdown:**")
            for style, count in style_counts.items():
                st.write(f"• {style.capitalize()}: {count} items")
    
    with tab3:
        st.subheader("🌍 Seasonal Coverage")
        if len(wardrobe_df) > 0:
            season_counts = wardrobe_df['Season'].value_counts()
            st.bar_chart(season_counts)

# ----------------------------
# SETTINGS PAGE
# ----------------------------
elif page == "Settings":
    st.subheader("⚙️ Settings & Data Management")
    
    tab1, tab2, tab3 = st.tabs(["Export Data", "Import Data", "Database Info"])
    
    with tab1:
        st.subheader("📥 Export Your Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export Outfits (CSV)", use_container_width=True):
                csv = outfits_df.to_csv(index=False)
                st.download_button(
                    label="Download Outfits CSV",
                    data=csv,
                    file_name=f"outfits_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("👕 Export Wardrobe (CSV)", use_container_width=True):
                csv = wardrobe_df.to_csv(index=False)
                st.download_button(
                    label="Download Wardrobe CSV",
                    data=csv,
                    file_name=f"wardrobe_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        st.divider()
        
        st.subheader("📋 Quick Stats")
        stats = {
            "Total Outfits": len(outfits_df),
            "Total Wardrobe Items": len(wardrobe_df),
            "Days with Outfits": len(outfits_df['Date'].unique()) if len(outfits_df) > 0 else 0,
            "Average Rating": f"{outfits_df['Rating'].astype(float).mean():.2f}" if len(outfits_df) > 0 else "N/A"
        }
        for stat, value in stats.items():
            st.write(f"**{stat}:** {value}")
    
    with tab2:
        st.subheader("📤 Import Data")
        st.info("Import CSV files to add items to your wardrobe or outfits")
        
        wardrobe_file = st.file_uploader("Upload Wardrobe CSV", type=['csv'], key='wardrobe_import')
        if wardrobe_file:
            imported_df = pd.read_csv(wardrobe_file)
            if st.button("Confirm Import Wardrobe"):
                wardrobe_df = pd.concat([wardrobe_df, imported_df], ignore_index=True)
                wardrobe_df = wardrobe_df.drop_duplicates(subset=['Item', 'Category']).reset_index(drop=True)
                wardrobe_df.to_csv("wardrobe.csv", index=False)
                st.success("✅ Wardrobe imported successfully!")
        
        outfits_file = st.file_uploader("Upload Outfits CSV", type=['csv'], key='outfits_import')
        if outfits_file:
            imported_df = pd.read_csv(outfits_file)
            if st.button("Confirm Import Outfits"):
                outfits_df = pd.concat([outfits_df, imported_df], ignore_index=True)
                outfits_df = outfits_df.drop_duplicates(subset=['Date', 'Description']).reset_index(drop=True)
                outfits_df.to_csv("outfits.csv", index=False)
                st.success("✅ Outfits imported successfully!")
    
    with tab3:
        st.subheader("💾 Database Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Wardrobe Records", len(wardrobe_df))
            st.metric("Total Items by Category", wardrobe_df['Category'].nunique() if len(wardrobe_df) > 0 else 0)
        
        with col2:
            st.metric("Outfit Records", len(outfits_df))
            st.metric("Unique Dates", len(outfits_df['Date'].unique()) if len(outfits_df) > 0 else 0)
        
        st.divider()
        
        if st.checkbox("Show Raw Data"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Wardrobe Data")
                st.dataframe(wardrobe_df, use_container_width=True)
            
            with col2:
                st.subheader("Outfits Data")
                st.dataframe(outfits_df, use_container_width=True)
        
        st.divider()
        
        if st.button("🗑️ Clear All Data (Cannot Undo!)", help="This will delete all wardrobe and outfit data"):
            if st.checkbox("I understand this cannot be undone"):
                wardrobe_df.drop(wardrobe_df.index, inplace=True)
                outfits_df.drop(outfits_df.index, inplace=True)
                wardrobe_df.to_csv("wardrobe.csv", index=False)
                outfits_df.to_csv("outfits.csv", index=False)
                st.warning("⚠️ All data has been cleared!")

st.sidebar.markdown("---")
st.sidebar.markdown("**Outfit Designer & Tracker**")
st.sidebar.markdown("✨ *Curate your perfect wardrobe*")
