q
import streamlit as st
import pandas as pd

# Initialize session state for portfolio tracking
if "portfolio" not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=[
        "Stock", "Buy Price", "Quantity", "Stop Loss", "Target", "Status"
    ])

# Sidebar settings
st.sidebar.header("🧮 Portfolio Settings")
portfolio_capital = st.sidebar.number_input("Total Portfolio Capital (₹)", value=500000)
risk_per_trade_pct = st.sidebar.slider("Risk % per Trade", min_value=0.5, max_value=5.0, value=1.0, step=0.1)
risk_amount = portfolio_capital * (risk_per_trade_pct / 100)

# Tab layout
tab1, tab2 = st.tabs(["📥 Add Trade", "📊 Portfolio & AI Picks"])

# --- Tab 1: Add Trade ---
with tab1:
    st.header("📥 Add Trade Candidate")
    stock = st.text_input("Stock Ticker (e.g., TCS)", value="TCS")
    buy_price = st.number_input("Buy Price (₹)", value=3800.0)
    stop_loss = st.number_input("Stop Loss (₹)", value=3700.0)
    target_price = st.number_input("Target Price (₹)", value=4050.0)

    if st.button("🧠 Calculate & Add to Portfolio"):
        if buy_price <= stop_loss:
            st.error("❌ Stop loss must be below Buy Price.")
        else:
            trade_risk = buy_price - stop_loss
            quantity = int(risk_amount / trade_risk)
            total_cost = quantity * buy_price
            expected_profit = (target_price - buy_price) * quantity
            upside_pct = ((target_price - buy_price) / buy_price) * 100

            # Append to portfolio
            new_trade = {
                "Stock": stock.upper(),
                "Buy Price": buy_price,
                "Quantity": quantity,
                "Stop Loss": stop_loss,
                "Target": target_price,
                "Status": "Active"
            }
            st.session_state.portfolio = pd.concat(
                [st.session_state.portfolio, pd.DataFrame([new_trade])],
                ignore_index=True
            )

            st.success(f"Added {stock.upper()} to your portfolio!")
            st.markdown(f"- Buy **{quantity} shares** at ₹{buy_price:.2f}")
            st.markdown(f"- Total cost: ₹{total_cost:,.2f}")
            st.markdown(f"- Target: ₹{target_price:.2f} → Upside: **{upside_pct:.2f}%**")
            st.markdown(f"- Expected Profit: ₹{expected_profit:,.2f}")

# --- Tab 2: Portfolio + AI Picks ---
with tab2:
    st.header("📊 Your Portfolio")
if not st.session_state.portfolio.empty:
    portfolio_df = st.session_state.portfolio.copy()
    portfolio_df["Select"] = False

    selected_indices = st.multiselect("Select trades to remove", portfolio_df.index, format_func=lambda i: f"{portfolio_df.loc[i, 'Stock']}")

    if st.button("🗑️ Delete Selected"):
        st.session_state.portfolio.drop(index=selected_indices, inplace=True)
        st.success(f"Deleted {len(selected_indices)} trade(s) from portfolio.")

    st.dataframe(st.session_state.portfolio.reset_index(drop=True), use_container_width=True)
else:
    st.info("No trades added yet. Use the 'Add Trade' tab to get started.")
    if not st.session_state.portfolio.empty:
        st.dataframe(st.session_state.portfolio, use_container_width=True)
    else:
        st.info("No trades added yet. Use the 'Add Trade' tab to get started.")

    st.markdown("---")
    st.header("🤖 Live AI Trade Ideas")

    try:
        ai_picks = pd.read_csv("live_ai_picks.csv")
        st.dataframe(ai_picks, use_container_width=True)
    except FileNotFoundError:
        st.warning("⚠️ No live AI picks file found. Please run the CSV generator script to populate live_ai_picks.csv.")
