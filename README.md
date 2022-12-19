<p align="center">
  <b><a href="https://hudson.corletti.xyz"><img src="https://github.com/anthonycorletti/hudson/blob/main/docs/img/hudson.png?raw=true" alt="Hudson"></a></b>
</p>
<p align="center">
    <em>🎶If you havin' data problems I feel bad for you son.<br>I got 99 problems and a framework ain't one.🎶</em>
</p>
<p align="center">
    <a href="https://github.com/anthonycorletti/hudson/actions?query=workflow%3Atest" target="_blank">
        <img src="https://github.com/anthonycorletti/hudson/workflows/test/badge.svg" alt="test">
    </a>
    <a href="https://github.com/anthonycorletti/hudson/actions?query=workflow%3Apublish" target="_blank">
        <img src="https://github.com/anthonycorletti/hudson/workflows/publish/badge.svg" alt="publish">
    </a>
    <a href="https://codecov.io/gh/anthonycorletti/hudson" target="_blank">
        <img src="https://codecov.io/gh/anthonycorletti/hudson/branch/main/graph/badge.svg?token=2K8O7U59KH" alt="coverage">
    </a>
    <a href="https://pypi.org/project/hudson/" target="_blank">
        <img alt="pypi" src="https://img.shields.io/pypi/v/hudson?color=blue">
    </a>
</p>

---

_:warning: Hudson is still in alpha and shouldn't be used in production yet. If you have any questions, feedback, or feature suggestions, please [create an issue on Github](https://github.com/anthonycorletti/hudson/issues/new/choose)._

**Documentation**: <a href="https://hudson.corletti.xyz" target="_blank">https://hudson.corletti.xyz</a>

**Source Code**: <a href="https://github.com/anthonycorletti/hudson" target="_blank">https://github.com/anthonycorletti/hudson</a>

---

Build multi-modal data applications with ease.

Some major features of Hudson are;

* 🐍 **Async Python**: Hudson is 100% async. It's built on top of [FastAPI](https://fastapi.tiangolo.com/), [SQLModel](https://sqlmodel.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [Pydantic](https://docs.pydantic.dev), [DocArray](https://docarray.jina.ai/), and more.
* 🧱 **DocArray**: Hudson uses [DocArray](https://docarray.jina.ai/) so you can work with multi-modal data without having to do work to support each modality separately.
* 🐻‍❄️ **Polars**: Hudson uses [Polars](https://pola-rs.github.io/polars-book/) for blazing fast server-side data processing.
* ☁️ **Modal**: Hudson deploys on [Modal](https://modal.com) by default. No need to worry about infrastructure, Kubernetes, or containers!
* 📨 **Publish-subscribe** functionality built right in. Create any workflow you need with Hudson!
* ✍️ **Just write code!** No YAML necessary.

## What's Hudson?

Hudson is a framework for building multi-modal data applications.

Hudson runs as a server-side application and provides a REST API for your application to communicate with. Hudson also provides a python client library that you can use to interact with the server.

## Use cases

1. **Multi-modal data analytics**: One way to work with data across any modality.
1. **Processing data in the cloud**: Build data processing pipelines with ease – no need to worry about infrastructure, plugging different cloud tools together, or writing code to support each modality.
1. **Machine learning data analytics**: Send data from your machine learning workflow to Hudson for processing and analysis. It already works with any modality and framework – you just have to send in the data and embeddings and that's it!

## Installing Hudson

Hudson is available on PyPI. You can install it with pip:

```sh
pip install hudson
```

## Contributing & Sponsorship

One of the easiest and best ways to contribute to Hudson is to star the project on [GitHub](https://github.com/anthonycorletti/hdson) and share it with your colleagues, friends, and anyone who might want to build data applications without the hassle.

If you would like to contribute, please read Hudson's [contributing guidelines](./contributing.md). [Issues](https://github.com/anthonycorletti/hudson/issues/new/choose) and [pull requests](https://github.com/anthonycorletti/hudson/compare) are very welcome.

If you would like to sponsor the project, you can do so [here](https://github.com/sponsors/anthonycorletti)
