#!/usr/bin/env python3

# Cleaned up: Removed temporary import testing and debugging prints

from aws_cdk import (
    Stack,
    aws_apprunner as apprunner,
    aws_ecr_assets as ecr_assets,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager
)
from constructs import Construct
import os

class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        image_asset = ecr_assets.DockerImageAsset(self, "Mem0McpServerImageAssetV3",
            directory=os.path.join(os.path.dirname(__file__), "..", "..") # Points to the project root
        )

        app_runner_ecr_access_role = iam.Role(
            self, "AppRunnerECRAccessRole",
            assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSAppRunnerServicePolicyForECRAccess")
            ]
        )
        
        image_asset.repository.grant_pull(iam.ServicePrincipal("build.apprunner.amazonaws.com"))

        mem0_api_key_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "Mem0ApiKeySecretLookup", 
            secret_name="mem0_MCP_API_KEY"
        )

        instance_config = apprunner.CfnService.InstanceConfigurationProperty(
            cpu="1 vCPU",
            memory="2 GB"
        )

        env_vars_list = [
            apprunner.CfnService.KeyValuePairProperty(
                name="MEM0_API_KEY",
                value=mem0_api_key_secret.secret_value_from_json("mem0_MCP_API_KEY").unsafe_unwrap()
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="MEM0_ORG_ID",
                value="org_6c7gYKa25e2wgGq9rexDAsWFEllT5p4YB49pcGKu"
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="MEM0_PROJECT_ID",
                value="proj_tuMFnQ6FBFYPsSKKq5gLe0uNHqrRRzakDoWmGS0a"
            )
        ]

        app_runner_service = apprunner.CfnService(
            self, "MyAppRunnerService",
            source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                image_repository=apprunner.CfnService.ImageRepositoryProperty(
                    image_identifier=image_asset.image_uri,
                    image_repository_type="ECR",
                    image_configuration=apprunner.CfnService.ImageConfigurationProperty(
                        port="8080", 
                        runtime_environment_variables=env_vars_list
                    )
                ),
                auto_deployments_enabled=True,
                authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                    access_role_arn=app_runner_ecr_access_role.role_arn
                )
            ),
            service_name="mem0-mcp-app-runner-service",
            instance_configuration=instance_config,
            health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
                protocol="TCP",
                healthy_threshold=2,
                unhealthy_threshold=5,
                interval=10,
                timeout=5
                # healthCheckGracePeriodSeconds parameter removed as it's not supported
            )
        )
