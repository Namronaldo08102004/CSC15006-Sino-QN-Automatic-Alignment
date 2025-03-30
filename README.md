<a id="readme-top"></a>
# Automatic Alignment between Sino character image and its Vietnamese Translation

## 📜 Overview
This project is a **data preparation pipeline** for language models, specifically designed for processing **old Vietnamese written texts**. It aims to collect, preprocess, and align textual data from historical Vietnamese sources to enhance OCR and NLP capabilities.

### ✨ Key Features
- **📚 Data Collection** – Collecting Old Vietnamese text images from books, poems, and other historical sources.
- **🛠️ Data Preprocessing** – Enhancing image quality for optimal OCR results.
- **🔍 OCR Processing** – Extracting text using **[Kim Hán Nôm OCR](https://tools.clc.hcmus.edu.vn/)**, tailored for Old Vietnamese texts.
- **🧹 Data Cleaning** – Removing OCR errors and normalizing text.
- **📖 Special Case Handling** – Addressing **Hán Nôm** complexities like blurs, noise, and stripes.
- **📝 Sentence Alignment** – Aligning sentences for structured translation.
- **🔗 Word Alignment** – Matching Vietnamese and Hán Nôm text pairs.



## 🚀 Pipeline Workflow

### 1️⃣ Data Collection
- Collects images containing Old Vietnamese text from books, manuscripts, and poems.
- Sources are curated to ensure historical accuracy and linguistic diversity.

### 2️⃣ Data Preprocessing
- **Noise Removal** – Enhancing image clarity.
- **Contrast Adjustment** – Improving OCR readability.
- **Resizing & Cropping** – Optimizing dimensions for processing.

### 3️⃣ OCR Processing
- **OCR Model**: Uses **[Kim Hán Nôm OCR](https://tools.clc.hcmus.edu.vn/)**.
- Extracts text from **preprocessed images**.

### 4️⃣ Data Cleaning
- Removes OCR-induced errors (e.g., misrecognized characters).
- Normalizes text formats (e.g., diacritics, punctuation).

### 5️⃣ Handling Special Cases
- Addresses **blurred text, noise, and historical variations** in Old Vietnamese.
- Special handling for **Hán Nôm** characters.

### 6️⃣ Sentence Alignment
- Ensures **proper alignment** between Old Vietnamese sentences and their modern equivalents.

### 7️⃣ Word Alignment
- Matches **Vietnamese and Hán Nôm** word pairs for linguistic research and translation models.



## 🧑‍💻 Contributors
Special thanks to the following contributors for their valuable work on this project:
- [@Namronaldo08102004](https://github.com/Namronaldo08102004)
- [@Kiet-2004](https://github.com/Kiet-2004)
- [@Melios22](https://github.com/Melios22)



## 📜 License
This project is licensed under the **MIT License** – feel free to use, modify, and distribute.



## 📝 Future Improvements
- **Enhancing OCR Accuracy** – Fine-tuning models for Old Vietnamese text.
- **Expanding Corpus** – Adding more historical texts for analysis.
- **Automated Translation Alignment** – Improving machine learning models for Vietnamese-Hán Nôm translations.



## ⭐ Support the Project
If you find this project useful, please consider giving it a **⭐ star** on GitHub!


<p align="right">
  <a href="#readme-top">⬆️ Back to top</a>
</p>
