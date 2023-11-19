provider "aws" {
  region = "eu-west-2"
  profile = "devops_test"
}

resource "aws_iam_role" "lambda_role" {
name   = "devops_test_lambda_python_role"
assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "lambda.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}

resource "aws_iam_policy" "iam_policy_for_lambda" {
 
 name         = "aws_iam_policy_for_devops_test_lambda_python_role"
 path         = "/"
 description  = "AWS IAM Policy for devops_test_lambda_python_role"
 policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": [
       "logs:CreateLogGroup",
       "logs:CreateLogStream",
       "logs:PutLogEvents",
       "ec2:DescribeInstances", 
       "ec2:DescribeImages",
       "ec2:DescribeTags",
       "ec2:DescribeVolumes"
     ],
     "Resource": "*",
     "Effect": "Allow"
   }
 ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "attach_iam_policy_to_iam_role" {
 role        = aws_iam_role.lambda_role.name
 policy_arn  = aws_iam_policy.iam_policy_for_lambda.arn
}

data "archive_file" "zip_the_python_code" {
type        = "zip"
source_dir  = "${path.module}/python/"
output_path = "${path.module}/python/labmda.zip"
}

resource "aws_lambda_function" "terraform_lambda_func" {
filename                       = "${path.module}/python/labmda.zip"
function_name                  = "devops_test_lambda_python"
role                           = aws_iam_role.lambda_role.arn
handler                        = "index.lambda_handler"
runtime                        = "python3.8"
source_code_hash               = data.archive_file.zip_the_python_code.output_base64sha256
layers                         = ["${aws_lambda_layer_version.python38-pandas-layer.arn}"]
depends_on                     = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role]
}

resource "aws_lambda_layer_version" "python38-pandas-layer" {
  filename            = "${path.module}/pandas.zip"
  layer_name          = "Python3-pandas"
  source_code_hash    = "${filebase64sha256("${path.module}/pandas.zip")}"
  compatible_runtimes = ["python3.8"]
}