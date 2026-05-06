# ============================================================
# FILE NAME : bigtable_dataflow_pipeline.py
# DESCRIPTION:
# Dynamic Apache Beam + Dataflow Pipeline
# Creates Bigtable Table + Column Family
# Inserts Employee Records Automatically
# ============================================================

import apache_beam as beam

from apache_beam.options.pipeline_options import PipelineOptions

from google.cloud.bigtable_admin_v2 import BigtableTableAdminClient

from google.cloud.bigtable_admin_v2.types import (
    Table,
    ColumnFamily,
    CreateTableRequest,
)

from google.cloud.bigtable.row import DirectRow

from google.cloud.bigtable import Client

from google.cloud.bigtable.column_family import MaxVersionsGCRule


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ID = "gcp-project1-491103"

INSTANCE_ID = "prachi-bigtable"

TABLE_ID = "employee"

COLUMN_FAMILY_ID = "profile"


# ============================================================
# SAMPLE EMPLOYEE DATA
# ============================================================

EMPLOYEE_DATA = [

    {
        "emp_id": "emp1001",
        "name": "Varinder",
        "city": "Delhi",
        "role": "DataEngineer"
    },

    {
        "emp_id": "emp1002",
        "name": "Rahul",
        "city": "Noida",
        "role": "CloudEngineer"
    },

    {
        "emp_id": "emp1003",
        "name": "Aman",
        "city": "Gurgaon",
        "role": "DevOpsEngineer"
    },

    {
        "emp_id": "emp1004",
        "name": "Priya",
        "city": "Pune",
        "role": "SoftwareEngineer"
    },

    {
        "emp_id": "emp1005",
        "name": "Simran",
        "city": "Chandigarh",
        "role": "DataAnalyst"
    },

    {
        "emp_id": "emp1006",
        "name": "Arjun",
        "city": "Bangalore",
        "role": "PlatformEngineer"
    },

    {
        "emp_id": "emp1007",
        "name": "Karan",
        "city": "Hyderabad",
        "role": "MLEngineer"
    },

    {
        "emp_id": "emp1008",
        "name": "Sneha",
        "city": "Mumbai",
        "role": "BackendDeveloper"
    },

    {
        "emp_id": "emp1009",
        "name": "Ritika",
        "city": "Jaipur",
        "role": "DataScientist"
    },

    {
        "emp_id": "emp1010",
        "name": "Harshit",
        "city": "Lucknow",
        "role": "SiteReliabilityEngineer"
    }
]


# ============================================================
# CREATE BIGTABLE TABLE + COLUMN FAMILY
# ============================================================

def create_bigtable_resources():

    admin_client = BigtableTableAdminClient()

    instance_path = admin_client.instance_path(
        PROJECT_ID,
        INSTANCE_ID
    )

    table_path = admin_client.table_path(
        PROJECT_ID,
        INSTANCE_ID,
        TABLE_ID
    )

    try:

        admin_client.get_table(name=table_path)

        print(f"Table '{TABLE_ID}' already exists.")

    except Exception:

        table = Table(
            column_families={
                COLUMN_FAMILY_ID: ColumnFamily(
                    gc_rule=MaxVersionsGCRule(1).to_pb()
                )
            }
        )

        request = CreateTableRequest(
            parent=instance_path,
            table_id=TABLE_ID,
            table=table
        )

        admin_client.create_table(request=request)

        print(f"Table '{TABLE_ID}' created successfully.")


# ============================================================
# APACHE BEAM TRANSFORM
# ============================================================

class WriteToBigtable(beam.DoFn):

    def setup(self):

        self.client = Client(
            project=PROJECT_ID,
            admin=True
        )

        self.instance = self.client.instance(
            INSTANCE_ID
        )

        self.table = self.instance.table(
            TABLE_ID
        )

    def process(self, element):

        row_key = element["emp_id"]

        row = DirectRow(
            row_key=row_key.encode("utf-8")
        )

        # Insert Name
        row.set_cell(
            COLUMN_FAMILY_ID,
            "name",
            element["name"]
        )

        # Insert City
        row.set_cell(
            COLUMN_FAMILY_ID,
            "city",
            element["city"]
        )

        # Insert Role
        row.set_cell(
            COLUMN_FAMILY_ID,
            "role",
            element["role"]
        )

        # Commit Row
        self.table.mutate_rows([row])

        print(f"Inserted Row: {row_key}")

        yield element


# ============================================================
# MAIN PIPELINE
# ============================================================

def run():

    # Create Table + Column Family Automatically
    create_bigtable_resources()

    pipeline_options = PipelineOptions(
        runner="DirectRunner",
        save_main_session=True
    )

    with beam.Pipeline(options=pipeline_options) as pipeline:

        (
            pipeline

            | "Create Employee Records"
            >> beam.Create(EMPLOYEE_DATA)

            | "Write Records To Bigtable"
            >> beam.ParDo(WriteToBigtable())
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run()