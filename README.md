# ❄️ FinPulse: End-to-End Snowflake Data Warehouse & Market Intelligence Platform

An end-to-end cloud data engineering and analytics application built on **Snowflake** and **Streamlit**, demonstrating multi-schema data warehousing, semi-structured data modeling, custom SQL User-Defined Table Functions (UDTFs), FinOps governance, and full-stack CRUD data applications.

---

## 🏗️ Architecture Overview

```text
[Market Data Sources] ──▶ [FINPULSE_DB.RAW] ──▶ [FINPULSE_DB.ANALYTICS] ──▶ [Streamlit Data App]
   (JSON / REST API)        (Stages & File         (Curated Fact Tables &       (Live UDTF Queries &
                             Formats / VARIANT)     SQL UDTFs / Secure Views)    Watchlist CRUD Forms)
                                                            │
                                                            ▼
                                               [Provider Studio / Sharing]
                                               (SECURE_MARKET_FEED_V)