from setuptools import setup, find_packages

setup(
    name='files-to-s3',
    version='1.0',
    packages=find_packages(),
    package_data={'': ['config.yaml']},
    entry_points={
        'console_scripts': ['upload_to_s3 = upload.upload_to_s3:main'],
    },
)
