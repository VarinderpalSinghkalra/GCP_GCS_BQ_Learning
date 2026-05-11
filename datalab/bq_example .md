!pip install db-dtypes     >>>> install this first


from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT *
FROM dataset.employee
LIMIT 10
"""

df = client.query(query).to_dataframe()

print(df)