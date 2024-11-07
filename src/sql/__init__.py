import os

SQL_DIR = os.path.dirname(os.path.abspath(__file__))


for filename in os.listdir(SQL_DIR):
    if filename.endswith(".sql"):
        name = filename.split(".")[0].upper()
        f = open(os.path.join(SQL_DIR, filename), "r")
        globals()[name] = f.read()
