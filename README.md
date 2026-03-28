# 🌱 AI Smart Bin Assistant
AI Smart Bin Assistant is a computer vision system that classifies waste (plastic, paper, metal, glass) in real time using a webcam. It provides disposal instructions and uses OCR to detect resin codes on plastics, enabling accurate and smarter recycling decisions.


### 🚀 Overview

The AI Smart Bin Assistant is a sustainability-focused application that classifies waste in real time using a webcam. It detects items such as plastic, paper, metal, and glass, and provides instant disposal instructions. The system also integrates OCR to detect resin codes on plastic items for more accurate recycling guidance.

### 🎯 Problem Statement

Recycling efficiency is low due to “wish-cycling”, where users incorrectly dispose of waste due to lack of knowledge about materials and recycling rules.

### 💡 Solution

This project solves the problem by:
Identifying waste items using AI
Providing real-time disposal instructions
Detecting resin codes using OCR for plastic items
Promoting correct recycling behavior

### 🧠 Features

✅ Core Features (MVP)

Real-time webcam-based waste detection

Classification into:

Plastic

Paper

Metal

Glass

Instruction overlay for proper disposal


### 🚀 Advanced Features

OCR-based resin code detection (1–7)

Smart recycling instructions based on material

Confidence-based filtering for reliable predictions


### ⚙️ Tech Stack

🔹 Frontend

HTML, CSS, JavaScript

🔹 Backend

Python
Flask (for web integration)

🔹 AI / ML

TensorFlow / Keras
EfficientNetB0 (Transfer Learning)

🔹 Computer Vision

OpenCV

🔹 OCR
Tesseract OCR / pytesseract

### 📊 Model Details & Training
To achieve high accuracy, we experimented with multiple deep learning models:
ResNet50
MobileNetV2
EfficientNetB0 (Best Performing)

### 📂 Dataset

The model was trained on a hybrid dataset consisting of:

🗂️ Public dataset: TrashNet

📱 Custom dataset: Images captured using mobile phones

This combination helped improve real-world performance and robustness.


### Dataset Size

Training: 1389 images

Validation: 297 images

Test: 301 images

Classes: 4 (plastic, paper, metal, glass)

### 🔧 Image Preprocessing

To improve model performance and OCR accuracy, multiple preprocessing techniques were applied during both training and inference.

📷 For Waste Classification Model

Before feeding images into the deep learning model, the following preprocessing steps were applied:

Resizing

All images were resized to 224 × 224 to match the input size of EfficientNetB0.

Color Conversion

Images were converted from BGR to RGB to align with deep learning model expectations.

Normalization

Pixel values were scaled appropriately based on the model requirements.

Data Augmentation (Training Phase)

To improve generalization and robustness:

Rotation

Zoom

Width & Height Shift

Horizontal Flip

Brightness Adjustment

### 📈 Training Performance (EfficientNetB0)

Epoch 1 → Accuracy: 73.0% → Val Accuracy: 86.5%

Epoch 3 → Accuracy: 90.0% → Val Accuracy: 91.9%

Epoch 6 → Accuracy: 93.7% → Val Accuracy: 93.27% (Best)

Epoch 10 → Accuracy: 95.9% → Val Accuracy: ~91.9%

### 🏆 Final Model Performance (EfficientNetB0)

Confusion Matrix

[68    4    0    4]

[ 3   55    0    4]

[ 0    0   89    1]

[ 2    1    0   70]

Classification Report

Class	Precision	Recall	F1-score

Glass	0.93	0.89	0.91

Metal	0.92	0.89	0.90

Paper	1.00	0.99	0.99

Plastic	0.89	0.96	0.92



### 📊 Overall Accuracy
👉 94% on test dataset



### 🔍 Observations

Paper classification is near-perfect

Minor confusion observed between:

Glass ↔ Plastic

Metal ↔ Glass

Model performs well in real-world conditions due to mixed dataset

