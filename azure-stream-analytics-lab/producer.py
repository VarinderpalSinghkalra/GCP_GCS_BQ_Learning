import json
import random
from datetime import datetime
from azure.eventhub import EventHubProducerClient, EventData

CONNECTION_STRING = "<EVENT_HUB_CONNECTION_STRING>"
EVENT_HUB_NAME = "telecomeventhub"

producer = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STRING,
    eventhub_name=EVENT_HUB_NAME
)

batch = producer.create_batch()

for i in range(1000):

    event = {
        "CallRecTime": datetime.utcnow().isoformat(),
        "CallingIMSI": str(random.randint(100000,999999)),
        "SwitchNum": random.randint(1,5)
    }

    batch.add(EventData(json.dumps(event)))

producer.send_batch(batch)

producer.close()

print("1000 Events Sent Successfully")