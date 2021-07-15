#!/usr/bin/env python3

from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import core
from aws_cdk import aws_sns as _sns
from aws_cdk import aws_sns_subscriptions as _snssub


class CdkStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        stack_prefix = id

        var_phone_number = core.CfnParameter(self, id='phoneNumber'.format(
            stack_prefix), no_echo=True, description="Phone number to send information. Example: +65123456")

        lambda_role = _iam.Role(
            self,
            id='{}-role-lambda'.format(stack_prefix),
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com'))

        cloudwatch_policy_statement = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW)
        cloudwatch_policy_statement.add_actions("logs:CreateLogGroup")
        cloudwatch_policy_statement.add_actions("logs:CreateLogStream")
        cloudwatch_policy_statement.add_actions("logs:PutLogEvents")
        cloudwatch_policy_statement.add_actions("logs:DescribeLogStreams")
        cloudwatch_policy_statement.add_resources("*")
        lambda_role.add_to_policy(cloudwatch_policy_statement)

        lambda_checkInventory = _lambda.Function(
            self,
            id='{}-lambda-checkInventory'.format(stack_prefix),
            function_name='{}-lambda-checkInventory'.format(stack_prefix),
            code=_lambda.AssetCode(
                "../lambda-functions/check-inventory/"),
            handler="app.handler",
            tracing=_lambda.Tracing.ACTIVE,
            timeout=core.Duration.seconds(30),
            role=lambda_role,
            runtime=_lambda.Runtime.PYTHON_3_8)

        lambda_checkPayment = _lambda.Function(
            self,
            id='{}-lambda-checkPayment'.format(stack_prefix),
            function_name='{}-lambda-checkPayment'.format(stack_prefix),
            code=_lambda.AssetCode("../lambda-functions/check-payment/"),
            handler="app.handler",
            tracing=_lambda.Tracing.ACTIVE,
            timeout=core.Duration.seconds(30),
            role=lambda_role,
            runtime=_lambda.Runtime.PYTHON_3_8)

        topic = _sns.Topic(self, id="{}-topic".format(stack_prefix), topic_name="{}-topic".format(stack_prefix),
                           display_name="Topic for {} demo".format(stack_prefix))
        topic.add_subscription(
            _snssub.SmsSubscription(phone_number=var_phone_number.value_as_string))

        core.CfnOutput(self, "{}-output-lambda-checkInventory".format(stack_prefix),
                       value=lambda_checkInventory.function_name, export_name="{}-output-lambda-checkInventory".format(stack_prefix))
        core.CfnOutput(self, "{}-output-lambda-checkPayment".format(stack_prefix),
                       value=lambda_checkPayment.function_name, export_name="{}-output-lambda-checkPayment".format(stack_prefix))
        core.CfnOutput(self, "{}-output-sns-topicName".format(stack_prefix),
                       value=topic.topic_name, export_name="{}-output-sns-topicName".format(stack_prefix))


stack_prefix = 'workflowStudio'
app = core.App()
stack = CdkStack(app, stack_prefix)
core.Tags.of(stack).add('Name', stack_prefix)

app.synth()
