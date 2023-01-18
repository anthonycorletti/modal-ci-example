# modal-ci-example

Evaluating modal as a complete replacement for local development, including CI.

Open questions:
- how to encapsulate all modal related code such that it doesn't change the local project's design? in order to make these tests run, `const.py` and `settings.py` had to be pulled out of `modalci` and into the project root. this is not really ideal. :thinking: how to make that better?
