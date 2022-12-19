Building messaging workflows with hudson is incredibly simple.

## So what's a messaging workflow?

A messaging workflow is a workflow that uses a publish-subscribe pattern to communicate between different parts of your application or applications. This is a very common pattern in software development and is used in many different applications.

## Why use a messaging workflow?

There are many reasons to use a messaging workflow. Here are a few:

1. You want to kick off simultaneous processes at the same time from a single event.
1. You want to run a process in the background and not block the main thread.
1. Your application has to submit data to external services and you want to do it in parallel.

## Using Hudson to build messaging workflows

Hudson provides a simple API for building messaging workflows.

You can use it to build workflows that run in the cloud or on your local machine.

The only way to do this now is through the REST API. In the future, hudson will have a UI and other client packages for building workflows.

### Getting started

Install and start hudson. You can checkout the [quickstart](./quickstart.md) guide for more information.

Once hudson is up and running, you can start building your messaging workflow.

### Making a namespace

The first thing you need to do is make a namespace. A namespace is a collection of resources in hudson you want to use for a particular purpose.

```python
from hudson import hudson_client

ns = hudson.create_namespace("my-namespace")

print(ns.id)
```

### Making a topic

A topic is a place where messages are published to. You can think of it as a channel.

Grab the namespace ID from the previous step and use it to make a topic.

```shell
curl -X POST \
http://localhost:8000/namespaces/{ns.id}/topics \
-H 'Content-Type: application/json' \
-d '{ "name": "my-topic" }'
```



### Making subscriptions

A subscription is a place where messages are received from a topic. These subscribers then take the message and can do anything with it.

Take the topic ID from the previous response and use it to create a subscription.

```shell
curl -X POST \
http://localhost:8000/namespaces/{ns.id}/topic/{topic.id}/subscriptions \
-H 'Content-Type: application/json' \
-d '{ "name": "my-subscription", "topic_id": {topic.id}, "delivery_type": "pull", "endpoint": "https://example.com/api/do-something-with-my-data" }'
```

You can do this as many times as you want to create as many subscriptions as you want for any topic.

### Publishing messages

Now that you have a topic and some subscriptions, you can publish messages to the topic.

```shell
curl -X POST \
http://localhost:8000/namespaces/{ns.id}/topic/{topic.id}/publish \
-H 'Content-Type: application/json' \
-d '{ "data": "my data" }'
```

This will publish a message to the topic and send it to all the subscriptions.

### Cleaning up

When you're done with a namespace, you can delete it.

```python
from hudson import hudson_client

hudson.delete_namespace("my-namespace")
```

## Questions?

If you have any questions, comments, or feedback about building workflows with hudson, please [make an issue in GitHub](https://github.com/anthonycorletti/hudson/issues/new/choose) with as much detail as possible.
