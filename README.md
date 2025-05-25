
# AI Chat App (LangChain + Streamlit)

This project is a **chat-based web app** built using **Streamlit**, powered by **LangChain** and **OpenAI** APIs. It enables natural language interaction with tools or agents you define in `main.py`.

---

## Features

- 💬 Chat interface with real-time responses
- 🔗 LangChain-powered reasoning and tool use
- 🔐 Uses environment variables for API credentials
- 🌐 Streamlit UI for interaction

---

## Project Structure

```

.
├── app.py             # Streamlit app entrypoint
├── main.py            # LangChain logic and custom tools
├── requirements.txt   # Python dependencies
├── .env               # Environment file (not included in repo)

````

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/ai-chat-app.git
cd ai-chat-app
````

### 2. Install dependencies

We recommend using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up your environment variables

Create a `.env` file in the root directory with the following:

```
OPENAI_API_KEY=your_openai_api_key_here
```

You can also add any other environment variables required by your tools in `main.py`.

### 4. Run the app

```bash
streamlit run app.py
```

---

## How It Works

* `main.py` contains the **LangChain logic**, including tools, prompts, chains, or agents.
* `app.py` is the **frontend logic** using Streamlit to render a user interface and interact with the backend.
* `langchain-openai` and `langchain-core` allow integration with OpenAI models and chains.

---

## Dependencies

From `requirements.txt`:

* `langchain`, `langchain-openai`, `langchain-core`, `langchain-community`
* `streamlit` — Web interface
* `requests` — API calls
* `python-dotenv` — Load `.env` secrets
* `typing` — Type hints for maintainability

Install with:

```bash
pip install -r requirements.txt
```

---

## Deployment

You can deploy this app using:

* [Streamlit Community Cloud](https://streamlit.io/cloud)
* [Render](https://render.com)
* [Heroku](https://heroku.com)
* [Vercel (via Serverless)](https://vercel.com)
* [Hugging Face Space](https://huggingface.co/spaces)

Make sure to include `.env` secrets in the deployment environment.

---

## TODO / Ideas

* [ ] Add memory or session history
* [ ] Customize tools and agent responses
* [ ] Add vector store integration (e.g., FAISS or ChromaDB)
* [ ] Enhance UI with file uploads or charts

---
## Check out:
* [Currency_Converter_Agent](https://huggingface.co/spaces/rkuma18/Currency_Converter_Chat)

## License

MIT License
