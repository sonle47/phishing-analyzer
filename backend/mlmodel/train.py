import pandas as pd
from datasets import load_dataset
from sklearn.model_selection import train_test_split

DATASET = "zefang-liu/phishing-email-dataset"

raw = load_dataset(DATASET, split="train").to_pandas()

data = pd.DataFrame({
    "text": raw["Email Text"],
    "label": raw["Email Type"].map({"Phishing Email": "phishing", "Safe Email": "safe"}),
})
data = data.dropna()
data = data[data["text"].str.strip().str.lower() != "empty"]
data = data.drop_duplicates(subset="text")

print(data.head())
print(data["label"].value_counts())

train_text, test_text, train_labels, test_labels = train_test_split(
    data["text"],
    data["label"],
    test_size=0.25,
    random_state=42,
    stratify=data["label"],
)

print("Training emails:", len(train_text))
print("Test emails:", len(test_text))
print(train_labels.value_counts(normalize=True))
print(test_labels.value_counts(normalize=True))
