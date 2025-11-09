from dotenv import load_dotenv
load_dotenv()
from agent.anwer_sql.runnable import run_agent,trace
from db.csv import load_metadata

table_context = load_metadata("student_scores").json()

trace(run_agent(table_context, "Who is student who have highest score on using calculator subjects?"))

