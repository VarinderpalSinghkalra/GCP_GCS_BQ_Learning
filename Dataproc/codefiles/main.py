from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# -----------------------------
# CONFIG
# -----------------------------
PROJECT = "data-engineering-488013"
BUCKET = "datavip-dataflow"

INPUT_FILE = f"gs://{BUCKET}/spend_cube_clean.csv"

BQ_DATASET = "conversational_demo_df"
BQ_TABLE = "sample_spenddata_raw"

FULL_TABLE_ID = f"{PROJECT}:{BQ_DATASET}.{BQ_TABLE}"

# -----------------------------
# SPARK SESSION
# -----------------------------
spark = SparkSession.builder \
    .appName("GCS-to-BQ-PySpark") \
    .getOrCreate()

# -----------------------------
# READ CSV
# -----------------------------
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(INPUT_FILE)

# -----------------------------
# CLEAN / TRANSFORM
# -----------------------------
df_clean = df.na.replace("", None)

# -----------------------------
# WRITE TO BIGQUERY
# -----------------------------
df_clean.write \
    .format("bigquery") \
    .option("table", FULL_TABLE_ID) \
    .mode("append") \
    .save()

print("Data successfully written to BigQuery 🚀")