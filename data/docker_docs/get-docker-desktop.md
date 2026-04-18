
# description
This concept page will teach you download Docker Desktop and install it on Windows, Mac, and Linux
## summary
  Getting Docker Desktop up and running is the first crucial step for
  developers diving into containerization, offering a seamless and
  user-friendly interface for managing Docker containers. Docker Desktop
  simplifies the process of building, sharing, and running applications in
  containers, ensuring consistency across different environments.

## Explanation

Docker Desktop is the all-in-one package to build images, run containers, and so much more.
This guide will walk you through the installation process, enabling you to experience Docker Desktop firsthand.


> **Docker Desktop terms**
>
> Commercial use of Docker Desktop in larger enterprises (more than 250
> employees OR more than $10 million USD in annual revenue) requires a [paid subscription](https://www.docker.com/pricing?ref=Docs&refAction=DocsGetDockerDesktop).


### title="Docker Desktop for Mac"
  description="[Download (Apple Silicon)](https://desktop.docker.com/mac/main/arm64/Docker.dmg?utm_source=docker&utm_medium=webreferral&utm_campaign=docs-driven-download-mac-arm64) | [Download (Intel)](https://desktop.docker.com/mac/main/amd64/Docker.dmg?utm_source=docker&utm_medium=webreferral&utm_campaign=docs-driven-download-mac-amd64) | [Install instructions](/desktop/setup/install/mac-install)"
  
### title="Docker Desktop for Windows"
  description="[Download](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe?utm_source=docker&utm_medium=webreferral&utm_campaign=docs-driven-download-windows) | [Install instructions](/desktop/setup/install/windows-install)"
 
### title="Docker Desktop for Linux"
  description="[Install instructions](/desktop/setup/install/linux/)"

Once it's installed, complete the setup process and you're all set to run a Docker container.

## Try it out

In this hands-on guide, you will see how to run a Docker container using Docker Desktop.

Follow the instructions to run a container using the CLI.


## Run your first container

Open your CLI terminal and start a container by running the `docker run` command:


```console
$ docker run -d -p 8080:80 docker/welcome-to-docker
```

## Access the frontend

For this container, the frontend is accessible on port `8080`. To open the website, visit [http://localhost:8080](http://localhost:8080) in your browser.

## Manage containers using Docker Desktop


1. Open Docker Desktop and select the **Containers** field on the left sidebar.
2. You can view information about your container including logs, and files, and even access the shell by selecting the **Exec** tab.
3. Select the **Inspect** field to obtain detailed information about the container. You can perform various actions such as pause, resume, start or stop containers, or explore the **Logs**, **Bind mounts**, **Exec**, **Files**, and **Stats** tabs.

Docker Desktop simplifies container management for developers by streamlining the setup, configuration, and compatibility of applications across different environments, thereby addressing the pain points of environment inconsistencies and deployment challenges.

## What's next?

Now that you have Docker Desktop installed and ran your first container, it's time to start developing with containers.