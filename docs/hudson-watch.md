In addition to writing directly to a dataset, you can also tell hudson to watch your filesystem for changes and automatically write new data to the dataset and cleanup old data.

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

Tell Hudson to start watching a location on your filesystem.

```Python
print("👀 Watching a directory")
hudson_client.watch()
```

Now, write some data to where Hudson is watching.

You can see where hudson is watching by looking at `hudson_client.client_watch_dir`. This can also be something you override yourself.

Currently jsonl files are supported. You can write as many documents as you want to a single file. The file name doesn't matter, but it must end in `.jsonl`.

Also hudson will automatically create a new file when the current file reaches a certain number of lines. The default size is `hudson_client.min_batch_upload_size` (64). You can change this by setting `hudson_client.min_batch_upload_size` or updating the `HudsonClientConfig` object yourself.

```Python
import random
import string

import torch
from docarray import Document

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
```

Tell Hudson to stop watching

```Python
print("🛑 Stop watching")
hudson_client.stop()
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
{!../docs_src/hudson-watch.py!}
```
