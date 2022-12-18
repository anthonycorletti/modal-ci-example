## Install Hudson

```sh
pip install hudson
```

## Run postgres

Hudson uses postgres as it's relational database. You can run postgres locally or in a docker container. For this example, we'll run postgres in a docker container. You can also run postgres locally if you prefer.

```sh
docker run --rm -d --name hudson-postgres \
-p 5432:5432 \
-e POSTGRES_PASSWORD=hudson \
-e POSTGRES_USER=hudson \
-e POSTGRES_PASSWORD=hudson \
-e POSTGRES_DB=hudson \
postgres:15.1
```

Run hudson's database migrations.

```sh
alembic upgrade head
```

## Start Hudson

```sh
hudson server
```

## Run the example

In another shell session, stream some data into Hudson.

The code below is copy-pastable and runs as is.

First, create your namespace.

```Python
from hudson import hudson_client

print("🎉 Creating a namespace")

namespace = hudson_client.create_namespace(
    name="quickstart",
)
```

Then, create a dataset.

```Python
print("🎉 Creating a dataset")

dataset = hudson_client.create_dataset(
    namespace_id=namespace.id,
    name="quickstart",
)
```

Now, write a DocumentArray to the dataset.

```Python
import random
import string
import time

import torch
from docarray import Document, DocumentArray

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
```

You can then read the data back out.

```Python
print("📖 Reading from the dataset")

t0 = time.time()
da = hudson_client.read_dataset(
    namespace_id=namespace.id,
    dataset_id=dataset.id,
)

print(f"⏰ Took {time.time() - t0:.2f} seconds to read {n} documents")
```

Optionally, you can also plot embeddings automatically! Note that these are randomly generated embeddings.

```Python
print("📊 Plotting the embeddings")

da.plot_embeddings()
```

Finally, clean up everything by deleting the namespace.

```Python
print("🧹 Cleaning up!")

hudson_client.delete_namespace(namespace.id)
```

## Full example

```Python
{!../docs_src/quickstart.py!}
```
