# E-commerce P&L, Forecast and Text-to-SQL (7-day mini project)

Upload an e-commerce CSV, get a Profit & Loss report and a revenue forecast, and ask
questions in English that are answered with SQL. Built with Python, pandas, SQLite,
Prophet, Streamlit and the Gemini API.

This is a learning project for a larger system (InsightFlow, a financial analytics
platform). The goal was to find out what breaks when real, messy data goes through
cleaning, P&L, forecasting and Text-to-SQL.

## What it does

| Step | What happens | Files |
|---|---|---|
| 1. Clean | Raw CSV to a SQLite `sales` table. Bad rows are flagged, not deleted | `src/clean.py` |
| 2. P&L | Monthly and category P&L from a column mapping (works on any dataset) | `src/pnl.py`, `app/pnl_page.py` |
| 3. Forecast | Weekly revenue forecast with Prophet, compared against a naive baseline | `src/forecast_weekly.py`, `src/forecast_cv.py`, `app/forecast_page.py` |
| 4. Chat | English question to SQL (Gemini), only a single SELECT allowed, one retry on error | `src/chat_sql.py`, `src/llm_chat.py` |
| 5. Second dataset | Same code tested on the Favorita grocery data | `src/test_favorita_pnl.py`, `src/forecast_favorita.py`, `src/chat_favorita.py` |

## Key design decisions

- **Flag, don't delete.** Rows get `is_sale` and `is_outlier` flags. Queries use
  `WHERE is_sale = 1 AND is_outlier = 0`, so every decision can be changed later.
- **Discount is counted once per order.** In multi-item orders the discount sits on the
  item rows, so it is kept on the first row of each order only. Checked against
  `grand_total` (gap +3.6% with this rule, -9.6% when summed over every row).
- **Business rules live in a SQL view** (`sales_rev`), so the LLM cannot get them wrong.
- **P&L works from a column mapping**, not from fixed column names.
- **Honest labels.** The Pakistan dataset has no cost column, so profit there is simulated
  and the page says so.

## Results

**P&L (Pakistan dataset, 306,661 sales rows):** total revenue 1,202,706,887. The biggest
month is 2017-11 (sale month) and the biggest category is Mobiles & Tablets. Margins come
from simulated cost and are not real profit.

**Forecast (weekly, cross-validation, WAPE, lower is better):**

| Dataset / setup | Prophet | Naive baseline |
|---|---|---|
| Pakistan, no events | 84.0% | 84.8% |
| Pakistan, known sale calendar | 77.9% | 84.8% |
| Favorita, weekly | 12.6% | 11.6% |
| Favorita, weekly + holidays | 12.5% | 11.6% |

Forecast error depends mostly on the data: Favorita is smooth (about 12%), the Pakistan
data is driven by a few sale spikes (about 78%). On Favorita, Prophet did not beat the
naive baseline.

**Second dataset:** the P&L engine ran on 3,000,888 Favorita rows in about 40 seconds with
real cost mode, and COGS matched the file. The chat needed a separate view and schema
prompt.

## Limitations

- Pakistan profit is simulated (no cost data). Forecast numbers are only an indicative
  baseline.
- The forecast on the Pakistan data is flat (the same value every week) with a very wide
  interval.
- The chat was tested on a small set of questions. LLMs can answer unanswerable questions
  confidently, so schema rules ("no cost data", "no customers") were added. Always check
  the SQL it shows.
- Code in `revenue_sql.py` and the `sales_rev` view is specific to each dataset.

## Setup

```powershell
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

1. Download "Pakistan Largest Ecommerce Dataset" (Kaggle) into `data/raw/`.
   Data files are not in this repository.
2. For the chat, create a `.env` file with your key:
```
   GEMINI_API_KEY=your_key_here
```
   Check the available model names with `python src/list_models.py` and set them in the
   `MODELS` list in `src/llm_chat.py`.

## Run

```powershell
python src\clean.py                 # raw CSV -> data/processed/ecommerce.db
python src\pnl.py                   # monthly_pnl and category_pnl tables
python src\forecast_weekly.py       # weekly_actual and forecast_weekly tables
streamlit run app\pnl_page.py       # P&L page
streamlit run app\forecast_page.py  # forecast page
python src\chat_sql.py              # 5 hand-written SQL checks
python src\llm_chat.py              # English questions -> SQL
```

## Project structure

```
src/     cleaning, P&L engine, forecasts, chat, dataset checks
app/     Streamlit pages
notes/   day1.md to day7.md: what was done, what broke, lessons
```

## What I learned

- Check which values are order-level (discount, grand_total) before
