# Installation and Usage Guide for Files-To-S3

This guide will walk you through the process of installing and using the Files-To-S3 Python package. Files-To-S3 is a package that uploads files from a local directory to an Amazon S3 bucket.

## Prerequisites

Before you begin, ensure that you have the following prerequisites installed on your system:

1. **Python**: You must have Python installed on your system. You can download it from [Python's official website](https://www.python.org/downloads/).

2. **AWS CLI**: This script relies on the AWS Command Line Interface (CLI) to interact with Amazon S3. You can install the AWS CLI and configure it with your AWS credentials. Get the AWS CLI from [AWS CLI Install](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

    - **Windows Installer**: Download the AWS CLI Windows Installer.

    - **Install AWS CLI**: Run the downloaded installer to install the AWS CLI on your Windows system. During installation, you can choose to add the AWS CLI to your system's PATH to make it accessible from the Command Prompt or PowerShell.

    - **(Optional) Configure AWS CLI with SSO**: Before using the federal identity, you need to configure the AWS CLI with SSO by following these steps:

      1. Open your command prompt or terminal.

      2. Run the following command to initiate the SSO configuration process:

            ```bash
            aws configure sso
            ```

        The command will prompt you to enter the following information:

        - **SSO session name (Recommended):** This can be any name you choose, e.g., "AWS-1."

        - **SSO start URL [None]:** Enter the SSO start URL provided to you (e.g., https://d-906703e724.awsapps.com/start#). If not provided, leave this field blank.

        - **SSO region [None]:** Enter the AWS region you want to use (e.g., us-east-1). If not provided, leave this field blank.

        - **SSO registration scopes [sso:account:access]:** Leave this field blank.

        - **CLI default client Region [None]:** (e.g., us-east-1). If not provided, leave this field blank.

        - **CLI default output format [None]:** Leave this field blank.

        - **CLI profile name [Access-0000000]:** If profile name is correct press ENTER

        Follow the prompts to sign in using your federal identity and complete the SSO configuration.

        Once you have successfully configured the AWS CLI with SSO, you can use the upload_to_s3 script to upload files to Amazon S3.

        If you encounter any issues during the SSO configuration, please refer to the official AWS documentation for AWS Single Sign-On (AWS SSO) for further guidance.


3. **Pip**: Pip is the package manager for Python. It usually comes with Python, but make sure it's installed. You can check by running `pip --version`.

4. **Virtual Environment (Optional)**: We recommend using a virtual environment to manage your Python packages. You can create a virtual environment using the `venv` module. For Windows, use Command Prompt; for macOS and Linux, you can use your terminal.

    ```bash
    # For macOS and Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

## Installation Steps

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your_username/Files-To-S3.git
   ```


2. **Install Package Requirements**:

    Change your current directory to the root of the repository and install the required packages:

    ```
    cd Files-To-S3
    pip install -r requirements.txt
    ```

3. **Modify config.yaml**:

    Edit the config.yaml file with your real AWS credentials. You'll need to provide the following information:

    ```
    AWS_SSO_PROFILE: 'sso-profile-name'
    AWS_REGION: 'us-east-1'
    AWS_S3_BUCKET_NAME: 's3-bucket-name'
    AWS_BUCKET_TARGET_FOLDER: 's3-folder-name'
    ```

4. **Install the Package**:

    Install the package using pip. This will make it available for use anywhere in your environment.

    ```
    pip install /path-to-Repo/Files-To-S3
    ```

5. **Export to PATH (Optional)**:

    To make the package available from any location, you can add the following line to your shell's startup file (e.g., ~/.bashrc, ~/.zshrc, or ~/.bash_profile for macOS and Linux):

    ```
    # For macOS and Linux
    export PATH=".:$PATH"
    ```

    This step is optional but can be helpful for easy command-line access to the package.

    **In Windows**, you can add the directory to your system's PATH environment variable as follows:

    1. Search for "Environment Variables".

    4. In the "Environment Variables" window, under the "User environment variables" (set for each user) or "System environment variables"(set for everyone). section, find and select the "Path" variable, and click the "Edit" button.

    5. In the "Edit Environment Variable" window, click the "New" button and add the path of the cloned repository to your directory. For example, if you want to add C:\Path\To\Your\Directory, add that path.

    6. Click "OK" to close each of the open windows.

    7. Restart your Command Prompt or PowerShell (if open) for the changes to take effect.

5. **Usage**

    Now that you have installed the package and configured your config.yaml file, you can use it to upload files to an S3 bucket. 
    You can use the `upload_to_s3` script to upload files from your local directory to an Amazon S3 bucket. Here are a few usage examples:

    - **Upload from the current local directory with the bucket name specified in `config.yaml`:**

        ```bash
        upload_to_s3
        ```

    - **Upload from the current directory to a specific S3 bucket folder name:**

        ```bash
        upload_to_s3 --bucket '/s3/bucket/directory'
        ```

    - **Upload from the current directory to a specific S3 bucket and folder name:**

        ```bash
        upload_to_s3 --bucket 'test_bucket' --s3-folder 'test_folder'
        ```

    - **Choose a local folder other than the current directory for file uploads:**

        ```bash
        upload_to_s3 --folder '/path-to-files-to-upload/'
        ```

    Make sure to edit the `config.yaml` file with your AWS credentials and configurations before running the script.

    Replace '/path-to-files-to-upload/' with the path to your local directory containing files to upload and /s3/bucket/directory with the S3 bucket directory where you want to upload the files.

    **NOTE**: If you've added the package to your PATH, you can run the command from any directory.