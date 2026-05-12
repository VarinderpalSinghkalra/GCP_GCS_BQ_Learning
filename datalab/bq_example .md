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



from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT *
FROM `gcp-project1-491103.prachi_dataset.employee`
LIMIT 10
"""

rows = client.query(query).result()

for row in rows:
    print(row)

