# English Abstract Move Recognition Tool

An automatic move recognition tool for scientific literature abstracts based on GLM-4 large language model. It uses prompt engineering to automatically annotate Background, Purpose, Method, Result, and Conclusion.

## Features

- Automatic recognition of 5 move types in English abstracts
- Visualized highlighting of recognition results
- Statistical distribution of each move type
- Clean and easy-to-use Web interface
- RESTful API for external integration

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

**Method 1: Use environment variable (recommended, more secure)**
```bash
# Temporary setting (current session only)
export ZHIPU_API_KEY="your_actual_api_key_here"

# Permanent setting (add to ~/.bashrc)
echo 'export ZHIPU_API_KEY="your_actual_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**Method 2: Use .env file**
```bash
# Copy example configuration file
cp .env.example .env

# Edit .env file and fill in your API key
nano .env
```

⚠️ **Security Note**: Do not commit real API keys to the Git repository. `.env` file is already excluded in .gitignore.

### 3. Get API Key

Visit [Zhipu AI Open Platform](https://open.bigmodel.cn/) to register and obtain an API Key.

### 4. Start the Service

```bash
python app.py
```

### 5. Access the Application

Open browser and visit: http://localhost:5001

## Usage

1. Enter your Zhipu AI API Key in the interface
2. Paste English scientific literature abstract content
3. Click "Start Recognition" button
4. View the results with different moves highlighted in different colors

## Move Type Definitions

| Label | Description |
|-------|-------------|
| BACKGROUND | Introduces research field background, current status, problems, or motivation |
| PURPOSE | States research objectives, problems to solve, or hypotheses to verify |
| METHOD | Describes research methods, experimental design, data sources, or techniques |
| RESULT | Presents research findings, experimental results, or data analysis |
| CONCLUSION | Summarizes conclusions, contributions, significance, or future outlook |

## Project Structure

```
en_abstract_move_recognition/
├── app.py              # Flask backend service
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Web frontend page
└── README.md           # Documentation
```

## Tech Stack

- **Backend**: Python + Flask
- **AI Model**: Zhipu GLM-4 (via zhipuai SDK)
- **Frontend**: HTML + CSS + JavaScript
- **Core Technology**: Prompt Engineering
