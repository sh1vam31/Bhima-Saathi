import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import sys

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings

st.set_page_config(page_title="Bima Saathi Dashboard", layout="wide")

@st.cache_data(ttl=60)
def load_data():
    engine = create_engine(settings.DATABASE_URL)
    
    funnel_query = """
    SELECT
      COUNT(DISTINCT c.conversation_id) AS started,
      COUNT(DISTINCT CASE WHEN t.tool='get_policy' AND t.status='success' THEN c.conversation_id END) AS policy_found,
      COUNT(DISTINCT CASE WHEN t.tool='get_renewal_quote' AND t.status='success' THEN c.conversation_id END) AS quote_shown,
      COUNT(DISTINCT CASE WHEN t.tool='create_payment_link' AND t.status='success' THEN c.conversation_id END) AS link_sent,
      COUNT(DISTINCT p.payment_link_id) AS paid
    FROM conversations c
    LEFT JOIN messages m ON m.conversation_id = c.conversation_id
    LEFT JOIN tool_calls t ON t.turn_id = m.turn_id
    LEFT JOIN payments p ON p.status = 'PAID';
    """
    
    funnel_df = pd.read_sql(funnel_query, engine)
    
    tool_error_query = """
    SELECT tool, COUNT(*) AS calls,
           ROUND(100.0 * SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) / COUNT(*), 1) AS error_pct
    FROM tool_calls 
    GROUP BY tool 
    ORDER BY error_pct DESC;
    """
    
    tool_error_df = pd.read_sql(tool_error_query, engine)
    
    return funnel_df, tool_error_df

st.title("Bima Saathi - Analytics Dashboard")

try:
    funnel_df, tool_error_df = load_data()
    
    st.header("Funnel")
    st.dataframe(funnel_df)
    
    st.header("Tool Error Rates")
    st.dataframe(tool_error_df)
    
    st.info("More charts and conversation viewer can be added here as per PRD Feature F.")
    
except Exception as e:
    st.error(f"Error loading data: {e}. Please ensure the database is initialized.")
