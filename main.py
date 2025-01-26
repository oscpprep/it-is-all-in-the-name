import os
import pandas as pd
from unidecode import unidecode
import pickle
import warnings

warnings.filterwarnings("ignore")

# Constants
base_dir = "."
data_dir = os.path.join(base_dir, "data")
model_dir = os.path.join(base_dir, "models")
output_dir = os.path.join(base_dir, "data/predictions")

# Create directories if they don't exist
os.makedirs(data_dir, exist_ok=True)
os.makedirs(model_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Name of data file
dataname = "sample_data.csv"

# Parameters
name = "name"  # Field containing individual's name
n_way = "2class"
classifier = "svm"

# Normalize function
def normalize(word):
    return unidecode(word)

# Clean data
def clean_data():
    data = pd.read_csv(os.path.join(data_dir, dataname), encoding="utf-8")
    data["name_cleaned"] = data[name]
    data["name_cleaned"].fillna("", inplace=True)
    data["name_cleaned"] = data["name_cleaned"].apply(normalize)
    data["name_cleaned"] = data["name_cleaned"].str.upper()
    data["name_cleaned"].replace("[^A-Z .\-]", " ", regex=True, inplace=True)
    data["name_cleaned"].replace("[.-]+", " ", regex=True, inplace=True)
    data["name_cleaned"].replace("([A-Z])\\1\\1+", "\\1", regex=True, inplace=True)
    data["name_cleaned"].replace("\s+", " ", regex=True, inplace=True)
    data["name_cleaned"] = data["name_cleaned"].str.strip()
    # Save only 'name' and 'name_cleaned' to the output file
    data[["name", "name_cleaned"]].to_csv(os.path.join(output_dir, dataname), encoding="utf-8", index=False)

# Load data
def load_data():
    data = pd.read_csv(os.path.join(output_dir, dataname), encoding="utf-8")
    data["name_cleaned"].fillna("", inplace=True)
    data["name_cleaned"].replace(" ", "}{", regex=True, inplace=True)
    data["name_cleaned"] = "{" + data["name_cleaned"].astype(str) + "}"
    return data

# Run cleaning and prediction
clean_data()  # Run once to clean data
data = load_data()

# Load vectorizer and classifier
vectorizer_file = "vectorizer_2class_svm_concat_False.sav"
model_file = "model_2class_svm_concat_False.sav"

# Load the vectorizer
vectorizer_path = os.path.join(model_dir, vectorizer_file)
vectorizer = pickle.load(open(vectorizer_path, "rb"))

# Load the SVM model
model_path = os.path.join(model_dir, model_file)
clf = pickle.load(open(model_path, "rb"))

# Transform the cleaned names into a vectorized representation
tfidf_matrix = vectorizer.transform(data["name_cleaned"])

# Predict probabilities and labels
y_pred_prob = clf.decision_function(tfidf_matrix)
y_pred = clf.predict(tfidf_matrix)

# Generate predictions
df = pd.DataFrame({
    name: data[name],
    "predicted_religion": pd.Series(y_pred),
    "muslim_score": pd.Series(y_pred_prob)
})

# Save predictions
df.to_csv(os.path.join(output_dir, "predictions.csv"), encoding="utf-8", index=False)

print(f"Predictions saved to {os.path.join(output_dir, 'predictions.csv')}")
