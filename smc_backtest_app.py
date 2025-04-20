import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set page config first!
st.set_page_config(page_title="SMC Backtesting App", layout="wide")
st.title("💹 SMC Strategy Backtesting App")

# File uploader
uploaded_file = st.file_uploader("📂 Upload your EURUSD data (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Detect file type
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ Data Loaded Successfully!")
        st.dataframe(df.head(50))  # Preview the first 50 rows

        # Clean up column names
        df.columns = [col.lower().strip() for col in df.columns]

        # Expected columns
        expected_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

        if all(col in df.columns for col in expected_cols):
            try:
                # Safe timestamp parsing
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df = df.dropna(subset=['timestamp'])
                df = df.sort_values('timestamp')

                if df.empty:
                    st.error("❌ No valid 'timestamp' values found after parsing.")
                else:
                    # --- Date Range Selection ---
                    st.subheader("📅 Select Date Range for Chart")

                    default_start = df['timestamp'].iloc[-min(500, len(df))].date()
                    default_end = df['timestamp'].iloc[-1].date()

                    start_date = st.date_input("Start Date", default_start)
                    end_date = st.date_input("End Date", default_end)

                    # Filter data by date
                    mask = (df['timestamp'] >= pd.to_datetime(start_date)) & (df['timestamp'] <= pd.to_datetime(end_date))
                    filtered_df = df.loc[mask]

                    if filtered_df.empty:
                        st.warning("⚠️ No data available for the selected date range.")
                    else:
                        st.subheader("📊 EURUSD Candlestick Chart")

                        # Chunk loading logic
                        MAX_CANDLES = 1000
                        chunk_df = filtered_df.iloc[-MAX_CANDLES:] if len(filtered_df) > MAX_CANDLES else filtered_df

                        # Candlestick chart
                        fig = go.Figure()

                        fig.add_trace(go.Candlestick(
                            x=chunk_df['timestamp'],
                            open=chunk_df['open'],
                            high=chunk_df['high'],
                            low=chunk_df['low'],
                            close=chunk_df['close'],
                            name="Candles"
                        ))

                        # Volume overlay
                        fig.add_trace(go.Bar(
                            x=chunk_df['timestamp'],
                            y=chunk_df['volume'],
                            name="Volume",
                            marker_color='rgba(128,128,128,0.5)',
                            yaxis='y2'
                        ))

                        # Layout with rangeslider
                        fig.update_layout(
                            xaxis_rangeslider_visible=True,
                            xaxis_title='Date',
                            yaxis_title='Price',
                            yaxis2=dict(
                                overlaying='y',
                                side='right',
                                title='Volume',
                                showgrid=False
                            ),
                            height=600
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        st.info("ℹ️ Use the rangeslider to navigate through the full dataset! The chart loads the latest chunk by default for performance.")

            except Exception as e:
                st.error(f"❌ Error while handling date column: {e}")

        else:
            st.error(f"❌ Your file must have these columns: {expected_cols}")

    except Exception as e:
        st.error(f"❌ Failed to load your file: {e}")
else:
    st.info("💡 Please upload your EURUSD data file to begin.")
