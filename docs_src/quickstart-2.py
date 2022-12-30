import random
import string
import time

import torch
from docarray import Document

from hudson import hudson_client

#
#   Create a namespace.
#
print("🎉 Creating a namespace")
namespace = hudson_client.create_namespace(
    name="quickstart",
)

#
#   Create a dataset.
#
print("🎉 Creating a dataset")
dataset = hudson_client.create_dataset(
    namespace_id=namespace.id,
    name="quickstart",
)

#
#   Tell Hudson to start watching for data.
#
print("👀 Watching for data")
hudson_client.watch()

#
#   Write data where hudson is watching.
#
print("✍️  Writing to the watch location")
n = 100
str_len = 100
with open(f"{hudson_client.client_watch_dir}/data-{int(time.time())}.jsonl", "w") as f:
    for _ in range(n):
        doc = Document(
            text="".join(
                random.choices(string.ascii_uppercase + string.digits, k=str_len)
            ),
            embedding=torch.randn(768),
        )
        f.write(doc.to_json() + "\n")

time.sleep(1)
#
#   Tell Hudson to stop watching for data.
#
print("👀 Stopped watching for data")
hudson_client.stop()

# print("📖 Reading from the dataset")
# t0 = time.time()
# da = hudson_client.read_dataset(
#     namespace_id=namespace.id,
#     dataset_id=dataset.id,
# )
# print(f"⏰ Took {time.time() - t0:.2f} seconds to read {n} documents")


# print("🧹 Cleaning up!")
# hudson_client.delete_namespace(namespace.id)
