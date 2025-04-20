import pandas as pd
import os
from datetime import datetime

# Configuration
INPUT_FOLDER = r'D:\TRADING\Data for Backtesting\Exness\Raw Data\EURUSD\Extracted File'
OUTPUT_FILE = 'EURUSD_1M_OHLC_FULL_FINAL.csv'
TIMEFRAME = '1T'  # 1-minute bars

def process_entire_folder():
    """Process all tick files into one consolidated OHLC file."""
    all_ohlc = pd.DataFrame()
    processed_files = 0
    
    print(f"Processing all files in: {INPUT_FOLDER}")
    
    # Get all CSV files
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.csv')]
    total_files = len(files)
    
    if not files:
        print(f"❌ Error: No CSV files found in {INPUT_FOLDER}")
        return
    
    for i, filename in enumerate(files, 1):
        try:
            print(f"\r🔄 Processing {i}/{total_files} ({i/total_files:.0%}) - {filename}", end="")
            
            filepath = os.path.join(INPUT_FOLDER, filename)
            df = pd.read_csv(
                filepath,
                usecols=['Timestamp', 'Bid', 'Ask'],
                parse_dates=['Timestamp'],
                date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S.%fZ'),
                dtype={'Bid': 'float32', 'Ask': 'float32'}
            )
            
            df['Mid'] = (df['Bid'] + df['Ask']) / 2
            df.set_index('Timestamp', inplace=True)
            
            ohlc = df['Mid'].resample(TIMEFRAME).agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last'
            })
            ohlc['Volume'] = df['Bid'].resample(TIMEFRAME).count()
            
            all_ohlc = pd.concat([all_ohlc, ohlc])
            processed_files += 1
            
        except Exception as e:
            print(f"\n⚠️ Error in {filename}: {str(e)}")
            continue
    
    if not all_ohlc.empty:
        # Final processing
        all_ohlc = all_ohlc.sort_index().drop_duplicates()
        all_ohlc.to_csv(OUTPUT_FILE)
        
        # NEW: Display last 5 lines
        print("\n\n=== Last 5 Rows of Output ===")
        print(all_ohlc.tail())
        
        print("\n✅ Success!")
        print(f"Processed {processed_files}/{total_files} files")
        print(f"Total bars: {len(all_ohlc):,}")
        print(f"Date range: {all_ohlc.index[0]} to {all_ohlc.index[-1]}")
        print(f"Saved to: {os.path.abspath(OUTPUT_FILE)}")
    else:
        print("\n❌ No valid data processed")

if __name__ == '__main__':
    process_entire_folder()