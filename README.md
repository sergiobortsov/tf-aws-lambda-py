## devops test project
This project contains python script for getting AWS EC2 EBS volumes info as well as Terraform code to AWS Lambda function to deploy that python script.

### How to use locally?
Python script requires to add AWS profile name and AWS region. To get the script help please run script with --help key. <br>
It's possible to filter EC2 instance by tag using standard regex, eg "*" or "server-*".
Script returns CSV table with EC2 instances list and their total size of EBS volume(s). Also, script shows the total size of all the available EBS attached EBS volumes in Gb.

### Terraform
Terraform configuration file (main.tf) is designed to deploy the locally available python function (script) in the "/python" folder plus panda Lambda layer.
