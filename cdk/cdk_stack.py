   from aws_cdk import (
       core,
       aws_apprunner as apprunner,
       aws_ecr as ecr,
   )

   class MyAppRunnerStack(core.Stack):
       def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
           super().__init__(scope, id, **kwargs)

           # Define your ECR repository (if using a Docker image)
           repository = ecr.Repository.from_repository_name(self, "MyRepo", "mem0-mcp-server")

           # Create the App Runner service
           service = apprunner.CfnService(
               self, "MyAppRunnerService",
               source_configuration={
                   "image_repository": {
                       "image_identifier": f"{repository.repository_uri}:latest",
                       "image_repository_type": "ECR",
                   },
                   "auto_deployments_enabled": True,
               },
               service_name="mem0-mcp-service",
               instance_configuration={
                   "cpu": "1 vCPU",
                   "memory": "2 GB",
               },
           )