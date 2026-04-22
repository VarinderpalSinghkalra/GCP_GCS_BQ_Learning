from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType

# CONFIG
PROJECT_ID = "data-engineering-488013"
BUCKET = "datavip-dataflow"
INPUT_FILE = f"gs://{BUCKET}/spend_cube_clean.csv"
TABLE = f"{PROJECT_ID}.conversational_demo_df.sample_spenddata_raw"

spark = SparkSession.builder.appName("Dedup Pipeline").getOrCreate()

# SCHEMA
schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("product", StringType(), True),
    StructField("category", StringType(), True),
    StructField("amount", StringType(), True),
    StructField("transaction_date", StringType(), True),
    StructField("city", StringType(), True),
])

# READ NEW DATA
new_df = spark.read.option("header", "true").schema(schema).csv(INPUT_FILE)

# REMOVE INTERNAL DUPLICATES
new_df = new_df.dropDuplicates(["transaction_id"])

# READ EXISTING DATA FROM BIGQUERY
existing_df = spark.read \
    .format("bigquery") \
    .option("table", TABLE) \
    .load()

# ANTI JOIN (KEEP ONLY NEW RECORDS)
final_df = new_df.join(
    existing_df.select("transaction_id"),
    on="transaction_id",
    how="left_anti"
)

print("Records after removing duplicates:")
final_df.show()

# WRITE ONLY NEW DATA
final_df.write \
    .format("bigquery") \
    .option("table", TABLE) \
    .option("temporaryGcsBucket", BUCKET) \
    .mode("append") \
    .save()

print("✅ Only new records inserted (duplicates skipped)")
