
import streamlit as st

# Title
st.title("📊 AI Stock Advisor & Position Sizer (India Edition)")

# Portfolio Capital and Risk Settings
st.sidebar.header("🧮 Portfolio Settings")
portfolio_capital = st.sidebar.number_input("Total Portfolio Capital (₹)", value=500000)
risk_per_trade_pct = st.sidebar.slider("Risk % per Trade", min_value=0.5, max_value=5.0, value=1.0, step=0.1)
risk_amount = portfolio_capital * (risk_per_trade_pct / 100)

# Stock Input
st.header("📥 Add Trade Candidate")
stock = st.text_input("Stock Ticker (e.g., TCS)", value="TCS")
buy_price = st.number_input("Buy Price (₹)", value=3800.0)
stop_loss = st.number_input("Stop Loss (₹)", value=3700.0)
target_price = st.number_input("Target Price (₹)", value=4050.0)

# Validate and Calculate
if st.button("🧠 Calculate Position Size"):
    if buy_price <= stop_loss:
        st.error("❌ Stop loss must be below Buy Price.")
    else:
        trade_risk = buy_price - stop_loss
        quantity = int(risk_amount / trade_risk)
        total_cost = quantity * buy_price
        expected_profit = (target_price - buy_price) * quantity
        upside_pct = ((target_price - buy_price) / buy_price) * 100

        st.success(f"✅ Recommendation for {stock}:")
        st.markdown(f"- Buy **{quantity} shares** at ₹{buy_price:.2f}")
        st.markdown(f"- Total cost: ₹{total_cost:,.2f}")
        st.markdown(f"- Risk per trade: ₹{risk_amount:,.2f} | Stop: ₹{stop_loss:.2f}")
        st.markdown(f"- Target: ₹{target_price:.2f} → Potential Upside: **{upside_pct:.2f}%**")
        st.markdown(f"- Expected Profit if Target Hit: ₹{expected_profit:,.2f}")

st.markdown("---")
st.markdown("ℹ️ This tool does not use broker APIs. You can manually enter your trade ideas and get AI-based position sizing + upside projections.")
