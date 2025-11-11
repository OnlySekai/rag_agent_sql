from dotenv import load_dotenv
load_dotenv()
from agent.anwer_sql.runnable import predict
from db.csv import load_metadata

table_context = load_metadata("student_subject_scores", './data').json()

predict(table_context, "Who is student who have highest score except on language subjects and when he have a dinner?")

