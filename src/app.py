import joblib
from flask import Flask,render_template,request
import numpy as np
import pandas as pd

app = Flask(__name__)
MODEL_PATH = "artifacts/models/model.pkl"
model = joblib.load(MODEL_PATH)

df = pd.read_csv("artifacts/raw/data.csv")
FEATURES = df.columns
print(FEATURES)

LABELS = {0 : "NO" , 1: "YES"}

@app.route("/" , methods=["GET" , "POST"])
def index():
    prediction = None

    if request.method=="POST":
        try:
            input_data = [float(request.form[feature]) for feature in FEATURES]
            input_array = np.array(input_data).reshape(1,-1)

            pred = model.predict(input_array)[0]
            prediction = LABELS.get(pred, 'Unknown')
            print(prediction)

        except Exception as e:
            print(str(e))
    
    return render_template("index.html" , prediction=prediction , features=FEATURES)

if __name__=="__main__":
    app.run(debug=True , port=5000 , host="0.0.0.0")