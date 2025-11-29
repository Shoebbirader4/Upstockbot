import pandas as pd
from pathlib import Path
from datetime import datetime
from utils.logger import log

class DataStorage:
    def __init__(self, storage_path: str = "./data", storage_type: str = "parquet"):
        self.storage_path = Path(storage_path)
        self.storage_type = storage_type
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_ohlcv(self, df: pd.DataFrame, symbol: str, date: datetime = None):
        """Save OHLCV data to storage"""
        if df.empty:
            log.warning("Empty dataframe, skipping save")
            return
        
        if date is None:
            date = datetime.now()
        
        if self.storage_type == "parquet":
            self._save_parquet(df, symbol, date)
        else:
            log.error(f"Unsupported storage type: {self.storage_type}")
    
    def _save_parquet(self, df: pd.DataFrame, symbol: str, date: datetime):
        """Save to Parquet file"""
        year_month = date.strftime("%Y%m")
        file_path = self.storage_path / f"{symbol}_{year_month}.parquet"
        
        # Append if file exists
        if file_path.exists():
            existing_df = pd.read_parquet(file_path)
            df = pd.concat([existing_df, df]).drop_duplicates(subset=['timestamp'], keep='last')
            df = df.sort_values('timestamp')
        
        df.to_parquet(file_path, index=False, engine='pyarrow')
        log.info(f"Saved {len(df)} bars to {file_path}")
    
    def load_ohlcv(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Load OHLCV data from storage"""
        if self.storage_type == "parquet":
            return self._load_parquet(symbol, start_date, end_date)
        return pd.DataFrame()
    
    def _load_parquet(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Load from Parquet files"""
        dfs = []
        
        # Generate list of year-months to load
        current = start_date.replace(day=1)
        while current <= end_date:
            year_month = current.strftime("%Y%m")
            file_path = self.storage_path / f"{symbol}_{year_month}.parquet"
            
            if file_path.exists():
                df = pd.read_parquet(file_path)
                dfs.append(df)
            
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        if not dfs:
            log.warning(f"No data found for {symbol} between {start_date} and {end_date}")
            return pd.DataFrame()
        
        df = pd.concat(dfs, ignore_index=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        log.info(f"Loaded {len(df)} bars for {symbol}")
        return df
