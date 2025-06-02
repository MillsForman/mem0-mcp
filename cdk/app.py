#!/usr/bin/env python3
import os
# import sys # No longer needed

# print(f"sys.path: {sys.path}") # REMOVED

import aws_cdk as cdk

# Import CdkStack
from cdk.cdk_stack import CdkStack

# Define the qualifier
QUALIFIER = "mem0mcp"

app = cdk.App()

# Define the synthesizer with the qualifier
synthesizer = cdk.DefaultStackSynthesizer(
    qualifier=QUALIFIER
)

CdkStack(app, "CdkStackNew",
    synthesizer=synthesizer, # Pass the custom synthesizer
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    )

app.synth()
