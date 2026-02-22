import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from collections import Counter
import json

st.set_page_config(
    page_title="Outfit Designer & Tracker", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "### Outfit Designer & Tracker\nDesign and track your personal style effortlessly!"
    }
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* General styling */
    .main {
        padding: 2rem;
    }
    
    /* Custom metric boxes */
    [data-testid="metric-container"] {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #6c63ff;
    }
    
    /* Better button styling */
    .stButton > button {
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    /* Card-like containers */
    .outfit-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Improved dividers */
    .divider {
        margin: 2rem 0;
    }
    
    /* Better titles */
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: #1f1f1f;
    }
    
    /* Color chips */
    .color-chip {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        background-color: #f0f2f6;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Page header with better styling
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.title("👔 Outfit Designer & Tracker")
    st.markdown("*Design, track, and analyze your personal style with ease*")

# ----------------------------
# Initialize Files & Session State
# ----------------------------

@st.cache_resource
def init_files():
    """Initialize CSV files if they don't exist"""
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

@st.cache_data(ttl=300)
def load_outfits():
    """Load outfits data with caching"""
    return pd.read_csv("outfits.csv")

@st.cache_data(ttl=300)
def load_wardrobe():
    """Load wardrobe data with caching"""
    return pd.read_csv("wardrobe.csv")

init_files()

outfits_df = load_outfits()
wardrobe_df = load_wardrobe()

# Ensure all required columns exist
required_wardrobe_cols = ["ID", "Category", "Item", "Color", "Style", "Season", "Times Used"]
for col in required_wardrobe_cols:
    if col not in wardrobe_df.columns:
        wardrobe_df[col] = 0 if col == "Times Used" else ""

required_outfits_cols = ["Date", "Description", "Rating", "Notes", "Weather", "Occasion", "ID"]
for col in required_outfits_cols:
    if col not in outfits_df.columns:
        outfits_df[col] = 0 if col in ["Rating", "ID"] else ""

# Convert data types
wardrobe_df["Times Used"] = pd.to_numeric(wardrobe_df["Times Used"], errors='coerce').fillna(0).astype(int)
outfits_df["Rating"] = pd.to_numeric(outfits_df["Rating"], errors='coerce').fillna(0)

# Save updated dataframes to ensure columns persist
wardrobe_df.to_csv("wardrobe.csv", index=False)
outfits_df.to_csv("outfits.csv", index=False)

# Initialize session state
if 'editing' not in st.session_state:
    st.session_state.editing = False
if 'page_refresh' not in st.session_state:
    st.session_state.page_refresh = False

# Helper functions
def get_next_item_id():
    """Get the next available item ID"""
    try:
        if len(wardrobe_df) == 0:
            return "1"
        return str(int(wardrobe_df["ID"].max()) + 1)
    except:
        return str(len(wardrobe_df) + 1)

def update_item_usage(item_id):
    """Increment usage count for an item with cache refresh"""
    try:
        wardrobe_df.loc[wardrobe_df["ID"] == str(item_id), "Times Used"] = \
            pd.to_numeric(wardrobe_df.loc[wardrobe_df["ID"] == str(item_id), "Times Used"], 
            errors='coerce').fillna(0).astype(int) + 1
        wardrobe_df.to_csv("wardrobe.csv", index=False)
        st.cache_data.clear()  # Clear cache after update
    except Exception as e:
        st.warning(f"Could not update usage: {str(e)}")

def safe_save_outfits(df):
    """Safely save outfits data"""
    try:
        df.to_csv("outfits.csv", index=False)
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Error saving outfits: {str(e)}")

def safe_save_wardrobe(df):
    """Safely save wardrobe data"""
    try:
        df.to_csv("wardrobe.csv", index=False)
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Error saving wardrobe: {str(e)}")

# Sidebar navigation with improved design
st.sidebar.markdown("---")
st.sidebar.markdown("## 📊 NAVIGATION")
st.sidebar.markdown("")

page = st.sidebar.radio(
    "Select a page:",
    ["🏠 Dashboard", "🧩 Outfit Maker", "👕 Wardrobe Manager", "📸 Outfit History", "📈 Analytics", "⚙️ Settings"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("**💡 Tips:**")
st.sidebar.info("""
• Start by adding items to your wardrobe
• Create outfits to track your style
• Rate your outfits for better insights
• Check analytics to see your trends
""")
st.sidebar.markdown("---")

# ----------------------------
# DASHBOARD PAGE
# ----------------------------
if page == "🏠 Dashboard":
    st.markdown("## Overview")
    
    # Enhanced metrics
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.metric("📌 Total Outfits", f"{len(outfits_df):,}", delta=None)
    with col2:
        st.metric("👕 Wardrobe Items", f"{len(wardrobe_df):,}", delta=None)
    with col3:
        avg_rating = outfits_df['Rating'].astype(float).mean() if 'Rating' in outfits_df.columns and len(outfits_df) > 0 else 0
        st.metric("⭐ Avg Rating", f"{avg_rating:.1f}/5" if avg_rating > 0 else "N/A", delta=None)
    with col4:
        recent_outfits = len(outfits_df[outfits_df['Date'] == str(datetime.today().date())])
        st.metric("📅 Today's Outfits", recent_outfits, delta=None)
    
    st.markdown("---")
    
    # Quick analytics
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 👕 Most Used Items")
        if len(wardrobe_df) > 0:
            top_items = wardrobe_df.nlargest(5, 'Times Used')[['Item', 'Times Used']]
            if len(top_items) > 0 and top_items['Times Used'].sum() > 0:
                st.bar_chart(top_items.set_index('Item'))
            else:
                st.info("📝 No usage data yet. Create some outfits to see trends!")
        else:
            st.info("👕 No items in your wardrobe. Add some to get started!")
    
    with col2:
        st.markdown("### ⭐ Recent High-Rated Outfits")
        if len(outfits_df) > 0 and 'Rating' in outfits_df.columns:
            try:
                high_rated = outfits_df.dropna(subset=['Rating'])
                high_rated['Rating'] = pd.to_numeric(high_rated['Rating'])
                top_outfits = high_rated.nlargest(3, 'Rating')[['Date', 'Description', 'Rating']]
                if len(top_outfits) > 0:
                    for idx, row in top_outfits.iterrows():
                        rating_stars = "⭐" * int(row['Rating'])
                        st.write(f"**{rating_stars}** {row['Date']}")
                        st.caption(f"*{row['Description']}*")
                        st.divider()
                else:
                    st.info("⭐ No rated outfits yet!")
            except:
                st.info("📊 Be the first to rate your outfits!")
        else:
            st.info("📸 No outfits recorded yet. Create one to get started!")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    
    with stat_col1:
        if len(wardrobe_df) > 0:
            most_used = wardrobe_df.nlargest(1, 'Times Used')
            if len(most_used) > 0:
                st.info(f"🔥 Most Used: {most_used.iloc[0]['Item']} ({most_used.iloc[0]['Times Used']} times)")
    
    with stat_col2:
        if len(wardrobe_df) > 0:
            categories = wardrobe_df['Category'].nunique()
            st.info(f"📂 Item Categories: {categories}")
    
    with stat_col3:
        if len(outfits_df) > 0:
            days_tracked = len(outfits_df['Date'].unique())
            st.info(f"📅 Days Tracked: {days_tracked}")

# ----------------------------
# OUTFIT MAKER PAGE
# ----------------------------
elif page == "🧩 Outfit Maker":
    st.markdown("## Create Your Outfit")
    
    # Check if wardrobe has items
    if len(wardrobe_df) == 0:
        st.warning("⚠️ You need to add items to your wardrobe first! Go to **Wardrobe Manager** to get started.")
        st.stop()
    
    # Organized selection with better layout
    st.markdown("### 👕 Select Items")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("**Tops**")
        tops = wardrobe_df[wardrobe_df["Category"] == "Top"][["ID", "Item", "Color"]].copy()
        if len(tops) > 0:
            tops_display = [f"🟡 {row['Item']} ({row['Color'].capitalize()})" for _, row in tops.iterrows()]
            selected_top_idx = st.selectbox("Select Top", range(len(tops_display)), format_func=lambda i: tops_display[i], key="top_select")
            selected_top_id = tops.iloc[selected_top_idx]["ID"]
            selected_top = tops.iloc[selected_top_idx]["Item"]
        else:
            st.info("📝 No tops in your wardrobe. Add some first!")
            st.stop()
        
        st.markdown("**Bottoms**")
        bottoms = wardrobe_df[wardrobe_df["Category"] == "Bottom"][["ID", "Item", "Color"]].copy()
        if len(bottoms) > 0:
            bottoms_display = [f"🔵 {row['Item']} ({row['Color'].capitalize()})" for _, row in bottoms.iterrows()]
            selected_bottom_idx = st.selectbox("Select Bottom", range(len(bottoms_display)), format_func=lambda i: bottoms_display[i], key="bottom_select")
            selected_bottom_id = bottoms.iloc[selected_bottom_idx]["ID"]
            selected_bottom = bottoms.iloc[selected_bottom_idx]["Item"]
        else:
            st.warning("📝 Add some bottoms to your wardrobe!")
            selected_bottom_id = None
            selected_bottom = "None"
    
    with col2:
        st.markdown("**Shoes**")
        shoes = wardrobe_df[wardrobe_df["Category"] == "Shoes"][["ID", "Item", "Color"]].copy()
        if len(shoes) > 0:
            shoes_display = [f"👟 {row['Item']} ({row['Color'].capitalize()})" for _, row in shoes.iterrows()]
            selected_shoes_idx = st.selectbox("Select Shoes", range(len(shoes_display)), format_func=lambda i: shoes_display[i], key="shoes_select")
            selected_shoes_id = shoes.iloc[selected_shoes_idx]["ID"]
            selected_shoes = shoes.iloc[selected_shoes_idx]["Item"]
        else:
            st.info("📝 No shoes in your wardrobe")
            selected_shoes = "None"
            selected_shoes_id = None
        
        st.markdown("**Accessories**")
        accessories = wardrobe_df[wardrobe_df["Category"] == "Accessory"][["ID", "Item", "Color"]].copy()
        if len(accessories) > 0:
            acc_display = [f"✨ {row['Item']} ({row['Color'].capitalize()})" for _, row in accessories.iterrows()]
            selected_acc_idx = st.selectbox("Select Accessory", range(len(acc_display)), format_func=lambda i: acc_display[i], key="acc_select")
            selected_acc_id = accessories.iloc[selected_acc_idx]["ID"]
            selected_accessory = accessories.iloc[selected_acc_idx]["Item"]
        else:
            st.info("📝 No accessories in your wardrobe")
            selected_accessory = "None"
            selected_acc_id = None
    
    st.markdown("---")
    
    # Outfit context
    st.markdown("### 🎯 Outfit Context")
    
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        occasion = st.selectbox("📍 Occasion", ["Casual", "Work", "Evening", "Sport", "Party", "Gym", "Dinner", "Other"], key="occasion_select")
        weather = st.selectbox("🌤️ Weather", ["Sunny", "Rainy", "Snowy", "Cloudy", "Hot", "Cold", "Windy", "Other"], key="weather_select")
    with col2:
        notes = st.text_area("📝 Notes", placeholder="Add notes about this outfit (colors, comfort, mood, etc.)", height=95, key="notes_input")
    
    st.markdown("---")
    
    # Outfit Preview with Enhanced Styling
    st.markdown("### 👗 Outfit Preview")
    
    description = f"{selected_top} + {selected_bottom} + {selected_shoes} + {selected_accessory}"
    
    preview_container = st.container(border=True)
    with preview_container:
        col1, col2, col3 = preview_container.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
                <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; color: white;'>
                    <h3>✨ Your Outfit Preview ✨</h3>
                    <p style='font-size: 1.1em; margin-top: 20px;'>{selected_top.upper()}</p>
                    <p style='font-size: 1.1em;'>+ {selected_bottom.upper()}</p>
                    <p style='font-size: 1.1em;'>+ {selected_shoes.upper()}</p>
                    <p style='font-size: 1.1em;'>+ {selected_accessory.upper()}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Save button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Save This Outfit", use_container_width=True, type="primary"):
            try:
                new_id = str(int(outfits_df['ID'].max()) + 1) if len(outfits_df) > 0 else "1"
                new_data = pd.DataFrame([[
                    str(datetime.today().date()), 
                    description,
                    0,
                    notes,
                    weather,
                    occasion,
                    new_id
                ]], columns=["Date", "Description", "Rating", "Notes", "Weather", "Occasion", "ID"])
                
                outfits_df = pd.concat([outfits_df, new_data], ignore_index=True)
                safe_save_outfits(outfits_df)
                
                # Update usage stats for all selected items
                item_ids = [selected_top_id, selected_bottom_id, selected_shoes_id, selected_acc_id]
                for item_id in item_ids:
                    if item_id and pd.notna(item_id):
                        update_item_usage(str(item_id))
                
                st.success(f"✅ Outfit saved! ({occasion}, {weather}) - Outfit #**{new_id}**")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error saving outfit: {str(e)}")

# ----------------------------
# WARDROBE MANAGER PAGE
# ----------------------------
elif page == "👕 Wardrobe Manager":
    st.markdown("## Manage Your Wardrobe")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Item", "👁️ View Items", "🛠️ Edit Items"])
    
    with tab1:
        st.markdown("### Add New Clothing Item")
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            category = st.selectbox("📦 Category", ["Top", "Bottom", "Shoes", "Accessory", "Outerwear", "Jacket", "Dress", "Other"], key="add_category")
            new_item = st.text_input("👗 Item Name", placeholder="e.g., Blue V-Neck T-Shirt, Black Jeans", key="item_name")
            color = st.text_input("🎨 Color", placeholder="e.g., Blue, Sage Green, Navy", key="item_color")
        
        with col2:
            style = st.selectbox("✨ Style", ["Casual", "Formal", "Sport", "Vintage", "Bohemian", "Minimalist", "Streetwear", "Other"], key="item_style")
            season = st.selectbox("🌍 Season", ["Year-round", "Spring", "Summer", "Fall", "Winter", "Summer/Winter"], key="item_season")
            condition = st.selectbox("📊 Condition", ["Like New", "Good", "Fair", "Need Repair"], key="item_condition")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Add Item to Wardrobe", use_container_width=True, type="primary"):
                if new_item.strip():
                    try:
                        new_id = get_next_item_id()
                        new_row = pd.DataFrame([[new_id, category, new_item.strip(), color.lower().strip(), style.lower(), season, 0]],
                                               columns=["ID", "Category", "Item", "Color", "Style", "Season", "Times Used"])
                        wardrobe_df_updated = pd.concat([wardrobe_df, new_row], ignore_index=True)
                        safe_save_wardrobe(wardrobe_df_updated)
                        st.success(f"✅ {new_item} added to {category}! (ID: {new_id})")
                    except Exception as e:
                        st.error(f"❌ Error adding item: {str(e)}")
                else:
                    st.warning("⚠️ Please enter an item name.")
    
    with tab2:
        st.markdown("### Your Wardrobe Items")
        
        # Filter options with better layout
        col1, col2, col3 = st.columns(3, gap="small")
        with col1:
            categories = ["All"] + sorted(wardrobe_df["Category"].dropna().unique().tolist())
            filter_category = st.selectbox("📦 Filter by Category", categories, key="filter_cat")
        with col2:
            colors = ["All"] + sorted([c for c in wardrobe_df["Color"].dropna().unique().tolist() if c])
            filter_color = st.selectbox("🎨 Filter by Color", colors, key="filter_col")
        with col3:
            styles = ["All"] + sorted([s for s in wardrobe_df["Style"].dropna().unique().tolist() if s])
            filter_style = st.selectbox("✨ Filter by Style", styles, key="filter_sty")
        
        # Apply filters
        filtered_df = wardrobe_df.copy()
        if filter_category != "All":
            filtered_df = filtered_df[filtered_df["Category"] == filter_category]
        if filter_color != "All":
            filtered_df = filtered_df[filtered_df["Color"] == filter_color]
        if filter_style != "All":
            filtered_df = filtered_df[filtered_df["Style"] == filter_style]
        
        st.markdown("---")
        
        # Display wardrobe with enhanced styling
        if len(filtered_df) > 0:
            # Create a more visual display
            for idx, (_, row) in enumerate(filtered_df.iterrows()):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"""
                    <div style='padding: 12px; background-color: #f0f2f6; border-left: 4px solid #667eea; border-radius: 6px;'>
                        <strong>{row['Item']}</strong><br>
                        📦 {row['Category']} | 🎨 {row['Color'].capitalize()} | ✨ {row['Style'].capitalize()} | 🌍 {row['Season']}<br>
                        <small>🔧 ID: {row['ID']} | Used: {row['Times Used']}x</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.metric("Usage", row['Times Used'], label_visibility="collapsed")
                with col3:
                    st.caption("_")  # Spacing
            
            st.markdown("---")
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("📊 Items Shown", len(filtered_df))
            with metric_col2:
                total_usage = filtered_df['Times Used'].sum()
                st.metric("🔥 Total Uses", total_usage)
            with metric_col3:
                avg_condition = len(filtered_df)
                st.metric("📈 Count", len(filtered_df))
        else:
            st.info("No items match your filter criteria")
    
    with tab3:
        st.markdown("### Edit or Remove Items")
        
        if len(wardrobe_df) > 0:
            item_names = [f"[{row['ID']}] {row['Item']} ({row['Color'].capitalize()})" for _, row in wardrobe_df.iterrows()]
            item_to_manage = st.selectbox("🔍 Select item to manage", item_names, key="manage_select")
            
            selected_idx = wardrobe_df.index[0]
            for idx, name in enumerate(item_names):
                if name == item_to_manage:
                    selected_idx = idx
                    break
            
            selected_item = wardrobe_df.iloc[selected_idx]
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3, gap="small")
            with col1:
                if st.button("🗑️ Delete Item", use_container_width=True, key="delete_btn"):
                    wardrobe_df_updated = wardrobe_df.drop(selected_idx).reset_index(drop=True)
                    safe_save_wardrobe(wardrobe_df_updated)
                    st.success(f"✅ {selected_item['Item']} deleted from wardrobe!")
                    st.rerun()
            
            with col2:
                if st.button("✏️ Edit Item", use_container_width=True, key="edit_btn"):
                    st.session_state.editing = True
            
            with col3:
                st.caption(f"ID: {selected_item['ID']}")
            
            if st.session_state.get('editing', False):
                st.markdown("---")
                st.markdown("### Edit Item Details")
                
                col1, col2 = st.columns(2, gap="medium")
                with col1:
                    new_color = st.text_input("🎨 Color", value=selected_item['Color'].capitalize(), key="edit_color")
                    new_style = st.selectbox("✨ Style", 
                        ["Casual", "Formal", "Sport", "Vintage", "Bohemian", "Minimalist", "Streetwear", "Other"],
                        index=["Casual", "Formal", "Sport", "Vintage", "Bohemian", "Minimalist", "Streetwear", "Other"].index(selected_item['Style'].capitalize()) if selected_item['Style'].capitalize() in ["Casual", "Formal", "Sport", "Vintage", "Bohemian", "Minimalist", "Streetwear", "Other"] else 0,
                        key="edit_style")
                
                with col2:
                    new_season = st.selectbox("🌍 Season", 
                        ["Year-round", "Spring", "Summer", "Fall", "Winter", "Summer/Winter"],
                        index=["Year-round", "Spring", "Summer", "Fall", "Winter", "Summer/Winter"].index(selected_item['Season']) if selected_item['Season'] in ["Year-round", "Spring", "Summer", "Fall", "Winter", "Summer/Winter"] else 0,
                        key="edit_season")
                    new_usage = st.number_input("Times Used", value=int(selected_item['Times Used']), min_value=0, key="edit_usage")
                
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("💾 Save Changes", use_container_width=True, type="primary"):
                        wardrobe_df.loc[selected_idx, 'Color'] = new_color.lower()
                        wardrobe_df.loc[selected_idx, 'Style'] = new_style.lower()
                        wardrobe_df.loc[selected_idx, 'Season'] = new_season
                        wardrobe_df.loc[selected_idx, 'Times Used'] = new_usage
                        safe_save_wardrobe(wardrobe_df)
                        st.success("✅ Item updated successfully!")
                        st.session_state.editing = False
                        st.rerun()
        else:
            st.info("👕 Your wardrobe is empty. Add items using the 'Add Item' tab!")

# ----------------------------
# OUTFIT HISTORY PAGE
# ----------------------------
elif page == "📸 Outfit History":
    st.markdown("## Outfit History")
    
    if len(outfits_df) == 0:
        st.info("📸 No outfits recorded yet. Go to **Outfit Maker** to create your first outfit!")
    else:
        # Filter options with better layout
        col1, col2, col3 = st.columns(3, gap="medium")
        with col1:
            occasions = ["All"] + (outfits_df["Occasion"].unique().tolist() if "Occasion" in outfits_df.columns else [])
            filter_occasion = st.selectbox("🎯 Filter by Occasion", occasions, key="hist_occ")
        with col2:
            weathers = ["All"] + (outfits_df["Weather"].unique().tolist() if "Weather" in outfits_df.columns else [])
            filter_weather = st.selectbox("🌤️ Filter by Weather", weathers, key="hist_wea")
        with col3:
            sort_by = st.selectbox("📊 Sort by", ["Recent First", "Oldest First", "Highest Rated", "Most Popular"], key="hist_sort")
        
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
        
        st.markdown("---")
        
        # Display outfits with enhanced styling
        if len(display_df) > 0:
            for index, row in display_df.iterrows():
                # Create outfit card
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2.5, 1, 0.8, 0.7])
                    
                    with col1:
                        st.markdown(f"### 📅 {row['Date']}")
                        st.markdown(f"**{row['Description']}**")
                        st.markdown(f"🎯 **{row.get('Occasion', 'N/A')}** | 🌤️ **{row.get('Weather', 'N/A')}**")
                        
                        if pd.notna(row.get('Notes', '')) and row.get('Notes', '') != '':
                            st.caption(f"📝 {row['Notes']}")
                    
                    with col2:
                        # Rating
                        current_rating = float(row.get('Rating', 0)) if pd.notna(row.get('Rating', 0)) else 0
                        new_rating = st.selectbox(f"⭐ Rate", range(0, 6), value=int(current_rating), key=f"rating_{index}", label_visibility="collapsed")
                        if new_rating != current_rating:
                            outfits_df.loc[outfits_df['ID'] == row['ID'], 'Rating'] = new_rating
                            safe_save_outfits(outfits_df)
                            st.rerun()
                        
                        # Show star rating visually
                        if new_rating > 0:
                            st.caption("⭐" * int(new_rating))
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_{index}", use_container_width=True):
                            outfits_df_updated = outfits_df.drop(index).reset_index(drop=True)
                            safe_save_outfits(outfits_df_updated)
                            st.success("✅ Outfit deleted!")
                            st.rerun()
            
            st.markdown("---")
            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Showing", len(display_df))
            with col2:
                avg_rating = display_df['Rating'].astype(float).mean() if len(display_df) > 0 else 0
                st.metric("⭐ Avg Rating", f"{avg_rating:.1f}/5" if avg_rating > 0 else "N/A")
            with col3:
                most_common_occ = display_df['Occasion'].mode()[0] if len(display_df) > 0 and 'Occasion' in display_df.columns else "N/A"
                st.metric("🎯 Most Common", most_common_occ)
            with col4:
                most_common_wea = display_df['Weather'].mode()[0] if len(display_df) > 0 and 'Weather' in display_df.columns else "N/A"
                st.metric("🌤️ Most Common", most_common_wea)
        else:
            st.warning("⚠️ No outfits match your filter criteria")

# ----------------------------
# ANALYTICS PAGE
# ----------------------------
elif page == "📈 Analytics":
    st.markdown("## Wardrobe Analytics & Insights")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        st.metric("📌 Total Outfits", f"{len(outfits_df):,}", delta=None)
    with col2:
        st.metric("👕 Wardrobe Size", f"{len(wardrobe_df):,}", delta=None)
    with col3:
        avg_rating = outfits_df['Rating'].astype(float).mean() if 'Rating' in outfits_df.columns and len(outfits_df) > 0 else 0
        st.metric("⭐ Average Rating", f"{avg_rating:.2f}/5" if avg_rating > 0 else "N/A", delta=None)
    with col4:
        days_tracked = len(outfits_df['Date'].unique()) if len(outfits_df) > 0 else 0
        st.metric("📅 Days Tracked", f"{days_tracked:,}", delta=None)
    
    st.markdown("---")
    
    # Charts with better layout
    chart_col1, chart_col2 = st.columns(2, gap="large")
    
    with chart_col1:
        st.markdown("### 👕 Most Used Items")
        if len(wardrobe_df) > 0:
            top_items = wardrobe_df.nlargest(10, 'Times Used')
            if len(top_items) > 0 and top_items['Times Used'].sum() > 0:
                st.bar_chart(top_items.set_index('Item')['Times Used'], use_container_width=True)
            else:
                st.info("📝 No usage data yet. Create some outfits!")
        else:
            st.info("👕 Add items to your wardrobe to see analytics")
    
    with chart_col2:
        st.markdown("### 📂 Items by Category")
        if len(wardrobe_df) > 0:
            category_counts = wardrobe_df['Category'].value_counts()
            st.bar_chart(category_counts, use_container_width=True)
        else:
            st.info("👕 No items in wardrobe yet")
    
    st.markdown("---")
    
    # Tabs for detailed analytics
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Colors", "✨ Styles", "🌍 Seasons", "🎯 Occasions"])
    
    with tab1:
        st.markdown("### Color Distribution")
        if len(wardrobe_df) > 0:
            color_counts = wardrobe_df['Color'].value_counts()
            col1, col2 = st.columns([2, 1])
            with col1:
                st.bar_chart(color_counts, use_container_width=True)
            with col2:
                st.markdown("**Color Breakdown:**")
                for color, count in color_counts.items():
                    st.write(f"• {color.capitalize()}: {count}")
        else:
            st.info("No color data available")
    
    with tab2:
        st.markdown("### Style Distribution")
        if len(wardrobe_df) > 0:
            style_counts = wardrobe_df['Style'].value_counts()
            col1, col2 = st.columns([2, 1])
            with col1:
                st.bar_chart(style_counts, use_container_width=True)
            with col2:
                st.markdown("**Style Breakdown:**")
                for style, count in style_counts.items():
                    st.write(f"• {style.capitalize()}: {count}")
        else:
            st.info("No style data available")
    
    with tab3:
        st.markdown("### Seasonal Coverage")
        if len(wardrobe_df) > 0:
            season_counts = wardrobe_df['Season'].value_counts()
            col1, col2 = st.columns([2, 1])
            with col1:
                st.bar_chart(season_counts, use_container_width=True)
            with col2:
                st.markdown("**Seasonal Breakdown:**")
                for season, count in season_counts.items():
                    st.write(f"• {season}: {count}")
        else:
            st.info("No seasonal data available")
    
    with tab4:
        st.markdown("### Occasions & Weather")
        if len(outfits_df) > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Occasions Used:**")
                occasion_counts = outfits_df['Occasion'].value_counts() if 'Occasion' in outfits_df.columns else pd.Series()
                if len(occasion_counts) > 0:
                    for occasion, count in occasion_counts.items():
                        st.write(f"🎯 {occasion}: {count}")
                else:
                    st.info("No occasion data")
            with col2:
                st.markdown("**Weather Conditions:**")
                weather_counts = outfits_df['Weather'].value_counts() if 'Weather' in outfits_df.columns else pd.Series()
                if len(weather_counts) > 0:
                    for weather, count in weather_counts.items():
                        st.write(f"🌤️ {weather}: {count}")
                else:
                    st.info("No weather data")

# ----------------------------
# SETTINGS PAGE
# ----------------------------
elif page == "⚙️ Settings":
    st.markdown("## Settings & Data Management")
    
    tab1, tab2, tab3 = st.tabs(["💾 Export Data", "📤 Import Data", "ℹ️ Database Info"])
    
    with tab1:
        st.markdown("### Export Your Data")
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("#### 📊 Export Outfits")
            if st.button("Download Outfits (CSV)", use_container_width=True, type="primary"):
                csv = outfits_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Outfits CSV",
                    data=csv,
                    file_name=f"outfits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            st.caption(f"Records: {len(outfits_df)}")
        
        with col2:
            st.markdown("#### 👕 Export Wardrobe")
            if st.button("Download Wardrobe (CSV)", use_container_width=True, type="primary"):
                csv = wardrobe_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Wardrobe CSV",
                    data=csv,
                    file_name=f"wardrobe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            st.caption(f"Records: {len(wardrobe_df)}")
        
        st.markdown("---")
        
        st.markdown("### 📋 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"""
            **📊 Outfits:** {len(outfits_df)}
            **👕 Wardrobe Items:** {len(wardrobe_df)}
            **📅 Days Tracked:** {len(outfits_df['Date'].unique()) if len(outfits_df) > 0 else 0}
            """)
        with col2:
            avg_rating = outfits_df['Rating'].astype(float).mean() if len(outfits_df) > 0 else 0
            st.info(f"""
            **⭐ Average Rating:** {f'{avg_rating:.2f}/5' if avg_rating > 0 else 'N/A'}
            **🔥 Categories:** {wardrobe_df['Category'].nunique() if len(wardrobe_df) > 0 else 0}
            **🎨 Colors:** {wardrobe_df['Color'].nunique() if len(wardrobe_df) > 0 else 0}
            """)
    
    with tab2:
        st.markdown("### Import Data")
        st.info("💡 Import CSV files to add items to your wardrobe or outfits. Duplicates will be skipped.")
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("#### 👕 Import Wardrobe")
            wardrobe_file = st.file_uploader("Upload Wardrobe CSV", type=['csv'], key='wardrobe_import', label_visibility="collapsed")
            if wardrobe_file:
                try:
                    imported_df = pd.read_csv(wardrobe_file)
                    st.success(f"✅ {len(imported_df)} items ready to import")
                    if st.button("Confirm Import Wardrobe", use_container_width=True, type="primary"):
                        wardrobe_df_updated = pd.concat([wardrobe_df, imported_df], ignore_index=True)
                        wardrobe_df_updated = wardrobe_df_updated.drop_duplicates(subset=['Item', 'Category']).reset_index(drop=True)
                        safe_save_wardrobe(wardrobe_df_updated)
                        st.success("✅ Wardrobe imported successfully!")
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
        
        with col2:
            st.markdown("#### 📸 Import Outfits")
            outfits_file = st.file_uploader("Upload Outfits CSV", type=['csv'], key='outfits_import', label_visibility="collapsed")
            if outfits_file:
                try:
                    imported_df = pd.read_csv(outfits_file)
                    st.success(f"✅ {len(imported_df)} outfits ready to import")
                    if st.button("Confirm Import Outfits", use_container_width=True, type="primary"):
                        outfits_df_updated = pd.concat([outfits_df, imported_df], ignore_index=True)
                        outfits_df_updated = outfits_df_updated.drop_duplicates(subset=['Date', 'Description']).reset_index(drop=True)
                        safe_save_outfits(outfits_df_updated)
                        st.success("✅ Outfits imported successfully!")
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
    
    with tab3:
        st.markdown("### Database Information")
        
        col1, col2 = st.columns(2, gap="medium")
        
        with col1:
            st.markdown("#### 👕 Wardrobe Data")
            st.metric("Total Records", len(wardrobe_df))
            st.metric("Categories", wardrobe_df['Category'].nunique() if len(wardrobe_df) > 0 else 0)
            st.metric("Colors", wardrobe_df['Color'].nunique() if len(wardrobe_df) > 0 else 0)
            st.metric("Styles", wardrobe_df['Style'].nunique() if len(wardrobe_df) > 0 else 0)
        
        with col2:
            st.markdown("#### 📸 Outfit Data")
            st.metric("Total Records", len(outfits_df))
            st.metric("Unique Dates", len(outfits_df['Date'].unique()) if len(outfits_df) > 0 else 0)
            st.metric("Occasions", outfits_df['Occasion'].nunique() if len(outfits_df) > 0 and 'Occasion' in outfits_df.columns else 0)
            st.metric("Weather Types", outfits_df['Weather'].nunique() if len(outfits_df) > 0 and 'Weather' in outfits_df.columns else 0)
        
        st.markdown("---")
        
        if st.checkbox("👀 Show Raw Data"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Wardrobe Data")
                st.dataframe(wardrobe_df, use_container_width=True, height=300)
            
            with col2:
                st.markdown("### Outfits Data")
                st.dataframe(outfits_df, use_container_width=True, height=300)
        
        st.markdown("---")
        
        st.markdown("### ⚠️ Danger Zone")
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.checkbox("I understand this action is permanent"):
                if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
                    wardrobe_df_cleared = wardrobe_df.drop(wardrobe_df.index, inplace=False)
                    outfits_df_cleared = outfits_df.drop(outfits_df.index, inplace=False)
                    safe_save_wardrobe(wardrobe_df_cleared)
                    safe_save_outfits(outfits_df_cleared)
                    st.warning("⚠️ All data has been cleared!")
                    st.rerun()
        with col2:
            st.caption("⚠️ Cannot undo")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem; color: #666;'>
    <p><strong>Outfit Designer & Tracker</strong></p>
    <p>✨ <em>Curate your perfect wardrobe</em> ✨</p>
    <p style='font-size: 0.8rem; margin-top: 1rem;'>Version 2.0 | Enhanced UI/UX</p>
</div>
""", unsafe_allow_html=True)
