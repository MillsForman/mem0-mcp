from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_apprunner as apprunner,
    aws_ecr_assets as ecr_assets, # Import ECR assets module
    aws_iam as iam  # Import IAM module
)
from constructs import Construct
import os # Import os module for path manipulation

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Build and push Docker image from the root Dockerfile
        # The path to the Dockerfile is relative to the cdk.json file (i.e., cdk/ directory)
        # So, '../' goes up one level to the project root.
        image_asset = ecr_assets.DockerImageAsset(self, "Mem0McpServerImageAsset",
            directory=os.path.join(os.path.dirname(__file__), "..", "..") # Points to the project root
        )

        # Create an IAM role for App Runner to access ECR (this might be simplified if CDK handles it with assets)
        app_runner_ecr_access_role = iam.Role(
            self, "AppRunnerECRAccessRole",
            assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSAppRunnerServicePolicyForECRAccess")
            ]
        )
        
        # Grant the App Runner service principal pull access to the ECR asset repository
        # This is often handled automatically by CDK when using DockerImageAsset with AppRunner,
        # but explicitly granting can resolve potential permission issues.
        image_asset.repository.grant_pull(iam.ServicePrincipal("build.apprunner.amazonaws.com"))


        # Create the App Runner service from the ECR image asset
        app_runner_service = apprunner.CfnService(
            self, "MyAppRunnerService",
            source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                image_repository=apprunner.CfnService.ImageRepositoryProperty(
                    image_identifier=image_asset.image_uri,  # Use the URI from the image asset
                    image_repository_type="ECR",
                    image_configuration=apprunner.CfnService.ImageConfigurationProperty(
                        port="8080" # Assuming your app listens on port 8080
                    )
                ),
                auto_deployments_enabled=True, # Set to False if you want to manually trigger deployments
                authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                    access_role_arn=app_runner_ecr_access_role.role_arn # This role allows App Runner to pull from ECR
                )
            ),
            service_name="mem0-mcp-app-runner-service", # Choose a unique name
            instance_configuration=apprunner.CfnService.InstanceConfigurationProperty(
                cpu="1 vCPU",
                memory="2 GB"
            )
            # Add health check configuration if needed
            # health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
            #     protocol="TCP", # or "HTTP"
            #     port="8080"
            # )
        )
