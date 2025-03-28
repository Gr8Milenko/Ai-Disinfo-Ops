import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# --- Trend Analysis ---
def plot_confidence_trend(df: pd.DataFrame):
    df['date'] = df['datetime'].dt.date
    daily_avg = df.groupby('date')['confidence'].mean().reset_index()

    st.subheader("Average Confidence Over Time")
    fig, ax = plt.subplots()
    ax.plot(daily_avg['date'], daily_avg['confidence'], marker='o')
    ax.set_xlabel("Date")
    ax.set_ylabel("Average Confidence")
    ax.set_title("Confidence Score Trend")
    st.pyplot(fig)

# --- Disinfo Counts Over Time ---
def plot_disinfo_volume(df: pd.DataFrame):
    df['date'] = df['datetime'].dt.date
    daily_counts = df[df['flagged']].groupby('date').size().reset_index(name='count')

    st.subheader("Flagged Disinformation Over Time")
    fig, ax = plt.subplots()
    ax.bar(daily_counts['date'], daily_counts['count'])
    ax.set_xlabel("Date")
    ax.set_ylabel("Flagged Entries")
    ax.set_title("Disinformation Volume Trend")
    st.pyplot(fig)

# --- Type Breakdown Pie Chart ---
def plot_type_distribution(df: pd.DataFrame):
    st.subheader("Distribution by Type")
    type_counts = df['type'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%')
    ax.set_title("Content Type Breakdown")
    st.pyplot(fig)
