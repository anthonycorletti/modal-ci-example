import random
import string
import time

from docarray import Document, DocumentArray

from hudson import client

#
#   Create a namespace.
#
print("🎉 Creating a namespace")
namespace = client.create_namespace(
    name="quickstart",
)

#
#   Create a dataset.
#
print("🎉 Creating a dataset")
dataset = client.create_dataset(
    namespace_id=namespace.id,
    name="quickstart",
)

#
#   Write a DocumentArray to the dataset.
#
print("✍️ Writing to the dataset")
n = 10_000
str_len = 100
t0 = time.time()
client.write_dataset(
    namespace_id=namespace.id,
    dataset_id=dataset.id,
    data=DocumentArray(
        [
            Document(
                text="".join(
                    random.choices(string.ascii_uppercase + string.digits, k=str_len)
                ),
                embedding=[random.random() for _ in range(128)],
            )
        ]
        * n,
    ),
)
print(f"⏰ Took {time.time() - t0:.2f} seconds to write {n} documents")


print("🧹 Cleaning up!")
client.delete_namespace(namespace.id)
