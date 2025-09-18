import os
import sys
sys.path.append("src")
from data_processing import DataProcessing
from model_training import ModelTraining

if __name__ == "__main__":
    processor = DataProcessing("artifacts/raw/data.csv" , "artifacts/processed")
    processor.run() 
    trainer = ModelTraining("artifacts/processed", "artifacts/models")
    trainer.run()
