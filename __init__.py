from boto3 import Session
from botocore.exceptions import ClientError
from flask import current_app

__version__ = '0.1'

class AwsSns(object):
    """
    Faciliate pub/sub with AWS SNS Service
    """

    def __init__(self, aws_access_key, aws_secret_key, aws_region):
        """
        Setup SNS Client
        :param aws_access_key: AWS Access Key
        :param aws_secret_key: AWS Secret Key
        :param aws_region: AWS Region
        """
        self.aws_creds = {
            aws_access_key: aws_access_key,
            aws_secret_key: aws_secret_key,
            aws_region: aws_region
        }
        self.sns = self.create_sns_client()

    def create_sns_client(self):
        """
        Creates a AWS SNS Client Object
        :return: AWS SNS Object
        """
        session = self.create_aws_session()
        sns = session.client('sns')
        return sns

    def create_aws_session(self):
        """
        Creates a AWS Session Object
        :return: AWS Session Object
        """
        try:
            session = Session(self.aws_creds)
	    return session
        except ClientError as e:
            raise AwsSnsError("Unable to create AWS session: {}".format(e.message))

    def publish_message(self, **kwargs):
        """
        Publish a message to a SNS Topic
        http://boto3.readthedocs.io/en/latest/reference/services/sns.html#SNS.Client.publish
        :param TopicArn: string semi-optional
        :param TargetArn: string semi-optional
        :param PhoneNumber: string semi-optional
        :param Message: string required
        :param Subject: string
        :param MessageStructure: string | if == json : Message == {"default": "foo", "somekey": "bar"}
        :param MessageAttributes: dict
        :return: MessageId || Error

        example:
          sns.publish_message(json.dumps({'default': 'foo', 'email': 'bar'}))
        """
        topic_arn = kwargs.get('TopicArn')
        target_arn = kwargs.get('TargetArn')
        phone_number = kwargs.get('PhoneNumber')

        # One of these is required
        if topic_arn or target_arn or phone_number:
            try:
                response = sns.publish(kwargs)
                if response.get('MessageId'):
                    return response.get('MessageId')
            except ClientError as e:
                raise AwsSnsError(e.message)
        else:
           raise AwsSnsError("TopicArn, TargetArn or PhoneNumber is required")

class AwsSnsError(Exception):
    """
    Handle AwsSns Class Errors
    """

    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return 'AwsSnsError: {}'.format(self.error)

    def __str__(self):
        return '{}'.format(self.error)

class RedisPs(object):
    """
    Todo: Implement
    """

    def __init__(self):
        pass
