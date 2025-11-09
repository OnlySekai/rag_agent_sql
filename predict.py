from dotenv import load_dotenv
load_dotenv()
from agent.anwer_sql.runnable import run_agent,trace
from db.csv import load_metadata

table_context = load_metadata("Student_Subject_Scores").json()

trace(run_agent(table_context, "What's time student who have highest score will be have dinner?"))

