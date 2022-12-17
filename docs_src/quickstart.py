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
print("✍️ Writing to the dataset")
n = 1_000
str_len = 100
t0 = time.time()
hudson_client.write_dataset(
    namespace_id=namespace.id,
    dataset_id=dataset.id,
    data=DocumentArray(
        [
            Document(
                text="".join(
                    random.choices(string.ascii_uppercase + string.digits, k=str_len)
                ),
                embedding=torch.randn(768),
            )
        ]
        * n,
    ),
)
print(f"⏰ Took {time.time() - t0:.2f} seconds to write {n} documents")


#
#   TODO: Read from the dataset – no pytorch on the server but pytorch on the client!
#
print("📖 Reading from the dataset")
df = hudson_client.read_dataset(
    namespace_id=namespace.id,
    dataset_id=dataset.id,
)

print("🧹 Cleaning up!")
hudson_client.delete_namespace(namespace.id)
