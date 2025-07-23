from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct

class LambdaDeploymentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ross_lake_bot = _lambda.Function(
            self, 
            'RossLakeLambda',
            code=_lambda.Code.from_asset_image('lambdas/ross_lake_bot'),
            handler=_lambda.Handler.FROM_IMAGE,
            runtime=_lambda.Runtime.FROM_IMAGE,
            memory_size=128,  
            timeout=Duration.seconds(120),
            description='Ross Lake monitoring bot',
        )

        half_hour_rule = events.Rule(
            self, 
            'RossLakeBotSchedule',
            schedule=events.Schedule.rate(Duration.minutes(30)), 
            description='Triggers Ross Lake Bot every 30 minutes'
        )

        half_hour_rule.add_target(targets.LambdaFunction(ross_lake_bot))

        CfnOutput(self, 
                  'RossLakeBot', 
                  value=ross_lake_bot.function_name,
                  description='Ross Lake Bot')
