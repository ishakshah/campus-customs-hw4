# Campus Customs

A customer website for Campus Customs, a Yale apparel shop, with a Personal Assistant chatbot. This is my MGT 409 Homework 4 project.

- **Front end:** React + Vite + TypeScript (`frontend/`)
- **Back end:** Python FastAPI (`backend/main.py`)
- **Assistant:** a PydanticAI agent that answers questions about prices, sizes, and stock from the shop's database. All model calls go through Portkey to `gpt-5.6-luna`.

## What's in this repo

```
hw4/
├── AI_prompts.md          every prompt I gave my AI coding assistant, by problem
├── requirements.txt       Python packages for the backend
├── .env.example           placeholders for the secrets you need (copy to .env)
├── .gitignore
├── README.md              this file
├── frontend/              Vite React TypeScript app
├── backend/
│   ├── main.py            FastAPI app (run with uvicorn, see below)
│   ├── agent.py           the agent: wiring, safety check, loop limits
│   ├── models.py          the typed shapes the API and agent use
│   ├── tools.py           the tools the agent can call
│   └── prompts/
│       └── prompt.md      the agent's system prompt (voice and safety rules)
└── output/
    ├── harness.md         how the whole system works (read this first)
    ├── design.md          the styling and design changes
    ├── usability.md       the usability improvements
    ├── app_check.html     the app check (open it in a browser)
    ├── app_check_images/  screenshots linked from app_check.html
    └── audit_trail.json   a record of the agent's activity
```

The agent itself is the four files `backend/prompts/prompt.md`, `backend/agent.py`, `backend/tools.py`, and `backend/models.py`.

## What is not in this repo

To keep the repository public and safe, three things are **not** committed (they're listed in `.gitignore`):

1. **My real `.env`**, which holds my Portkey API key. `.env.example` has placeholders only.
2. **The database**, `data/campus_customs.db`.
3. **The product images**, `data/products/`.

The database and images come as a separate **data pack**, so you need to place that yourself before running the site (step 2 below).

## Before you start

You need:

- **Python 3.13** (earlier 3.x versions may work, but I built and tested it on 3.13)
- **Node.js 24** with npm (I used Node 24 and npm 11)
- **The data pack** (`campus_customs.db` and the `products/` folder of images)
- **A Portkey API key**, only for the Personal Assistant chat. Everything else (the product pages, filters, accounts, Explore, and About Us) works without one.

## Run it

All commands are run from the cloned `hw4` folder unless it says otherwise. The commands below are for macOS and Linux. On Windows, activate the virtual environment with `.venv\Scripts\activate` instead.

### 1. Clone the repo

```bash
git clone <the repo URL>
cd hw4
```

(If the repository folder has a different name, `cd` into it instead.)

### 2. Place the data pack

Put the data pack inside the `hw4` folder in a folder named `data`, so it looks like this:

```
hw4/
└── data/
    ├── campus_customs.db
    └── products/          the product images the database refers to
```

The backend reads products from `data/campus_customs.db`, so the site has nothing to show without it. The `data/` folder is ignored by git, so it won't be added to the repo by accident.

### 3. Add your secrets

Copy the example file to a new file named `.env`, in the `hw4` folder:

```bash
cp .env.example .env
```

Then open `.env` and fill in:

- `PORTKEY_API_KEY`: your Portkey key. Without it the site still works, but the chat says the assistant isn't available.
- `SESSION_SECRET` (optional): a long random string that signs the login cookie. Generate one with `python3 -c "import secrets; print(secrets.token_hex(32))"`. If you leave it empty, everyone is logged out each time the backend restarts.

`.env` is ignored by git, so your real values are never committed. (The backend also reads a `.env` in the folder above `hw4`, if you keep one there.)

### 4. Start the back end

Set up a virtual environment and install the packages (the first time only):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then start the API from the `backend` folder:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Leave it running. If you see `command not found: uvicorn`, the virtual environment isn't active. Run `source .venv/bin/activate` from `hw4` (or use `python -m uvicorn main:app --reload --port 8000`).

### 5. Start the front end

Open a second terminal. From the `hw4` folder:

```bash
cd frontend
npm install
npm run dev
```

(`npm install` is only needed the first time.)

### 6. Open the site

Go to **http://campuscustoms.localhost:5174**. If your browser doesn't open that address, **http://localhost:5174** works too.

Both servers must be running. The front end sends every `/api` and `/images` request on to the backend on port 8000, so you only ever open the front end's address.

## Try it

- **Browse:** open **Products**, then try the filters (size, color, item type, price) and the sort menu.
- **Ask the assistant:** click **Personal Assistant** in the bottom right corner and try "what t-shirts do you have?" or "what's the inventory level of basic hoodie big yale in size M?" The assistant looks up real prices and stock from the database, and a browse question fills the Products page with matching items.
- **Create an account** with a password of at least 10 characters that includes a letter, a number, and a special character. Signed-in shoppers get their chat history saved and the assistant greets them by name.
- **Explore** and **About Us** show the campus tour slideshow with a map and the shop's story.

## Where to read more

- **[output/harness.md](output/harness.md)** explains how the system works: the database, accounts and passwords, how the front end talks to the API, the agent's tools and model fields, the safety rules, the audit trail, and every limit.
- **[output/design.md](output/design.md)** and **[output/usability.md](output/usability.md)** cover the design and usability changes.
- **[output/app_check.html](output/app_check.html)** shows the app check with screenshots. Open it in a browser.
- **[output/audit_trail.json](output/audit_trail.json)** is the record of what the agent does. It's written by the backend each time the assistant answers, and new entries are added to the end.

## Troubleshooting

- **Products don't load, or the backend shows database errors:** check that `data/campus_customs.db` is in the `hw4` folder (step 2).
- **Product photos are missing:** check that `data/products/` is in place.
- **The chat says the assistant isn't available:** `PORTKEY_API_KEY` is missing or empty in `.env`. Add it and restart the backend.
- **Everyone gets logged out when the backend restarts:** set `SESSION_SECRET` in `.env`.
- **The page can't reach the API:** make sure the backend is running on port 8000, and the front end is on port 5174.
