from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    Tags,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct
import os

TAGS = {
    "Project": "RossLakeBot",
    "Environment": "Dev",
}

def create_lambda(scope, name, code_path, memory=128, timeout=120, env_vars=None):
    environment = {}
    if env_vars:
        environment = {k: os.getenv(k, '') for k in env_vars}
    
    lambda_fn = _lambda.Function(
        scope, f'{name}Function',
        code=_lambda.Code.from_asset_image(code_path),
        handler=_lambda.Handler.FROM_IMAGE,
        runtime=_lambda.Runtime.FROM_IMAGE,
        memory_size=memory,
        timeout=Duration.seconds(timeout),
        environment=environment
    )
    
    return lambda_fn

def minutely(minutes=30):
    return events.Schedule.rate(Duration.minutes(minutes))

def add_schedule(scope, name, lambda_fn, schedule=None, description=""):
    if schedule is None:
        schedule = events.Schedule.rate(Duration.hours(1)) 
    
    rule = events.Rule(
        scope, name,
        schedule=schedule,
        description=description
    )
    rule.add_target(targets.LambdaFunction(lambda_fn))
    return rule

class RossLakeDeploymentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        for key, value in TAGS.items():
            Tags.of(self).add(key, value)

        ross_lake_bot = create_lambda(self, 'RossLakeLambda', code_path='lambdas/ross_lake_bot', env_vars=['DISCORD_WEBHOOK_URL'])

        add_schedule(self, "RossLakeBotSchedule", ross_lake_bot, minutely(30), "Trigger Lambda every 30 minutes")

        CfnOutput(self, 
                  'RossLakeBot', 
                  value=ross_lake_bot.function_name,
                  description='Ross Lake Bot')
