# -*- coding: utf-8 -*-
"""hf_creditibility_score.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qbkjtHQwHOLbvs7kTJKI2SNq186ufDHi
"""

import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, Dense, Concatenate, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import pandas as pd

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Dense, Concatenate, Flatten

# Define function to create the neural network model
def create_nn_model(vocab_size: int, embedding_dim: int, max_length: int, num_of_dense: int) -> Model:
    """
    Creates a neural network model that processes user prompts using an embedding layer,
    concatenates it with function ratings, and passes through dense layers.

    Args:
        vocab_size (int): Size of the vocabulary for embedding.
        embedding_dim (int): Dimensionality of the embedding layer.
        max_length (int): Maximum length of input sequences.
        num_of_dense (int): Number of dense layers before concatenation.

    Returns:
        Model: A compiled TensorFlow model.
    """
    # Text input (user prompt)
    text_input = Input(shape=(max_length,), name="text_input")
    embedding = Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=max_length)(text_input)
    flatten = Flatten()(embedding)

    # Dense layers for text input
    num_neurons = 2**12  # Start with 4096 neurons
    x = flatten
    for _ in range(num_of_dense):
        num_neurons = max(1, int(num_neurons / 2))  # Ensure integer neurons, minimum of 1
        x = Dense(num_neurons, activation='relu')(x)

    # Numeric input (func_rating)
    func_rating_input = Input(shape=(1,), name="func_rating_input")
    y = Dense(32, activation='relu')(func_rating_input)

    # Concatenate both paths
    concatenated = Concatenate()([x, y])
    # output = Dense(1, activation='linear', name="output")(concatenated)
    output = Dense(6, activation='softmax', name="output")(concatenated)

    # Define and compile the model
    model = Model(inputs=[text_input, func_rating_input], outputs=output)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    return model

import os
print("Files in directory:", os.listdir())

# Try reading the saved CSV file
df = pd.read_csv("combined_data (1).csv")
print(df.head())  # Display first few rows

df["custom_rating"].unique()

df.shape

# Tokenize and prepare data
tokenizer = Tokenizer()
tokenizer.fit_on_texts(df["user_prompt"])
vocab_size = len(tokenizer.word_index) + 1
max_length = max([len(x.split()) for x in df["user_prompt"]])
embedding_dim = 16

# Convert text data into sequences
X_text = tokenizer.texts_to_sequences(df["user_prompt"])
X_text = pad_sequences(X_text, maxlen=max_length, padding='post')
print(X_text.shape)

# Numeric input
X_func_rating = np.array(df["func_rating"]).reshape(-1, 1)
print(X_func_rating.shape)

# Target variable
y = np.array(df["custom_rating"]).reshape(-1, 1)
print(y.shape)

df["custom_rating"].unique()

from keras.utils import to_categorical

# Assuming y is your array of class labels shaped as (20, 1)
# Convert labels to one-hot encoding
y_one_hot = to_categorical(y)

# Check the new shape of y_one_hot
print(y_one_hot.shape)

# Create the model with updated Embedding layer
num_of_dense_layers = 3  # Number of dense layers before concatenation

model = create_nn_model(
    vocab_size=vocab_size,
    embedding_dim=embedding_dim,
    max_length=max_length,
    num_of_dense=num_of_dense_layers  # Ensure correct parameter naming
)

# Display model summary
model.summary()

# Commented out IPython magic to ensure Python compatibility.
# %%time
# 
# # Train the model
# model.fit(
#     {"text_input": X_text, "func_rating_input": X_func_rating},
#     y_one_hot,
#     epochs=80,
#     batch_size=2,
#     validation_split=0.1,
#     verbose=2
# )

# Plot error
import matplotlib.pyplot as plt

plt.plot(model.history.history['loss'])
plt.plot(model.history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

# Display the model summary
model.summary()

import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "huggingface_hub"])

!huggingface-cli logout  # This will remove all saved tokens

!huggingface-cli login

import requests

HF_TOKEN = "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"  # Replace with your actual token

headers = {"Authorization": f"Bearer {HF_TOKEN}"}
response = requests.get("https://huggingface.co/api/whoami-v2", headers=headers)

if response.status_code == 200:
    print(" Token is valid:", response.json())
else:
    print(f" Token is INVALID. Status Code: {response.status_code}, Response: {response.text}")

!huggingface-cli login

import requests

HF_TOKEN = "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"  # Replace with your actual token

headers = {"Authorization": f"Bearer {HF_TOKEN}"}
response = requests.get("https://huggingface.co/api/whoami-v2", headers=headers)

if response.status_code == 200:
    print(" Token is valid:", response.json())
else:
    print(f" Token is INVALID. Status Code: {response.status_code}, Response: {response.text}")

from huggingface_hub import HfApi

# Define Hugging Face credentials
hf_username = "KAMAL18"  # Ensure this matches your exact username
repo_name = "my-tf-nn-model-v18"
repo_id = f"{hf_username}/{repo_name}"

# Use your valid token (paste your actual token)
HF_TOKEN = "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"  # Replace with your correct token

# Initialize API
api = HfApi()

# Create the repository using explicit authentication
api.create_repo(repo_id=repo_id, token=HF_TOKEN, exist_ok=True)

print(f" Repository created successfully: https://huggingface.co/{repo_id}")

HF_TOKEN = "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"

import requests

HF_TOKEN = "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"  # Paste your token

headers = {"Authorization": f"Bearer {HF_TOKEN}"}
response = requests.get("https://huggingface.co/api/whoami-v2", headers=headers)

if response.status_code == 200:
    print(" Token is valid:", response.json())
else:
    print(f" Token is INVALID. Status Code: {response.status_code}, Response: {response.text}")

!huggingface-cli logout  # Log out first
!huggingface-cli login   # Log in again

HF_TOKEN = "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"

import os
HF_TOKEN = "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"  # Replace with your actual token
os.environ["HF_TOKEN"] = HF_TOKEN  # Store token in environment

from huggingface_hub import whoami

try:
    user_info = whoami(token=os.environ["HF_TOKEN"])
    print(f" Authentication successful: {user_info['name']}")
except Exception as e:
    print(f" Authentication failed: {e}")

import os

# Set Keras backend to JAX (before importing Keras/TensorFlow)
os.environ["KERAS_BACKEND"] = "jax"

import numpy as np
import tensorflow as tf
from tensorflow import keras
from huggingface_hub import hf_hub_download

# 🔹 Define Hugging Face repository details
repo_id = "KAMAL18/my-tf-nn-model-v18"  # Change as needed
HF_TOKEN = "your_actual_huggingface_token_here"  # Replace with your token

# 🔹 Define the model filename (Ensure it matches the uploaded file)
filename = "model.keras"

# 🔹 Download the model from Hugging Face
try:
    model_path = hf_hub_download(repo_id=repo_id, filename=filename, token=HF_TOKEN)
    print(f" Model downloaded successfully: {model_path}")
except Exception as e:
    print(f" Failed to download model: {e}")
    exit()  # Stop execution if model fails to download

# 🔹 Load the Keras model
try:
    model = keras.models.load_model(model_path)
    print(" Model loaded successfully!")
except Exception as e:
    print(f" Error loading model: {e}")
    exit()  # Stop execution if model fails to load

model.summary()

import pickle
import numpy as np
from huggingface_hub import hf_hub_download
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

#  Define Hugging Face repository details
repo_id = "KAMAL18/my-tf-nn-model-v18"  # Change as needed
HF_TOKEN = "your_actual_huggingface_token_here"  # Replace with your token

try:
    #  Download and load the model
    model_path = hf_hub_download(repo_id=repo_id, filename="model.keras", token=HF_TOKEN)
    model = keras.models.load_model(model_path)
    print(" Model loaded successfully!")

    #  Download and load the tokenizer
    tokenizer_path = hf_hub_download(repo_id=repo_id, filename="tokenizer.pkl", token=HF_TOKEN)
    with open(tokenizer_path, "rb") as f:
        tokenizer = pickle.load(f)
    print(" Tokenizer loaded successfully!")

except Exception as e:
    print(f" Error loading model/tokenizer: {e}")
    exit()

#  Sample test data
test_texts = [
    "How to improve focus and concentration?",
    "What are the side effects of lack of sleep?",
]

#  Preprocess text input
max_length = model.input_shape[1] if isinstance(model.input_shape, tuple) else 10  # Default length if unknown
X_text_test = pad_sequences(tokenizer.texts_to_sequences(test_texts), maxlen=max_length, padding='post')

#  Automatically detect if the model was trained with text-only or text + numeric inputs
expected_input_shape = model.input_shape[1]

if expected_input_shape == X_text_test.shape[1]:
    X_test_final = X_text_test.astype(np.float32)  # Convert to float32 for TensorFlow compatibility
    print(" Model trained on text only. Using text input.")

elif expected_input_shape == X_text_test.shape[1] + 1:
    X_func_test = np.array([[5], [4]], dtype=np.float32)  # Convert to float32
    X_test_final = np.hstack((X_text_test, X_func_test))  # Merge inputs
    print(" Model trained on text + numeric input. Merging inputs.")

else:
    raise ValueError(f" Model expected {expected_input_shape} features, but got {X_text_test.shape[1]} or {X_text_test.shape[1] + 1}.")

#  Make predictions
predictions = model.predict(X_test_final)

#  Display results in the expected format
print("\n **Predictions:**")
for text, pred in zip(test_texts, predictions):
    print(f" Prompt: {text}")
    print(f" Predicted Rating: {pred[0]:.2f}")
    print("-" * 50)

    # Load the model
model = keras.models.load_model(model_path)

#  Recompile the model to reset the optimizer state
model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])  # Adjust loss if needed

print(" Model loaded and recompiled successfully!")

from google.colab import files

uploaded = files.upload()  # This will prompt you to select the file

import os

print(os.listdir("/content"))  # This should now include tokenizer.pkl

import pickle

file_path = "/content/tokenizer (3).pkl"  # Make sure the name matches your uploaded file

# Load the tokenizer object
with open(file_path, "rb") as file:
    tokenizer = pickle.load(file)

print("Tokenizer loaded successfully!")

# Check the vocabulary (word to index mapping)
print(tokenizer.word_index)

# Check the reverse mapping (index to word)
print(tokenizer.index_word)

# Check the number of words in the tokenizer
print(len(tokenizer.word_index))

# Check word frequency counts
print(tokenizer.word_counts)

import json

# Convert tokenizer to JSON format
tokenizer_json = tokenizer.to_json()

# Save JSON file
with open("tokenizer.json", "w") as json_file:
    json.dump(tokenizer_json, json_file, indent=4)

print("Tokenizer saved as JSON. You can now open and inspect it!")

import json

# Convert tokenizer to JSON and pretty-print it
print(json.dumps(json.loads(tokenizer.to_json()), indent=4))

