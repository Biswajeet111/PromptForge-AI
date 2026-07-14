<div align="center">
  <h1>🚀 PromptForge AI</h1>
  <p><b>AI-Powered Prompt Optimization Studio</b></p>
  <p><i>Supercharge your prompt engineering with Google Gemini API & Streamlit</i></p>
</div>

---

## 📖 Overview

**PromptForge AI** is a professional-grade prompt engineering workspace. It takes your raw ideas and transforms them into highly effective, structured, and optimized prompts tailored to specific tasks and tones. Equipped with a **Prompt Quality Analyzer**, it not only optimizes your prompts but also teaches you how to write better ones by evaluating clarity, structure, and context.

## ✨ Key Features

- **🧠 Intelligent Optimization**: Uses Google's **Gemini 2.5 Flash** model to refine and structure your prompts.
- **📊 Prompt Quality Analyzer (Phase 7)**:
  - **Overall Score** evaluation.
  - Granular metrics: **Clarity**, **Structure**, **Context**, and **Specificity**.
  - **AI Suggestions**: Provides actionable improvement tips, identifies missing information, and offers better formatting techniques.
- **⚙️ Customization**: Configure Task Type (General, Writing, Coding, etc.), Tone, Detail Level, and use predefined Templates.
- **📜 Smart History**: 
  - Automatically saves all your optimizations.
  - **Clickable History Items**: Load previous prompts with a single click.
  - **Search & Favorites**: Easily find past prompts or star your best ones for quick access.
- **📋 Seamless UX**: 
  - Beautiful, modern card-based UI.
  - One-click native **Copy to Clipboard**.
  - Download optimized prompts as `.txt` files.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **AI Model**: [Google Generative AI (Gemini)](https://ai.google.dev/)
- **Data Handling**: Pandas

## 🚀 Getting Started

### Prerequisites
Make sure you have Python installed. You will also need a Google Gemini API Key.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/PromptForge-AI.git
   cd PromptForge-AI
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup:**
   Create a `.env` file in the root directory and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## 📂 Project Structure

```
PromptForge-AI/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration & Environment loading
├── requirements.txt       # Python dependencies
├── assets/
│   └── style.css          # Custom styling
├── data/
│   └── prompt_history.csv # Local storage for history
└── src/
    ├── ai/
    │   └── gemini_client.py # Gemini API integration & Analyzer
    ├── core/
    │   ├── history.py       # History management (save, load, favorites)
    │   └── optimizer.py     # Prompt optimization logic
    └── utils.py             # Helper functions (CSS loader)
```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to contribute.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
