import pandas as pd
import joblib
import os
from logger import get_logger
from custom_exception import CustomException
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

logger = get_logger(__name__)

class DataProcessing:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None
        
        os.makedirs(self.output_path, exist_ok=True)
        logger.info("DataProcessing initialized")
        
    def load_data(self):
        try:
            self.df = pd.read_csv(self.input_path)
            logger.info("Data loaded successfully")
            return self.df
        except Exception as e:
            logger.error("Data loading error")
            raise CustomException(e)
        
    def preprocess(self):
        try:
            categorical = []
            numerical = []
            for col in self.df.columns:
                if self.df[col].dtypes == "object":
                    categorical.append(col)
                else:
                    numerical.append(col)
            self.df["Date"] = pd.to_datetime(self.df["Date"]) 
            self.df["Year"] = self.df["Date"].dt.year 
            self.df["Month"] = self.df["Date"].dt.month 
            self.df["Day"] = self.df["Date"].dt.day 
            self.df.drop(columns=["Date"], inplace=True)
            
            for col in numerical:
                self.df = self.df.fillna({col: self.df[col].mean()})
            self.df.dropna(inplace= True)
            logger.info("Data preprocessing completed") 
        except Exception as e:
            logger.error("Data processing error")
            raise CustomException(e)
    def label_encode(self):
        try:
            categorical = [
                'Location',
                'WindGustDir',
                'WindDir9am',
                'WindDir3pm',
                'RainToday',
                'RainTomorrow'
            ]
            for col in categorical:
                le = LabelEncoder()
                self.df[col] = le.fit_transform(self.df[col])
                label_mapping = dict(zip(le.classes_ , range(len(le.classes_))))
                logger.info(f"Label mapping for {col}")
                logger.info(label_mapping)
        except Exception as e:
            logger.error("Label encoding error")
            raise CustomException(e)    
    
    def split_data(self):
        try:
            X =self.df.drop(columns=["RainTomorrow"], axis = 1)
            y = self.df["RainTomorrow"]
            logger.info(f"X shape: {X.shape}, y shape: {y.shape}")
            logger.info(f"Columns: {X.columns.tolist()}")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            joblib.dump(X_train , os.path.join(self.output_path , "X_train.pkl"))
            joblib.dump(X_test , os.path.join(self.output_path , "X_test.pkl"))
            joblib.dump(y_train , os.path.join(self.output_path , "y_train.pkl"))
            joblib.dump(y_test , os.path.join(self.output_path , "y_test.pkl"))
            joblib.dump((X_train, X_test, y_train, y_test), os.path.join(self.output_path, "train_test_data.joblib"))
            logger.info("Data split completed")
        except Exception as e:
            logger.info("Data split error")
            raise CustomException(e)
    
    def run(self):
        self.load_data()
        self.preprocess()
        self.label_encode()
        self.split_data()
        logger.info("Data progcessiing competed")


if __name__ == "__main__":
        #Later change the path to "artifacts/raw/data.csv" , "artifacts/processed"
        processor = DataProcessing("artifacts/raw/data.csv" , "artifacts/processed")
        processor.run()