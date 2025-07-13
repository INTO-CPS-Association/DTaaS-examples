# Heart Digital Twin

This example demonstrates the use of DevOps features of the DTaaS platform for the Heart Digital Twin.
The GitLab DevOps pipelines are used for providing this feature in the DTaaS.

## Pipeline Configuration

The `.gitlab-ci.yml` file controls the sequence of executing the lifecycle
scripts of the heart digital twin. The configuration format of `.gitlab-ci.yml`
permits specifying stages for execution of a program.

This heart digital twin example uses a multi-stage pipeline with the following stages:

- **create**: Sets up the Python virtual environment and installs dependencies
- **execute**: Runs the heart digital twin application

## Runner Requirements

**Important**: This digital twin requires a **shell-based GitLab runner**, not a Docker-based runner.
The heart digital twin application needs:

- Direct access to the host system's Python environment
- Ability to create and manage Python virtual environments
- File system access for model loading and data processing
- Network access for the web application

Docker-based runners may have limitations with network configurations that are essential for this digital twin.

## Artifacts and Outputs

This example produces heart simulation outputs and web application logs which are 
saved as artifacts in the GitLab pipeline. The virtual environment created during 
the create stage is preserved as an artifact for use in subsequent stages.

You can access the pipeline artifacts at your GitLab instance's artifacts repository.

## Lifecycle Scripts

The digital twin uses the following lifecycle scripts:

- `lifecycle/create`: Sets up the Python environment and installs required packages
- `lifecycle/execute`: Starts the heart digital twin web application

Each script is designed to work in a shell environment and requires appropriate
permissions to execute.