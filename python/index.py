import boto3
import csv
import datetime
import logging
from os import environ
import collections
import time
import sys
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="List of arguments",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-p", "--profile", help="define aws profile in the ~/.aws/credentials file", required=True)
parser.add_argument("-n", "--name", help="EC2 instance Name(tag). Possible regex values: '*' for all available instances, 'server-*' - for partial name filtering", required=True)
args = parser.parse_args()
args = vars(parser.parse_args())
print(args)

profile=args["profile"]
temp_output_file='temp_output.csv'
output_file='output.csv'
clean_output_file='clean_output.csv'
result_file='result.csv'
volume_id_list=[]
result = []
regions = ['eu-west-2']
tag=args["name"]



def get_tag(each, tag_name):
    if 'Tags' in each:
        for tag in each['Tags']:
          if tag['Key'] == tag_name:
              return tag['Value']
    return ''

def get_vol(each, ec2):
    resultVol = {
        "vol_id": "",
        "vol_size": "",
        "vol_type": ""
    }
    resp = ec2.describe_volumes(
        Filters=[{'Name':'attachment.instance-id','Values':[each['InstanceId']]}]
    )
    for volume in (resp["Volumes"]):
        resultVol['vol_size'] += (str(volume["Size"]) + "\n")
        resultVol['vol_type'] += (str(volume["VolumeType"]) + "\n")

    return resultVol

def lambda_handler(event, context):
    try:
        logging.basicConfig(level=logging.INFO)
        logging.info('EC2 Inventory details')

        for region in regions:
            session = boto3.Session(profile_name=profile, region_name=region)
            ec2 = session.client('ec2')
            response = ec2.describe_instances(
                Filters=[
                    {
                        'Name': 'tag:Name',
                        'Values': [tag]
                    }
                ]
            )
            for item in response["Reservations"]:
                for each in item['Instances']:
                    volsss = get_vol(each, ec2)
                    result.append({
                        'instance-name': get_tag(each, 'Name'),
                        'instance-id': each.get('InstanceId', ''),
                        'instance-type': each.get('InstanceType', ''),
                        'status': each['State']['Name'],
                        'private-ip': each.get('PrivateIpAddress', ''),
                        'public-ip': each.get('PublicIpAddress', ''),             
                        'volume.size': volsss['vol_size']
                    })
                    
        header = ['instance-name', 'instance-id', 'instance-type', 'status', 'private-ip', 'public-ip', 'volume.size']
        with open(temp_output_file, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerows(result)

        df1 = pd.read_csv(temp_output_file)
        res1 = df1.set_index(['instance-name', 'instance-id', 'instance-type', 'status', 'private-ip', 'public-ip']).apply(lambda x: x.str.split('\n').explode()).reset_index()
        res1.to_csv(output_file)

        df2 = pd.read_csv(output_file)
        res2 = df2.dropna()
        res2.to_csv(clean_output_file)

        df3 = pd.read_csv(clean_output_file)
        df3.groupby(['instance-name', 'instance-id', 'instance-type', 'status', 'private-ip', 'public-ip'])['volume.size'].astype(int).sum().rename('total-size-ebs-volumes').to_csv(result_file)

        with open(result_file) as f:
            total = sum(float(r['total-size-ebs-volumes']) for r in csv.DictReader(f))
            print(int(total), 'Gb', sep='')

    except Exception as e:
        logging.error(
            'EC2 inventory with uncaught exception: {}'.format(e)
        )

if __name__ == '__main__':
    lambda_handler(None, None)