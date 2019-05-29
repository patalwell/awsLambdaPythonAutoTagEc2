# awsLambdaPythonAutoTagEc2

![Image](https://github.com/patalwell/ec2_autoTag_LambdaFunction/blob/master/AutoTagDiagram.png)

This repository contains a python client for AWS Lambda that can be used to monitor AWS resources and automatically tag
 AWS objects like EC2 instances or EBS volumes on creation. The function specifically identifies which User is creating 
 an EC2 instance or EBS Volume.
 
 Note: Based on my experience, I would <i>Highly</i> recommend organizations use this function to help monitor 
 development costs in AWS. e.g. Sometimes developers aren't mindful of their instances spend and this allows teams leaders
 to help educate their peers about cost savings best practices


###Requirements

1. The application logic requires `Python 2.7`.
2. You'll also have to verify that the Cloud Formation template properly creates and configures the 
services you'll need for the function. e.g. cloudWatch events via CloudTrail and permission for Lambda to monitor 
API calls via cloudTrail, write logs to Cloudwatch, and Tag Ec2 Instances
3. You can also copy and paste the python into the Lambda Function that is created as a result of the cloudformation template 
to prevent issues or manually configure the function yourself

###Usage
2. Clone this repository to a directory e.g. `git clone https://github.com/patalwell/awsLambdaPythonAutoTagEc2.git`
2. Log into AWS
3. Turn on Cloudtrail for the awsRegion in which you wish to enable autoTagging
4. Navigate to Cloudformation
5. Upload the EC2AutoTagCloudFormation template to the Cloudformation UI
6. Launch the Stack
8. Test the Lambda application with sample eventData from cloudWatch logs e.g. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference.html
9. Test autoTagging by creating an instance and making sure the appropriate
tags were deployed

## Note: The stack creates several AWS services in conjunction with Lambda. These include:
  1. A Policy and Role within IAM that allows Lambda to communicate with CloudTrail, CloudWatch, and EC2 related services and impersonate on a user's behalf
  2. A group within IAM so that users may only delete or stop resources tagged with their name, else admin has permissions
  3. A Cloudwatch trigger to listen for events from ec2.amazonaws.com that pertain to creation of an instance; e.g. RunInstances, CreateVolume, or CreateImage
  4. A lambda function with the ability to lookup Cloudtrail events, log event details, and automatically tag EC2 resources.
  5. Further details can be found here:https://aws.amazon.com/blogs/security/how-to-automatically-tag-amazon-ec2-resources-in-response-to-api-events/

  Special thanks to @Alessandro Martini
