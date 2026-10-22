# Day 5: Text-to-SQL chat

## What I built
- chat_sql.py: sales_rev view (discount counted once per order) and 5 hand-written SQL
  questions. All 5 matched the P&L totals (total revenue 1,202,706,887; top months and
  categories; average order value about 5,966).
- llm_chat.py: Gemini generates SQL from an English question. Only a single SELECT is
  allowed. If the SQL fails, the error goes back to the model for one retry.
- Gemini returned 503 (high demand), so ask_llm() retries with waiting and falls back to
  other flash models.

## What went wrong
- Question "when was the biggest loss": the model used discount as loss. The number was
  correct for discount but the meaning was wrong. The dataset has no cost, so loss cannot
  be answered.
- Fix: schema rules ("no cost data", "discount is not a loss"). After the fix, the answer
  should be "Not available".

## Lessons
- An LLM answers wrong or unanswerable questions with confidence. Check the meaning of the
  SQL, not only the number.
- Put business rules in a view (the sales_rev view) so the model cannot get them wrong.
- API calls need retry and fallback.

## Not done
- A 10-question test list (test_questions.py) was written but not run.