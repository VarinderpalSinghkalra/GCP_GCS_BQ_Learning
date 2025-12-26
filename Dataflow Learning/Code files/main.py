import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import bigquery
import csv
from io import StringIO

# -----------------------------
# CONFIG
# -----------------------------
PROJECT = "data-engineering-479617"
REGION = "us-central1"

INPUT_FILE = "gs://datavip/spend_cube_clean.csv"

BQ_PROJECT = "data-engineering-479617"
BQ_DATASET = "conversational_demo_df"
BQ_TABLE = "sample_spenddata_raw"
FULL_TABLE_ID = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

TEMP_LOCATION = "gs://datavip/temp"
STAGING_LOCATION = "gs://datavip/staging"

SERVICE_ACCOUNT = "sql-bot-sa@data-engineering-479617.iam.gserviceaccount.com"

# -----------------------------
# STEP 1: CREATE BQ TABLE FROM CSV HEADER
# -----------------------------
def create_table_from_csv_header():
    client = bigquery.Client(project=BQ_PROJECT)

    # Ensure dataset exists
    dataset_ref = bigquery.Dataset(f"{BQ_PROJECT}.{BQ_DATASET}")
    try:
        client.get_dataset(dataset_ref)
    except Exception:
        client.create_dataset(dataset_ref)

    # Read header directly from GCS
    import subprocess
    header_line = subprocess.check_output(
        ["gsutil", "cat", INPUT_FILE],
        text=True
    ).splitlines()[0]

    headers = next(csv.reader([header_line]))

    schema = [bigquery.SchemaField(col, "STRING") for col in headers]

    # Delete table if exists
    try:
        client.delete_table(FULL_TABLE_ID)
    except Exception:
        pass

    table = bigquery.Table(FULL_TABLE_ID, schema=schema)
    client.create_table(table)

    return headers

# -----------------------------
# CSV PARSER (DYNAMIC)
# -----------------------------
class ParseCSV(beam.DoFn):
    def process(self, line, header):
        reader = csv.DictReader(
            StringIO(line),
            fieldnames=header
        )
        for row in reader:
            # Skip header row
            if row[header[0]] == header[0]:
                return
            yield {k: (v if v != "" else None) for k, v in row.items()}

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":

    # 🔥 Pre-flight: Create table dynamically
    HEADER = create_table_from_csv_header()

    options = PipelineOptions(
        runner="DataflowRunner",
        project=PROJECT,
        region=REGION,
        temp_location=TEMP_LOCATION,
        staging_location=STAGING_LOCATION,
        service_account_email=SERVICE_ACCOUNT,
        job_name="gcs-to-bq-csv-raw-dynamic",
        save_main_session=True
    )

    with beam.Pipeline(options=options) as p:

        (
            p
            | "Read CSV" >> beam.io.ReadFromText(INPUT_FILE)
            | "Parse CSV Rows" >> beam.ParDo(
                ParseCSV(),
                header=beam.pvalue.AsSingleton(
                    p | "Header PCollection" >> beam.Create([HEADER])
                )
            )
            | "Write to BigQuery (Streaming)" >> beam.io.WriteToBigQuery(
                FULL_TABLE_ID,
                method=beam.io.WriteToBigQuery.Method.STREAMING_INSERTS,
                create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )
        )