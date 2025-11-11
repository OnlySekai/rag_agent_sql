import os
from dotenv import load_dotenv
load_dotenv()

from agent.create_db.runnable import preprocess_table_v2
# Load biến môi trường từ file .env

# Lấy key từ env
api_key = os.getenv("API_KEY")


table_student_md = """
| Student Info |  | Subject Info |  | Score |
|---|---|---|---|---|
| ID | Name | ID | Name |  |
|---|---|---|---|---|
| 1 | John Doe | 101 | Math | 95 |
| 2 | Jane Smith | 102 | Science | 88 |
| 1 | John Doe | 102 | Science | 92 |
| 3 | Peter Jones | 101 | Math | 78 |
| 2 | Jane Smith | 101 | English | 85 |"""


with open("./data/a.html", "r") as f:
    table_student_md = f.read()



a = preprocess_table_v2(table_student_md, './data')
print(a)