import streamlit as st
import pandas as pd
import os
from datetime import datetime, timezone

st.set_page_config(page_title="FinPulse | Snowflake Intelligence", layout="wide")

st.title("❄️ FinPulse: Real-Time Market Intelligence Platform")
st.caption("End-to-End Snowflake Data Warehouse • SQL UDTFs • Provider Studio • Streamlit")

# Connect to Snowflake using native Workspace connection
conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
session = conn.session()

tab1, tab2, tab3 = st.tabs([
    "📊 Market & UDTF Risk Analyzer",
    "📝 Watchlist Manager (CRUD)",
    "⚙️ FinOps & Sharing Governance"
])

# ============================================================================
# TAB 1: Read Curated Data & Query Custom SQL UDTF
# ============================================================================
with tab1:
    col_header, col_btn = st.columns([4, 1])
    with col_header:
        st.subheader("Curated Asset Metrics & Dynamic UDTF Risk Scoring")
    with col_btn:
        if st.button("🔄 Load Live Market Snapshot"):
            now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            sample_rows = [
                ("bitcoin", "BTC", "Bitcoin", 91450.00, 1810000000000.0, 42500000000.0, 3.45, now_ts),
                ("ethereum", "ETH", "Ethereum", 3120.50, 376000000000.0, 18900000000.0, -1.80, now_ts),
                ("solana", "SOL", "Solana", 215.80, 102000000000.0, 8400000000.0, 6.92, now_ts),
                ("cardano", "ADA", "Cardano", 0.78, 27500000000.0, 1250000000.0, 5.40, now_ts),
                ("avalanche-2", "AVAX", "Avalanche", 36.40, 14900000000.0, 980000000.0, -2.65, now_ts),
                ("chainlink", "LINK", "Chainlink", 15.90, 9950000000.0, 610000000.0, 1.15, now_ts),
                ("polkadot", "DOT", "Polkadot", 6.45, 9200000000.0, 430000000.0, -0.55, now_ts),
            ]
            for r in sample_rows:
                session.sql(f"""
                    INSERT INTO FINPULSE_DB.ANALYTICS.FACT_MARKET_PRICES
                    VALUES ('{r[0]}', '{r[1]}', '{r[2]}', {r[3]}, {r[4]}, {r[5]}, {r[6]}, '{r[7]}')
                """).collect()
            st.success("Loaded market snapshot into FINPULSE_DB.ANALYTICS.FACT_MARKET_PRICES!")
            st.rerun()

    min_vol = st.slider(
        "Filter Minimum 24h Trading Volume (USD) via SQL UDTF:",
        min_value=0,
        max_value=20_000_000_000,
        value=100_000_000,
        step=100_000_000,
    )

    # Query the custom User-Defined Table Function
    df_risk = session.sql(f"""
        SELECT * 
        FROM TABLE(FINPULSE_DB.ANALYTICS.GET_ASSET_RISK_PROFILE({min_vol}::FLOAT))
        ORDER BY LATEST_PRICE DESC;
    """).to_pandas()

    if not df_risk.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Tracked Assets", len(df_risk))
        m2.metric("Top Asset (BTC)", f"${df_risk.iloc[0]['LATEST_PRICE']:,.2f}", f"{df_risk.iloc[0]['CHANGE_24H_PCT']:.2f}%")
        high_vol_count = len(df_risk[df_risk["VOLATILITY_TIER"] == "HIGH_VOLATILITY"])
        m3.metric("High Volatility Alerts", high_vol_count)

        st.dataframe(df_risk, use_container_width=True)
        st.bar_chart(df_risk.set_index("SYMBOL")["CHANGE_24H_PCT"])
    else:
        st.info("Click '🔄 Load Live Market Snapshot' at the top right to populate your Snowflake table!")

# ============================================================================
# TAB 2: UI Entry Form Writing Directly to Snowflake
# ============================================================================
with tab2:
    st.subheader("Add Custom Price Alert (`FINPULSE_DB.APP_DATA.USER_WATCHLIST`)")

    with st.form("watchlist_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        user_name = c1.text_input("Analyst Name", value="Sadiq")
        symbol = c2.selectbox("Asset Symbol", ["BTC", "ETH", "SOL", "ADA", "AVAX", "LINK", "DOT"])
        alert_type = c3.selectbox("Alert Condition", ["ABOVE", "BELOW"])

        target_price = st.number_input("Target Price (USD)", min_value=0.01, value=100.00, step=10.0)
        notes = st.text_input("Strategy Notes", placeholder="e.g., Buy dip near support level")

        submitted = st.form_submit_button("Save Alert to Snowflake")
        if submitted:
            safe_user = user_name.replace("'", "''")
            safe_notes = notes.replace("'", "''")
            session.sql(f"""
                INSERT INTO FINPULSE_DB.APP_DATA.USER_WATCHLIST
                (USER_NAME, SYMBOL, TARGET_PRICE_USD, ALERT_TYPE, NOTES)
                VALUES ('{safe_user}', '{symbol}', {target_price}, '{alert_type}', '{safe_notes}')
            """).collect()
            st.success(f"Saved {symbol} {alert_type} ${target_price:,.2f} alert to Snowflake!")

    st.markdown("### Active Watchlist Table")
    df_watch = session.sql("SELECT * FROM FINPULSE_DB.APP_DATA.USER_WATCHLIST ORDER BY CREATED_AT DESC;").to_pandas()
    st.dataframe(df_watch, use_container_width=True)

# ============================================================================
# TAB 3: Showcasing FinOps & Data Sharing Governance
# ============================================================================
with tab3:
    st.subheader("Snowflake Warehouse & Secure Share Governance")
    st.markdown("""
    - **Compute Warehouse:** `FINPULSE_WH` (`XSMALL`, 60s Auto-Suspend)
    - **Resource Monitor:** `FINPULSE_MONITOR` (50 Credit Monthly Quota | Notify @ 75% | Suspend @ 90%)
    - **Marketplace / Collaboration Object:** `FINPULSE_DB.ANALYTICS.SECURE_MARKET_FEED_V`
    """)
    df_wh = session.sql("SHOW WAREHOUSES LIKE 'FINPULSE_WH';").to_pandas()
    st.dataframe(df_wh, use_container_width=True)