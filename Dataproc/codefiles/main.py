from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType

# -----------------------------
# CONFIG
# -----------------------------
PROJECT_ID = "data-engineering-488013"
BUCKET = "datavip-dataflow"
INPUT_FILE = f"gs://{BUCKET}/spend_cube_clean.csv"

BQ_DATASET = "conversational_demo_df"
BQ_TABLE = "sample_spenddata_raw"
FULL_TABLE = f"{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"

# -----------------------------
# SPARK SESSION
# -----------------------------
spark = SparkSession.builder \
    .appName("GCS to BigQuery - Final Working Version") \
    .getOrCreate()

# -----------------------------
# DEFINE SCHEMA (MATCH BQ EXACTLY)
# -----------------------------
schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("product", StringType(), True),
    StructField("category", StringType(), True),
    StructField("amount", StringType(), True),
    StructField("transaction_date", StringType(), True),  # 🔥 keep STRING
    StructField("city", StringType(), True),
])

# -----------------------------
# READ CSV
# -----------------------------
df = spark.read \
    .option("header", "true") \
    .schema(schema) \
    .csv(INPUT_FILE)

print("Schema after read:")
df.printSchema()

# -----------------------------
# CLEANING
# -----------------------------
df = df.dropDuplicates()

print("Final Schema:")
df.printSchema()

df.show(5)

# -----------------------------
# WRITE TO BIGQUERY
# -----------------------------
df.write \
    .format("bigquery") \
    .option("table", FULL_TABLE) \
    .option("temporaryGcsBucket", BUCKET) \
    .mode("append") \
    .save()

print("✅ Data successfully written to BigQuery")
