import boto3
import time
import json
import subprocess
import os

def update_cloudformation_stack():
    print("\n=== Updating CloudFormation Stack ===")
    cloudformation = boto3.client('cloudformation', region_name='eu-west-1')
    
    try:
        # Read the template with correct path
        template_path = os.path.join(os.path.dirname(__file__), 'infrastructure/cfn-deployer/skill-stack.yaml')
        with open(template_path, 'r') as f:
            template_body = f.read()
        
        # Update the stack
        stack_name = 'ask-UKJobFinder-default-skillStack-1734364051331'
        try:
            response = cloudformation.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND'],
                Parameters=[
                    {
                        'ParameterKey': 'SkillId',
                        'UsePreviousValue': True
                    },
                    {
                        'ParameterKey': 'CodeBucket',
                        'UsePreviousValue': True
                    },
                    {
                        'ParameterKey': 'CodeKey',
                        'UsePreviousValue': True
                    },
                    {
                        'ParameterKey': 'CodeVersion',
                        'UsePreviousValue': True
                    },
                    {
                        'ParameterKey': 'LambdaHandler',
                        'UsePreviousValue': True
                    },
                    {
                        'ParameterKey': 'LambdaRuntime',
                        'UsePreviousValue': True
                    }
                ]
            )
            print("Stack update initiated...")
            
            # Wait for stack update to complete
            waiter = cloudformation.get_waiter('stack_update_complete')
            print("Waiting for stack update to complete...")
            waiter.wait(
                StackName=stack_name,
                WaiterConfig={'Delay': 5, 'MaxAttempts': 60}
            )
            print("Stack update completed successfully!")
            
        except cloudformation.exceptions.ClientError as e:
            if 'No updates are to be performed' in str(e):
                print("No stack updates needed")
            else:
                raise e
                
    except Exception as e:
        print(f"Error updating stack: {str(e)}")
        raise

def deploy_skill():
    print("\n=== Deploying Alexa Skill ===")
    try:
        # Change to the skill directory first
        os.chdir(os.path.dirname(__file__))
        # Deploy using ASK CLI
        subprocess.run(['ask', 'deploy'], check=True)
        print("Skill deployment completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error deploying skill: {str(e)}")
        raise

def main():
    try:
        # Update CloudFormation stack first
        update_cloudformation_stack()
        
        # Deploy the skill
        deploy_skill()
        
        print("\n=== Deployment Complete ===")
        print("Next steps:")
        print("1. Test the skill in the Alexa developer console")
        print("2. Verify the DynamoDB table has the new UserEmailIndex")
        print("3. Test saving a job through Alexa")
        print("4. View the saved job in the web interface")
        
    except Exception as e:
        print(f"\nDeployment failed: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
