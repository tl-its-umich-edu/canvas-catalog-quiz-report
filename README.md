# catalog scripts

Designed to support University of Michigan School of Publish Health Canvas Catalog quiz and survey report needs.

## Development

### Pre-requisities

The sections below provide instructions for configuring, installing, and using the application.
Depending on the environment you plan to run the application in, you may
also need to install some or all of the following:

- [Python 3.8](https://docs.python.org/3.8/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

While performing any of the actions described below, use a terminal, text editor, or file
utility as necessary. Sample terminal commands are provided for some steps.

### Configuration

Before running the application, you will need to prepare the configuration file: `env.json` file containing key-value pairs that will be added to the environment. See the **Installation & Usage** section below for details on where the file will need to be located.

- `env.json`

  The `env.son` file serves as the primary configuration file, loading credentials for kaltura admins. A template called `env_sample.json` has been provided in
  the `config` directory. The comments before the variables in the template should describe the purpose of each; some recommended values have been provided. If you use the approach described below in **Installation & Usage - With Docker**, you can use the provided values to connect to the database managed by Docker.

The meanings of the keys and their expected values are described in the table below.

| **Key**             | **Description**                           |
| ------------------- | ----------------------------------------- |
| `API_URL`           | URL value for the Canvas Catalog instance |
| `API_KEY`           | Key value for API call                    |
| `TERM_ID`           | The Canvas cademic term id for courses    |
| `CANVAS_ACCOUNT_ID` | The Canvas subaccount id for courses      |

---

Create your own versions of `env.json`, and be prepared to move them to specific directories.

### Installation & Usage

#### With Docker

Before beginning, perform the following additional steps to configure the project for Docker.

1.  Build an docker image

    ```sh
    docker build -t catalog .
    ```

2.  Copy the command below and replace the "TARGET_FOLDER" with a folder path on your local machine. Run the command. The script will create a folder for each course within the given account, and download all "student analysis" reports for all quizzes objects within the course, if the course has at least one student.

    ```sh
    docker run -it -v TARGET_FOLDER:/tmp/ catalog
    ```
