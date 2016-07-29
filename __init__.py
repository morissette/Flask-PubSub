from base64 import b64decode
from boto3 import Session
from botocore.exceptions import ClientError
from flask import current_app
from M2Crypto import X509
from re import compile as regex_compile, IGNORECASE
import requests

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
	subscription_handler = kwargs.get('SubscriptionHandler', self.subscription_handler)

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

    def subsciption_handler(self):
	"""
	Setup subscription route
	"""
	current_app.add_url_rule('/subscribe', view_func=self.subscription_endpoint)

    def subscription_endpoint(self, headers, data):
	"""
	Handle requests from SNS
	:param headers: request.headers
	:param data: request.get_json(force=True)
	:return: True
	"""
	if self.is_valid_message(data):
            message_type = headers.get('x-amz-sns-message-type:')
            if message_type == 'SubscriptionConfirmation':
                subscription_confirmation_url = data.get('SubscribeURL')
                response = requests.get(subscription_confirmation_url)
                if response.status_code == 200:
                    return True
		else:
		    raise AwsSnsError("Confirmation of subscription failed")
            elif message_type == 'Notification':
                message = data.get('Message')
                if message:
                    return message
                else:
		    raise AwsSnsError("No message received from notification")
        else:
	    raise AwsSnsError("SNS validation failed")

    def is_valid_message(self, msg):
	if msg[u'SignatureVersion'] != '1':
	    raise Exception('Wrong signature version')

        signing_url = msg[u'SigningCertURL']
        prog = regex_compile(r'^https://sns\.[-a-z0-9]+\.amazonaws\.com/.*$', IGNORECASE)
        if not prog.match(signing_url):
	    raise Exception("Cert is not hosted at AWS URL (https): %s", signing_url)

	r = requests.get(signing_url)
        cert = X509.load_cert_string(str(r.text))
        str_to_sign = None
        if msg[u'Type'] == 'Notification':
	    str_to_sign = build_notification_string(msg)
        elif any(msg[u'Type'] == s for s in ['SubscriptionConfirmation', 'UnsubscribeConfirmation']):
	    str_to_sign = build_subscription_string(msg)

        pubkey = cert.get_pubkey()
        pubkey.reset_context(md='sha1')
        pubkey.verify_init()
        pubkey.verify_update(str_to_sign.encode())
        result = pubkey.verify_final(b64decode(msg['Signature']))
        if result != 1:
	    raise Exception('Notification could not be confirmed')
        else:
	    return True

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
