
import streamlit as st
import pandas as pd
import datetime
import os
import yfinance as yf

st.set_page_config(page_title="AI Stock Advisor 🇮🇳", layout="wide")
st.title("📈 AI Stock Advisor & Position Sizer (India Edition)")

portfolio_path = "portfolio.csv"
if "portfolio" not in st.session_state:
    if os.path.exists(portfolio_path):
        st.session_state.portfolio = pd.read_csv(portfolio_path)
        st.session_state.portfolio["Date Added"] = pd.to_datetime(st.session_state.portfolio["Date Added"]).dt.date
    else:
        st.session_state.portfolio = pd.DataFrame(columns=["Stock", "Buy Price", "Quantity", "Stop Loss", "Target", "Date Added"])

def save_portfolio():
    st.session_state.portfolio.to_csv(portfolio_path, index=False)

def get_live_price(ticker):
    try:
        if not ticker.endswith(".NS"):
            ticker += ".NS"
        data = yf.Ticker(ticker).history(period="1d")
        return float(data["Close"].iloc[-1])
    except Exception:
        return None

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
        risk_amount = st.number_input("Optional: Max ₹Risk You Want to Take", min_value=0.0, format="%.2f")
        submit = st.form_submit_button("📌 Calculate Position Size")

    if submit:
        if not stock or buy_price == 0 or stop_loss == 0 or target == 0:
            st.warning("Please fill all required fields.")
        else:
            if risk_amount > 0:
                per_unit_risk = abs(buy_price - stop_loss)
                if per_unit_risk > 0:
                    quantity = int(risk_amount / per_unit_risk)
            st.session_state.portfolio.loc[len(st.session_state.portfolio)] = [
                stock, buy_price, quantity, stop_loss, target, datetime.date.today()
            ]
            save_portfolio()
            st.success(f"✅ Added {stock} to your portfolio with quantity {quantity}.")

    st.markdown("---")
    st.subheader("📤 Import Portfolio (CSV)")
    uploaded_file = st.file_uploader("Upload CSV with columns: Stock,Buy Price,Quantity,Stop Loss,Target", type=["csv"])
    if uploaded_file is not None:
        try:
            imported_df = pd.read_csv(uploaded_file)
            imported_df["Date Added"] = datetime.date.today()
            st.session_state.portfolio = pd.concat([st.session_state.portfolio, imported_df], ignore_index=True)
            save_portfolio()
            st.success("✅ Portfolio imported successfully.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

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
                live_price = get_live_price(row['Stock'])
                alert = ""
                if live_price:
                    sl_gap = abs((live_price - row["Stop Loss"]) / row["Stop Loss"])
                    target_gap = abs((live_price - row["Target"]) / row["Target"])
                    if sl_gap < 0.05:
                        alert = "⚠️ Near Stop-Loss"
                    elif target_gap < 0.05:
                        alert = "🎯 Near Target"
                price_info = f"Live ₹{live_price:.2f}" if live_price else "❌ No Price"
                st.write(f"**{row['Stock']}** | Qty: {row['Quantity']} | Buy: ₹{row['Buy Price']} | SL: ₹{row['Stop Loss']} | Target: ₹{row['Target']} | {price_info} | {alert}")
            with col2:
                delete_flags.append(st.checkbox("❌", key=f"del_{idx}"))

        if st.button("🗑️ Delete Selected"):
            for idx, flag in enumerate(delete_flags):
                if not flag:
                    updated_portfolio.append(st.session_state.portfolio.iloc[idx])
            st.session_state.portfolio = pd.DataFrame(updated_portfolio)
            save_portfolio()
            st.success("✅ Selected trade(s) removed.")

        st.markdown("---")
        st.subheader("📈 Portfolio Summary")
        total_investment = (st.session_state.portfolio["Buy Price"] * st.session_state.portfolio["Quantity"]).sum()
        total_risk = ((st.session_state.portfolio["Buy Price"] - st.session_state.portfolio["Stop Loss"]) * st.session_state.portfolio["Quantity"]).sum()
        total_gain = ((st.session_state.portfolio["Target"] - st.session_state.portfolio["Buy Price"]) * st.session_state.portfolio["Quantity"]).sum()
        st.metric("💰 Total Investment", f"₹{total_investment:,.2f}")
        st.metric("⚠️ Total Risk (if SL hit)", f"₹{total_risk:,.2f}")
        st.metric("📈 Potential Gain (if Targets met)", f"₹{total_gain:,.2f}")

        st.download_button("⬇️ Export Portfolio CSV", data=st.session_state.portfolio.to_csv(index=False), file_name="my_portfolio.csv", mime="text/csv")

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
