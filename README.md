# 📁 Tech Assignment

This project demonstrates integration with Google Drive to list, summarize, and download summaries of selected files using a web interface built with Flask.

---

## 🚀 Getting Started

Follow the steps below to set up and run the project on your local machine.

---

### 1️⃣ Clone the Repository

```bash
git https://github.com/Roddur114/tech-exactly-assignment.git
cd tech-exactly-assignment
```

2️⃣ Create a Virtual Environment
```
python -m venv venv

```
3️⃣ Activate the Virtual Environment
Windows:
```
.\venv\Scripts\activate
```

Linux/macOS:
```
source venv/bin/activate

```

4️⃣ Install Dependencies
```
pip install -r requirements.txt

```
▶️ Run the Project
Windows:

```
run.bat
```

Ubuntu/Linux/macOS:
```
./run.sh

```


## Note

Since this is a personal API key, publishing it on GitHub may cause it to be revoked.
Please manually generate a new API key by visiting:
```
https://console.groq.com/keys

```

After generating the key, update your project configuration in:

```
constant/constant.py
```

Inside the ProjectConstant class, set:

```
class ProjectConstant:
    GROQ_API_KEY = "your_new_groq_api_key_here"
```