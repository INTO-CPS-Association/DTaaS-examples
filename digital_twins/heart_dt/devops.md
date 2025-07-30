# Heart Digital Twin

This example demonstrates the use of DevOps features of the DTaaS platform for the Heart Digital Twin.
GitLab DevOps pipelines are used to automate and manage its lifecycle.

## Pipeline Configuration

The `.gitlab-ci.yml` file controls the sequence of lifecycle script executions for the heart digital twin. It defines multiple stages:

* **create**: Sets up the Python virtual environment and installs dependencies
* **execute**: Runs the heart digital twin application

## Runner Requirements

**Important**: This digital twin requires a **shell-based GitLab runner**, not a Docker-based runner. The application needs:

* Access to the host system's Python environment
* Ability to create and manage Python virtual environments
* File system access for model loading and data processing
* Network access for the web application

Docker-based runners may restrict network or filesystem access critical to this digital twin.

## Alternative Execution Mode: Docker

You also have the option to use **Docker-based execution** for the heart digital twin — while still using a **shell-based GitLab runner**.

The corresponding GitLab CI file for this approach is `gitlab-ci-docker.yml`

To enable this alternative execution path, you'll need to modify the root `.gitlab-ci.yml` to reference this Docker-based pipeline (`gitlab-ci-docker.yml`) instead of the default one.

## Artifacts and Outputs

This example produces:

* Heart simulation outputs
* Web application logs

These are saved as artifacts in the GitLab pipeline. The virtual environment created in the `create` stage is also preserved as an artifact for reuse in the `execute` stage.

## Lifecycle Scripts

The digital twin uses the following lifecycle scripts:

* `lifecycle/create`: Sets up the Python environment and installs required packages
* `lifecycle/execute`: Starts the heart digital twin web application

Each script is designed for shell execution and requires appropriate permissions.