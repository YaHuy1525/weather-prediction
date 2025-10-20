import pandas as pd
import joblib
import os
import time
from pathlib import Path
from logger import get_logger
from custom_exception import CustomException
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from typing import Any, Dict, Optional, Tuple, Union

logger = get_logger(__name__)

class DataProcessing:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None
        self.version = int(time.time())
        
        self.versioned_dir = Path(self.output_path) / f"v{self.version}"
        self.versioned_dir.mkdir(parents=True, exist_ok=True)
        
        self.latest_dir = Path(self.output_path) / "latest"
        if self.latest_dir.exists():
            self.latest_dir.unlink()
        self.latest_dir.symlink_to(f"v{self.version}", target_is_directory=True)
        
        logger.info(f"DataProcessing initialized (v{self.version})")
    
    def _save_artifact(self, data: Any, filename: str) -> str:
        try:
            filepath = self.versioned_dir / filename
            joblib.dump(data, filepath)
            return str(filepath)
        except Exception as e:
            logger.error(f"Error saving {filename}: {str(e)}")
            raise CustomException(f"Failed to save {filename}")
    
    def load_data(self) -> pd.DataFrame:
        try:
            self.df = pd.read_csv(self.input_path)
            logger.info(f"Data loaded successfully. Shape: {self.df.shape}")
            return self.df
        except Exception as e:
            logger.error(f"Data loading error: {str(e)}")
            raise CustomException("Failed to load input data")
    
    def preprocess(self) -> None:
        try:
            self.df["Date"] = pd.to_datetime(self.df["Date"])
            self.df["Year"] = self.df["Date"].dt.year
            self.df["Month"] = self.df["Date"].dt.month
            self.df["Day"] = self.df["Date"].dt.day
            self.df.drop(columns=["Date"], inplace=True)
            
            numerical = self.df.select_dtypes(include=['number']).columns
            for col in numerical:
                self.df[col] = self.df[col].fillna(self.df[col].median())
            
            initial_rows = len(self.df)
            self.df.dropna(inplace=True)
            
            logger.info(f"Preprocessing complete. Dropped {initial_rows - len(self.df)} rows with missing values.")
            
        except Exception as e:
            logger.error(f"Data preprocessing error: {str(e)}")
            raise CustomException("Data preprocessing failed")
    
    def label_encode(self) -> None:
        try:
            categorical = [
                'Location', 'WindGustDir', 'WindDir9am', 
                'WindDir3pm', 'RainToday', 'RainTomorrow'
            ]
            
            self.label_mappings = {}
            
            for col in categorical:
                if col in self.df.columns:
                    le = LabelEncoder()
                    self.df[col] = le.fit_transform(self.df[col].astype(str))
                    self.label_mappings[col] = dict(zip(le.classes_, le.transform(le.classes_)))
                    logger.debug(f"Encoded {col}: {self.label_mappings[col]}")
            
            # Save label mappings
            self._save_artifact(self.label_mappings, "label_mappings.joblib")
            logger.info(f"Encoded {len(categorical)} categorical features")
            
        except Exception as e:
            logger.error(f"Label encoding error: {str(e)}")
            raise CustomException("Label encoding failed")
    
    def split_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        try:
            X = self.df.drop(columns=["RainTomorrow"], axis=1)
            y = self.df["RainTomorrow"]
            
            logger.info(f"Splitting data. Features: {X.shape[1]}, Samples: {len(X)}")
            
            # Stratified split to handle class imbalance
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=0.2, 
                random_state=42,
                stratify=y
            )
            
            # Save individual components
            self._save_artifact(X_train, "X_train.pkl")
            self._save_artifact(X_test, "X_test.pkl")
            self._save_artifact(y_train, "y_train.pkl")
            self._save_artifact(y_test, "y_test.pkl")
            
            # Save metadata
            metadata = {
                'version': self.version,
                'created_at': time.strftime("%Y-%m-%d %H:%M:%S"),
                'features': X.columns.tolist(),
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'feature_count': X.shape[1]
            }
            self._save_artifact(metadata, "metadata.joblib")
            
            logger.info(f"Data split complete. Train: {len(X_train)}, Test: {len(X_test)}")
            
            return X_train, X_test, y_train, y_test
            
        except Exception as e:
            logger.error(f"Data splitting error: {str(e)}")
            raise CustomException("Failed to split data")
    
    def run(self) -> Dict[str, Any]:
        try:
            self.load_data()
            self.preprocess()
            self.label_encode()
            
            # Get split data
            X_train, X_test, y_train, y_test = self.split_data()
            
            # Save complete dataset
            dataset = {
                'X_train': X_train,
                'X_test': X_test,
                'y_train': y_train,
                'y_test': y_test,
                'version': self.version,
                'created_at': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self._save_artifact(dataset, "dataset.joblib")
            
            logger.info(f"Data processing completed successfully (v{self.version})")
            return {
                'status': 'success',
                'version': self.version,
                'output_dir': str(self.versioned_dir),
                'train_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise CustomException("Data processing pipeline failed")


def load_processed_data(version: str = "latest") -> Dict[str, Any]:
    try:
        if version == "latest":
            path = Path("artifacts/processed/latest/dataset.joblib")
        else:
            path = Path(f"artifacts/processed/v{version}/dataset.joblib")
        
        if not path.exists():
            raise FileNotFoundError(f"No data found for version: {version}")
            
        return joblib.load(path)
        
    except Exception as e:
        logger.error(f"Error loading data (version: {version}): {str(e)}")
        raise CustomException(f"Failed to load processed data: {str(e)}")


if __name__ == "__main__":
    try:
        processor = DataProcessing(
            input_path="artifacts/raw/data.csv",
            output_path="artifacts/processed"
        )
        result = processor.run()
        print(f"Processing completed: {result}")
    except Exception as e:
        logger.critical(f"Processing failed: {str(e)}")
        raise