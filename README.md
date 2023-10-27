# Iroha news subscription code

## Concept

Iroha mailer is a tool that would allow our developers
to automate sending the emails to our community
when they post updates in a select GitHub repository.

It uses GitHub CI to automatically send emails whenever someone merges a PR in the news repository.

The server side works constantly: the users need to subscribe or unsubscribe, and the developers can preview the news. In addition to the emails, these previews are saved in PDF and stored separately.

The Iroha mailer pipeline works with the following steps:

* As soon as someone merges a news PR, the CI side is triggered to send an update to the server
* The server renders the stylized emails using the data provided by CI.
* The server sends the HTML emails to all subscribers of the repository.

## Parts

* [Server side](./server) - server code and its Docker config; available on [DockerHub](https://hub.docker.com/repository/docker/iamgrid/iroha_mailer/general)
* [CI side](./ci) - needed for GitHub CI, currently only contains Python scripts
