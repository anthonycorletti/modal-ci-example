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
#   Write a DocumentArray to the dataset.
#
print("🧱 Building the dataset")
n = 100
str_len = 100
data = DocumentArray(
    [
        Document(
            text="".join(
                random.choices(string.ascii_uppercase + string.digits, k=str_len)
            ),
            embedding=torch.randn(768),
        )
        for _ in range(n)
    ]
)
print("✍️  Writing to the dataset")
t0 = time.time()
hudson_client.write_dataset(
    namespace_id=namespace.id,
    dataset_id=dataset.id,
    data=data,
)
print(f"⏰ Took {time.time() - t0:.2f} seconds to write {n} documents")


print("📖 Reading from the dataset")
t0 = time.time()
da = hudson_client.read_dataset(
    namespace_id=namespace.id,
    dataset_id=dataset.id,
)
print(f"⏰ Took {time.time() - t0:.2f} seconds to read {n} documents")

print("🧹 Cleaning up!")
hudson_client.delete_namespace(namespace.id)
