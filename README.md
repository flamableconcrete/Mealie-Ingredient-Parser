# Mealie Ingredient Parser

A Terminal User Interface (TUI) application for processing unparsed recipe ingredients in your Mealie instance.
This tool identifies recipes with unparsed ingredients, uses Mealie’s built-in NLP parser to process them, and provides an interactive interface for creating missing units/foods or adding aliases to existing ones.

---

## ✨ Features

- **Automatic Detection** — Scans your Mealie instance to find all recipes with unparsed ingredients
- **NLP Parsing** — Leverages Mealie’s NLP parser to extract structured ingredient data
- **Progress Tracking** — Real-time statistics showing units, foods, and aliases created
- **Smart Workflow** — Interactive modals guide you through creating missing units/foods or adding aliases
- **Async Performance** — Built with `aiohttp` for fast, concurrent API operations
- **Modern TUI** — Clean, intuitive interface powered by [Textual](https://textual.textualize.io)

---

## 🧩 Requirements

- Python ≥ 3.13
- A running Mealie instance with API access
- Mealie API key with appropriate permissions

---

## ⚙️ Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Install dependencies
uv sync
```

Alternatively, install with pip:

```bash
pip install -r requirements.txt
```

---

## 🔐 Configuration

Create a `.env` file in the project root with your Mealie credentials:

```env
MEALIE_API_KEY=your_api_key_here
MEALIE_URL=https://your-mealie-instance.com/api
```

**Variables:**

- `MEALIE_API_KEY` — Your Mealie API bearer token
- `MEALIE_URL` — Base URL for the Mealie API (include `/api` path)

---

## 🚀 Usage

Run the application:

```bash
python main.py
# or
uv run main.py
```

### Workflow

1. **Loading** — The app fetches all recipes, units, and foods from your Mealie instance.
2. **Recipe List** — View all recipes with unparsed ingredients in a sortable table.
3. **Ingredient Review** — Process each unparsed ingredient:
   - If a unit is missing, choose to create a new unit or skip.
   - If a food is missing, choose to:
     - Create a new food
     - Add as alias to existing food
     - Create with custom name
     - Skip
4. **Progress Tracking** — Monitor units, foods, and aliases created in real time.
5. **Next Recipe** — Move to the next recipe or return to the list.

---

## 🧠 How It Works

An ingredient is considered *unparsed* when it has a `note` or `originalText` but no associated `food.id` or `unit.id`.

The parser:

1. Identifies all unparsed recipes
2. Sends each unparsed ingredient to Mealie’s NLP parser
3. Detects missing units/foods in the parsed result
4. Provides interactive prompts to resolve missing data
5. Updates the recipe with newly parsed ingredients

---

## 🗂️ Project Structure

```
mealie-testing/
├── main.py
├── mealie_client.py
├── parser.py
├── tui/
│   ├── app.py
│   ├── components/
│   └── views/
├── .env.example
├── requirements.txt
└── README.md
```
