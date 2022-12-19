import time

from docarray import Document, DocumentArray

from hudson import hudson_client

#
#   Create a namespace.
#
print("🎉 Creating a namespace")
namespace = hudson_client.create_namespace(
    name="tabular-example",
)

#
#   Create a dataset.
#
print("🎉 Creating a dataset")
dataset = hudson_client.create_dataset(
    namespace_id=namespace.id,
    name="tabular-example-dataset",
)

#
#   Write a DocumentArray to the dataset.
#
print("🧱 Building the dataset")
n = 100
data = DocumentArray(
    [
        Document(
            tags={
                "english": "hello",
                "german": "hallo",
                "french": "bonjour",
                "spanish": "hola",
                "italian": "ciao",
            },
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
