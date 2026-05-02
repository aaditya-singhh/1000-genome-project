import duckdb

csv_path = "/Users/aaditya/VS Code/1000 genome project/Data/chrX_full.csv"

con = duckdb.connect()

# --- Preview first 10 rows ---
print("=== First 10 rows ===")
print(con.execute(f"SELECT * FROM read_csv_auto('{csv_path}') LIMIT 10").df().to_string())

# --- Row and column count ---
print("\n=== Shape ===")
result = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{csv_path}')").fetchone()
print(f"Rows: {result[0]:,}")

# --- Column names ---
print("\n=== Columns ===")
cols = con.execute(f"DESCRIBE SELECT * FROM read_csv_auto('{csv_path}') LIMIT 1").df()
print(cols[["column_name", "column_type"]].to_string())

# --- Example: filter by chromosome position range ---
# Uncomment and edit to run custom queries:
# print("\n=== Custom query ===")
# df = con.execute(f"""
#     SELECT *
#     FROM read_csv_auto('{csv_path}')
#     WHERE column2 BETWEEN 1000000 AND 2000000
#     LIMIT 100
# """).df()
# print(df)
