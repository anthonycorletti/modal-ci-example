import random
import string
import time

import torch
from docarray import Document, DocumentArray

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
print("✍️  Writing data")
n = hudson_client.min_batch_upload_size
watch_dir = hudson_client.client_watch_dir
num_batches = 100
str_len = 100
for batch in range(num_batches):
    with open(f"{watch_dir}/data-{batch}.jsonl", "w") as f:
        for i in range(n):
            doc = Document(
                text="".join(
                    random.choices(
                        string.ascii_uppercase + string.digits,
                        k=str_len,
                    )
                ),
                embedding=torch.randn(768),
            )
            f.write(doc.to_json() + "\n")

#
#   Tell Hudson to stop watching.
#
print("🛑 Stop watching")
hudson_client.stop()

#
#   Read the data from the dataset.
#
print("📖 Reading from the dataset")
t0 = time.time()
da = hudson_client.read_dataset(
    namespace_id=namespace.id,
    dataset_id=dataset.id,
)
assert isinstance(da, DocumentArray)
print(f"⏰ Took {time.time() - t0:.2f} seconds to read {len(da)} documents")

#
#   Clean up.
#
print("🧹 Cleaning up!")
hudson_client.delete_namespace(namespace.id)
