from __future__ import print_function
import json
import boto3
import logging
import time
import datetime

'''
This function listens for a cloudWatch event that filters for AWS API calls via
CloudTrail. Moreover, it appends a series of reference vars and instance IDs to a python
dictionary in order to tag ec2 instances with a predefined set of key pair values.

Note: In order to attain the proper event level details you'll need to log the
event level metadata to the cloudwatch logs and capture the json for testing
purposes. e.g.logger.info('Event: ' + json.dumps(event, indent=2))

To check the event level from cloudWatch logs navigate to cloudWatch, Logs,
the appropriate log group, e.g./aws/lambda/EC2-AutoTag-EC2..., and the verison
of the lambda function you are testing
'''

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('Event: ' + json.dumps(event, indent=2))

    ids = []

    try:
        region = event['region']
        detail = event['detail']
        eventname = detail['eventName']
        arn = detail['userIdentity']['arn']
        principal = detail['userIdentity']['principalId']
        userType = detail['userIdentity']['type']
        user = detail['userIdentity']['userName']
        date = detail['eventTime']
        items = detail['responseElements']['instancesSet']['items'][0]['instanceId']

        if userType == 'IAMUser':
            user = detail['userIdentity']['userName']

        else:
            user = principal.split(':')[1]

        logger.info('principalId: ' + str(principal))
        logger.info('awsRegion: ' + str(region))
        logger.info('eventName: ' + str(eventname))
        logger.info('userName: ' + str(user))
        logger.info('items: ' + str(items))

        if not detail['responseElements']:
            logger.warning('No responseElements found')
            if detail['errorCode']:
                logger.error('errorCode: ' + detail['errorCode'])
            if detail['errorMessage']:
                logger.error('errorMessage: ' + detail['errorMessage'])
            return False

        ec2 = boto3.resource('ec2')

        if eventname == 'CreateVolume':
            ids.append(detail['responseElements']['volumeId'])
            logger.info(ids)
        elif eventname == 'RunInstances':
            items = detail['responseElements']['instancesSet']['items']
            for item in items:
                ids.append(item['instanceId'])
            logger.info(ids)
            logger.info('number of isntances: ' + str(len(ids)))

            base = ec2.instances.filter(InstanceIds=ids)

            # loop through the instances
            for instance in base:
                for vol in instance.volumes.all():
                    ids.append(vol.id)
                for eni in instance.network_interfaces:
                    ids.append(eni.id)

        elif eventname == 'CreateImage':
            ids.append(detail['responseElements']['imageId'])
            logger.info(ids)

        elif eventname == 'CreateSnapshot':
            ids.append(detail['responseElements']['snapshotId'])
            logger.info(ids)
        else:
            logger.warning('Not supported action')

        if ids:
            for resourceid in ids:
                print('Tagging resource ' + resourceid)
            ec2.create_tags(DryRun=False, Resources=[ids[0]],
                            Tags=[{'Key': 'Name', 'Value': ' '},
                                  {'Key': 'Service', 'Value': ' '},
                                  {'Key': 'Application', 'Value': ' '},
                                  {'Key': 'Team', 'Value': ''},
                                  {'Key': 'Owner', 'Value': user},
                                  {'Key': 'CreateDate', 'Value': date}])

        logger.info(' Remaining time (ms): ' + str(context.get_remaining_time_in_millis()) + '\n')
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False