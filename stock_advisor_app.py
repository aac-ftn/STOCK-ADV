
import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Stock Advisor 🇮🇳", layout="wide")
st.title("📈 AI Stock Advisor & Position Sizer (India Edition)")

# --- Session Storage ---
if "portfolio" not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=["Stock", "Buy Price", "Quantity", "Stop Loss", "Target"])

# --- Tabs ---
tab1, tab2 = st.tabs(["📥 Add Trade", "📊 Portfolio & AI Picks"])

# --- Tab 1: Add Trade Form ---
with tab1:
    st.header("➕ Add Trade Candidate")
    with st.form("trade_form"):
        stock = st.text_input("Stock Ticker (e.g., TCS)").upper()
        buy_price = st.number_input("Buy Price (₹)", min_value=0.0, format="%.2f")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        stop_loss = st.number_input("Stop Loss (₹)", min_value=0.0, format="%.2f")
        target = st.number_input("Target Price (₹)", min_value=0.0, format="%.2f")
        submit = st.form_submit_button("📌 Calculate Position Size")

    if submit:
        if not stock or buy_price == 0 or stop_loss == 0 or target == 0:
            st.warning("Please fill all fields.")
        else:
            st.session_state.portfolio.loc[len(st.session_state.portfolio)] = [stock, buy_price, quantity, stop_loss, target]
            st.success(f"✅ Added {stock} to your portfolio.")

# --- Tab 2: Portfolio and AI Picks ---
with tab2:
    st.header("📊 Your Portfolio")

    if not st.session_state.portfolio.empty:
        updated_portfolio = []
        delete_flags = []

        st.write("### Select Trades to Remove")
        for idx, row in st.session_state.portfolio.iterrows():
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(f"**{row['Stock']}** | Qty: {row['Quantity']} | Buy: ₹{row['Buy Price']} | SL: ₹{row['Stop Loss']} | Target: ₹{row['Target']}")
            with col2:
                delete_flags.append(st.checkbox("❌", key=f"del_{idx}"))

        if st.button("🗑️ Delete Selected"):
            for idx, flag in enumerate(delete_flags):
                if not flag:
                    updated_portfolio.append(st.session_state.portfolio.iloc[idx])
            st.session_state.portfolio = pd.DataFrame(updated_portfolio)
            st.success("✅ Selected trade(s) removed.")

        st.markdown("---")
        st.dataframe(st.session_state.portfolio.reset_index(drop=True), use_container_width=True)
    else:
        st.info("No trades added yet. Use the 'Add Trade' tab to get started.")

    st.markdown("---")
    st.header("🤖 Live AI Trade Ideas")

    try:
        ai_picks = pd.read_csv("live_ai_picks.csv")
        st.dataframe(ai_picks, use_container_width=True)
    except FileNotFoundError:
        st.warning("⚠️ No live AI picks file found. Please run the CSV generator script to populate live_ai_picks.csv.")
