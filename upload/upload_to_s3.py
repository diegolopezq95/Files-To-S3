import boto3
import os
import subprocess
import argparse
import yaml
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError
from dotenv import load_dotenv
load_dotenv()

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[96m'
RESET = '\033[0m'  # Reset the color


LINUX = '1'
MACOS = '2'
WINDOWS = '3'

SSO = '1'
ACCESS_KEY = '2'
ACCESS_SESSION_TOKEN = '3'


class S3Uploader:
    """Upload files to S3"""

    def __init__(self):
        """Initialize the S3Uploader class"""
        config = self.load_config("config.yaml")
        self.region = config.get("us-east-1")
        self.target_directory = config.get("AWS_BUCKET_TARGET_FOLDER")
        self.bucket_name = config.get("AWS_S3_BUCKET_NAME")
        self.sso_profile_name = config.get("AWS_SSO_PROFILE")
        self.access_key_id = config.get("AWS_ACCESS_KEY_ID")
        self.access_secret = config.get("AWS_SECRET_ACCESS_KEY")
        self.login_method = None
        self.os_choice = None

    @staticmethod
    def load_config(config_file: str) -> dict:
        """Load configuration file

        Args:
            config_file (str): Path to the configuration file

        Returns:
            dict: Configuration file
        """
        script_directory = os.path.dirname(os.path.abspath(__file__))
        # Construct the full path to the config.yaml file
        config_path = os.path.join(script_directory, config_file)
        with open(config_path, 'r') as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    def login_method_input(self) -> str:
        """Ask the user for their login preference

        Returns:
            choice (str): Login method
        """
        # Ask the user for their login preference
        print(BLUE + "Select your login method:" + RESET)
        print("1. AWS SSO")
        print("2. AWS access key")
        print("3. AWS session token")
        choice = input(
            BLUE + "Enter the number of your choice: " + RESET).strip()
        if choice == SSO:
            # Handle SSO login
            print(YELLOW + "Logging in with AWS SSO..." + RESET)
            return choice
        elif choice == ACCESS_KEY:
            # Handle Access Key login
            print(YELLOW + "Logging in with AWS access Key..." + RESET)
            return choice
        elif choice == ACCESS_SESSION_TOKEN:
            # Handle Access Key login
            print(YELLOW + "Logging in with AWS session token..." + RESET)
            return choice
        else:
            print(RED + "Invalid choice. Please enter 1 for AWS SSO, 2 for AWS access key or 3 for AWS session token" + RESET)
            exit(1)

    def mac_or_linux_or_windows(self) -> str:
        """Ask the user for their OS preference

        Returns:
            string (str): OS
        """
        # Ask the user for their login preference
        print(BLUE + "Select your OS:" + RESET)
        print("1. Linux")
        print("2. MacOS")
        print("3. Windows")
        choice = input(
            BLUE + "Enter the number of your choice: " + RESET).strip()
        valid_choices = [LINUX, MACOS, WINDOWS]
        if choice in valid_choices:
            return choice
        else:
            print(
                RED + "Invalid choice. Please enter 1 for Linux, 2 for MacOS, or 3 for Windows" + RESET)
            exit(1)

    def print_environment_instructions(self, os_choice) -> None:
        """Print instructions for setting environment variables

        Args:
            os_choice (str): OS
        """
        print(
            BLUE + "Please configure the following environment variables by executing the following command:" + RESET)
        if os_choice == LINUX or os_choice == MACOS:
            print(YELLOW + 'export AWS_ACCESS_KEY_ID="****"')
            print(YELLOW + 'export AWS_SECRET_ACCESS_KEY="****"')
            print(YELLOW + 'export AWS_SESSION_TOKEN="****"' + RESET)
        elif os_choice == WINDOWS:
            print(YELLOW + 'SET AWS_ACCESS_KEY_ID=****')
            print(YELLOW + 'SET AWS_ACCESS_KEY_ID=****')
            print(YELLOW + 'SET AWS_ACCESS_KEY_ID=****' + RESET)
            print(BLUE + "If using PowerShell execute this: " + RESET)
            print(YELLOW + '$Env:AWS_ACCESS_KEY_ID="****"')
            print(YELLOW + '$Env:AWS_SECRET_ACCESS_KEY="****"')
            print(YELLOW + '$Env:AWS_SESSION_TOKEN="****"' + RESET)

    def get_credentials(self, credentials) -> tuple:
        """Get AWS credentials

        Args:
            credentials (str): Path to the AWS credentials file

        Returns:
            tuple: AWS credentials
        """
        aws_credentials = {}
        with open(credentials, 'r') as file:
            for line in file:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=')
                    aws_credentials[key.strip()] = value.strip()
        access_key_id = aws_credentials.get('aws_access_key_id')
        secret_access_key = aws_credentials.get(
            'aws_secret_access_key')
        return access_key_id, secret_access_key

    def configure_aws_login(self) -> boto3.client:
        """Configure AWS SSO login

        Returns:
            client (boto3.client): AWS client
        """
        self.login_method = self.login_method_input()
        if self.login_method == SSO:
            aws_sso_cli_command = f"aws configure sso"
            aws_config_file = os.path.expanduser("~/.aws/config")
            try:
                if not os.path.isfile(aws_config_file):
                    print(
                        YELLOW + "AWS CLI configuration does not exist. Initiating AWS SSO configuration..." + RESET)
                    subprocess.run(aws_sso_cli_command, shell=True, check=True)
                    print(
                        GREEN + f"AWS SSO profile '{self.sso_profile_name}' configured successfully." + RESET)

                    # After SSO configuration, read the updated config file
                    with open(aws_config_file, "r") as config_file:
                        config_content = config_file.read()
                else:
                    # AWS CLI configuration already exists, read the existing config file
                    with open(aws_config_file, "r") as config_file:
                        config_content = config_file.read()
                if f"[profile {self.sso_profile_name}]" not in config_content:
                    # Execute the `aws configure sso` command from Python
                    try:
                        subprocess.run(aws_sso_cli_command,
                                       shell=True, check=True)
                        print(
                            GREEN + f"AWS SSO profile '{self.sso_profile_name}' configured successfully." + RESET)
                    except subprocess.CalledProcessError as e:
                        print(RED + f"Error configuring AWS SSO: {e}" + RESET)
                        exit(1)
                else:
                    print(
                        YELLOW + f"Profile '{self.sso_profile_name}' already exists in the AWS CLI config." + RESET)
                boto3.setup_default_session(profile_name=self.sso_profile_name)
                s3_client = boto3.client('s3')
                return s3_client
            except Exception as e:
                print(RED + f"Error configuring AWS SSO: {e}" + RESET)
                exit(1)
        elif self.login_method == ACCESS_KEY:
            try:
                # Open the credentials file and append the profile
                credentials_path = "~/.aws/credentials"
                aws_cli_command = f"aws configure"
                credentials = os.path.expanduser(credentials_path)
                if not os.path.isfile(credentials):
                    print(
                        YELLOW + "AWS CLI configuration does not exist. Initiating AWS access key configuration..." + RESET)
                    subprocess.run(aws_cli_command, shell=True, check=True)
                    print(
                        GREEN + f"AWS access key configured successfully." + RESET)
                access_key_id, secret_access_key = self.get_credentials(
                    credentials)
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key,
                )
                return s3_client
            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidAccessKeyId':
                    # Handle the InvalidAccessKeyId error here
                    print(
                        RED + "Error connecting to AWS: The AWS Access Key Id you provided is invalid." + RESET)
                    print(RESET)
                    print(
                        YELLOW + "Initiating new AWS access key configuration..." + RESET)
                    subprocess.run(aws_cli_command, shell=True, check=True)
                    print(
                        GREEN + f"AWS access key configured successfully." + RESET)
                    access_key_id, secret_access_key = self.get_credentials(
                        credentials)
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=access_key_id,
                        aws_secret_access_key=secret_access_key,
                    )
                    # _ = s3_client.list_buckets()
                    print(GREEN + "Connection successful." + RESET)
                    return s3_client
                else:
                    # Handle other AWS-related errors
                    print(RED + f"AWS error occurred: {e}" + RESET)
                    exit(1)
            except Exception as e:
                print(
                    RED + f"Error configuring AWS access key credentials: {e}" + RESET)
                exit(1)
        elif self.login_method == ACCESS_SESSION_TOKEN:
            try:
                self.os_choice = self.mac_or_linux_or_windows()
                aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
                aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
                aws_session_token = os.getenv("AWS_SESSION_TOKEN")
                if aws_access_key_id is None or aws_secret_access_key is None or aws_session_token is None:
                    self.print_environment_instructions(self.os_choice)
                else:
                    print(
                        GREEN + "Environment variables are set. You can proceed with your code." + RESET)
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=self.region,
                    aws_session_token=aws_session_token
                )
                return s3_client
            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidAccessKeyId':
                    print(RED + f"AWS error occurred: {e}" + RESET)
                    self.print_environment_instructions(self.os_choice)
                    print(
                        BLUE + "After configuring the environment variables, you can rerun the upload_to_s3 command." + RESET)
                else:
                    # Handle other AWS-related errors
                    print(RED + f"AWS error occurred: {e}" + RESET)
                    exit(1)
            except Exception as e:
                print(
                    RED + f"Error configuring AWS session token credentials: {e}" + RESET)
                exit(1)

    def input_arguments(self) -> argparse.Namespace:
        """Input arguments

        Returns:
            argparse.Namespace: Input arguments
        """
        parser = argparse.ArgumentParser(description="Upload files to S3.")
        parser.add_argument(
            "--bucket",
            help="Path to the S3 bucket."
        )
        parser.add_argument(
            "--s3-folder",
            help="Path to the S3 bucket folder."
        )
        parser.add_argument(
            "--folder",
            help="Path to the folder containing files to upload to S3."
        )
        args = parser.parse_args()
        return args

    def upload_file(self, client) -> None:
        """Upload files to S3

        Args:
            client (boto3.client): AWS client

        Returns:
            None
        """
        args = self.input_arguments()
        # Use the specified bucket or a default if none is provided
        bucket_name = args.bucket or self.bucket_name
        print(YELLOW + f"Using S3 bucket: S3://{bucket_name}" + RESET)
        # Use the specified bucket folder or a default if none is provided
        s3_folder = args.s3_folder or self.target_directory
        print(YELLOW + f"Using S3 bucket folder: {s3_folder}" + RESET)
        # Use the specified folder or a default if none is provided
        local_folder_path = args.folder or "."
        print(YELLOW + f"Using local folder: {local_folder_path}" + RESET)
        # Check if the local directory exists
        local_folder_path = os.path.abspath(local_folder_path)

        if not os.path.exists(local_folder_path):
            print(
                RED + f"The local folder does not exist: {local_folder_path}" + RESET)
            exit(1)
        # List files in the local directory
        files_to_upload = []
        for root, dirs, files in os.walk(local_folder_path):
            for file in files:
                local_file_path = os.path.join(root, file)
                s3_object_key = os.path.join(
                    s3_folder, os.path.relpath(local_file_path, local_folder_path))
                files_to_upload.append((local_file_path, s3_object_key))

        if files_to_upload == []:
            print(
                RED + f"No files found in the local folder: {local_folder_path}" + RESET)
            exit(1)

        # Prompt the user for confirmation
        print(YELLOW + f'Files to upload to S3: ' + RESET)
        for local_file_path, s3_object_key in files_to_upload:
            print(YELLOW + '- Local: ' + RESET + f'{local_file_path}' + RESET)
            print(YELLOW + '- S3: ' + RESET +
                  f's3://{bucket_name}/{s3_object_key}' + RESET)

        confirmation = input(BLUE + 'Do you want to push these files to S3? (' +
                             RESET + GREEN + 'Yes' + RESET + '/' + RED + 'No' + RESET + '): ')

        if confirmation == 'Yes':
            try:
                for local_file_path, s3_object_key in files_to_upload:
                    # Upload the file to S3
                    client.upload_file(
                        local_file_path, bucket_name, s3_object_key)
                print(GREEN + 'Files uploaded to S3 successfully!' + RESET)
            except (ClientError, S3UploadFailedError) as e:
                if self.login_method == SSO:
                    if 'InvalidAccessKeyId' in str(e):
                        aws_sso_cli_command = f"aws configure sso"
                        print(
                            YELLOW + "AWS CLI configuration does not exist. Initiating AWS SSO configuration..." + RESET)
                        subprocess.run(aws_sso_cli_command,
                                       shell=True, check=True)
                        print(
                            GREEN + f"AWS SSO profile '{self.sso_profile_name}' configured successfully." + RESET)
                        print(
                            BLUE + "You can rerun the upload_to_s3 command." + RESET)
                    else:
                        # Handle other AWS-related errors
                        print(RED + f"AWS error occurred: {e}" + RESET)
                        exit(1)
                elif self.login_method == ACCESS_KEY:
                    if 'InvalidAccessKeyId' in str(e):
                        aws_cli_command = f"aws configure"
                        # Handle the InvalidAccessKeyId error here
                        print(
                            RED + "Error connecting to AWS: The AWS Access Key Id you provided is invalid." + RESET)
                        print(RESET)
                        print(
                            YELLOW + "Initiating new AWS access key configuration..." + RESET)
                        subprocess.run(aws_cli_command, shell=True, check=True)
                        print(
                            GREEN + f"AWS access key configured successfully." + RESET)
                        print(
                            BLUE + "You can rerun the upload_to_s3 command." + RESET)
                    else:
                        # Handle other AWS-related errors
                        print(RED + f"AWS error occurred: {e}" + RESET)
                        exit(1)
                elif self.login_method == ACCESS_SESSION_TOKEN:
                    if 'InvalidAccessKeyId' in str(e) or 'InvalidToken' in str(e):
                        print(RED + f"AWS error occurred: {e}" + RESET)
                        self.print_environment_instructions(self.os_choice)
                        print(
                            BLUE + "After configuring the environment variables, you can rerun the upload_to_s3 command." + RESET)
                    else:
                        print(RED + f"AWS error occurred: {e}" + RESET)
                        exit(1)
                else:
                    print(RED + f"Error uploading files to S3: {e}" + RESET)
                    exit(1)
            except Exception as e:
                print(RED + f"Error uploading files to S3: {e}" + RESET)
                exit(1)
        else:
            print(YELLOW + 'Upload canceled. No files were pushed to S3.' + RESET)


def main():
    S3 = S3Uploader()
    client = S3.configure_aws_login()
    S3.upload_file(client)


if __name__ == "__main__":
    main()
