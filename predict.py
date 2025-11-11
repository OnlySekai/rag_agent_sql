from dotenv import load_dotenv
load_dotenv()
from agent.anwer_sql.runnable import predict
from db.csv import load_metadata

table_context = load_metadata("ung_dung", './data').json()

predict(table_context, "How many application?")

