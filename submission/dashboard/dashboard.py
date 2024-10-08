import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
import pandas as pd
import os

# Set Matplotlib backend
import matplotlib
matplotlib.use('Agg')

sns.set(style='dark')

# Use relative path or environment variable
data_path = os.environ.get('DATA_PATH', 'main_data.csv')
all_df = pd.read_csv(data_path)

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date", "order_approved_at"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True, drop=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

def create_daily_orders_df(df):
    daily_orders_df = df.set_index('order_purchase_timestamp').resample(rule='D').agg({
        "order_id": "nunique",
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
    }, inplace=True)
    
    return daily_orders_df 

def plot_bar_chart(df):
    state_counts = df['customer_state'].value_counts()
    fig, ax = plt.subplots()
    state_counts.plot(kind='bar', ax=ax)
    ax.set_xlabel('State')
    ax.set_ylabel('Number of Customers')
    ax.set_title('Number of Customers by State')
    st.pyplot(fig)

def plot_pie_chart(df):
    if 'delivered_on_time' not in df.columns:
        st.warning("Column 'delivered_on_time' not found in the DataFrame")
        return
    on_time_count = df['delivered_on_time'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(on_time_count, labels=on_time_count.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    ax.set_title('Delivery On Time Ratio')
    st.pyplot(fig)

st.header('E-Commerce Dashboard 🛒')

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Use relative path or environment variable for logo
    logo_path = os.environ.get('LOGO_PATH', 'logo.png')
    st.image(logo_path)
    
    st.header("Filter by Date :spiral_calendar_pad:")
    start_date, end_date = st.date_input(
        label='Date Range',
        min_value=min_date.date(),
        max_value=max_date.date(),
        value=[min_date.date(), max_date.date()]
    )

main_df = all_df[(all_df["order_purchase_timestamp"].dt.date >= start_date) & 
                 (all_df["order_purchase_timestamp"].dt.date <= end_date)]

daily_orders_df = create_daily_orders_df(main_df)

st.subheader('Penjualan Harian')
total_orders = daily_orders_df.order_count.sum()
st.metric("Total orders", value=total_orders)

st.subheader('Trend Penjualan')
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

map_data = main_df.dropna(subset=['geolocation_lat', 'geolocation_lng'])
map_data = map_data.rename(columns={'geolocation_lat': 'latitude', 'geolocation_lng': 'longitude'})

st.subheader('Peta Persebaran Penjualan')
st.map(map_data)

st.subheader('Number of Customers by State:')
plot_bar_chart(main_df)

st.subheader('Delivery On Time Ratio:')
plot_pie_chart(main_df)

st.caption('Copyright (C) Kaltralala 2024')