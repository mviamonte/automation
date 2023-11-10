import boto3
from botocore.exceptions import ClientError
from datetime import datetime,timedelta
#Library for local use
from pprint import pprint
#Defining the switch to execute one function or the other
#switch = "list_spot_volumes"
switch = "list_volumes_to_delete"
#Creating the client 
now = datetime.now()
retention_days = 14
ec2 = boto3.client('ec2')
print("Calling the main function")
result = ec2.describe_volumes(
    Filters = [
        {
            'Name' : 'status',
            'Values': ['available'],
        }
    ],
    #DryRun=True
)
#pprint(result)
def describe_volumes(volume_id):
        try:
            ec2resource = boto3.resource('ec2')
            volume = ec2resource.Volume(volume_id)
            print(volume.describe_status())
        except ClientError as e:
            print(f"Caught exception: {e}")
            
def main_function(switch,result):
    #Function to list volumes with tags (usually belongs to some spot creation)
    def list_tagged_volumes(result):
        try:
            #Iterate through the volumes from the describe_volumes method 
            for volume_id in result['Volumes']:
                if 'Tags' in volume_id.keys():
                    for name in volume_id['Tags']:
                        if 'Name' in name.values():
                            print(f"The volume {volume_id['VolumeId']} belongs to: {name['Value']}")
        except ClientError as e:
            print(f"Caught exception: {e}")
    def list_older_volumes(result):
        try:
            for volume in result['Volumes']:
                # print(f"The volume {volume['VolumeId']} was created on {volume['CreateTime']}")
                #Delete the tzinfo of each volume
                volume_time = volume['CreateTime'].replace(tzinfo=None)
                #Dates are already in the same format and compare
                if (now - volume_time) > timedelta(retention_days):
                    # print(f"Volume is older than configured retention of {retention_days} days")
                    # print(f"We should delete {volume['VolumeId']} this volume")
                    pprint(f"The volume {volume['VolumeId']} was created on {volume['CreateTime']}, proceding to delete")
                    describe_volumes(volume['VolumeId'])
                else:
                    print(f"Volume is newer than configured retention of {retention_days} days, so we keep it")
        except ClientError as e:
            print(f"Caught exception: {e}")

    print(f"Executing the step {switch}")
    if switch == "list_spot_volumes":
        list_tagged_volumes(result)
    elif switch == "list_volumes_to_delete":
        list_older_volumes(result)
main_function(switch,result)