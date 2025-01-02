# UK Job Finder Alexa Skill

An Alexa skill that helps users find and save UK jobs using the Reed.co.uk API.

## Prerequisites

1. Amazon Developer Account
2. AWS Account
3. Reed.co.uk API Key
4. ASK CLI (Alexa Skills Kit CLI)
5. AWS CLI
6. Python 3.9+

## Setup Instructions

### 1. Install Required Tools

```bash
# Install ASK CLI
npm install -g ask-cli

# Install AWS CLI
# Windows: Download and run the installer from AWS website
# Configure AWS CLI with your credentials
aws configure

# Initialize ASK CLI
ask configure
```

### 2. Get Reed.co.uk API Key

1. Go to [Reed.co.uk API Registration](https://www.reed.co.uk/developers/jobseeker)
2. Register for an account if you don't have one
3. Apply for API access
4. Once approved, copy your API key

### 3. Project Setup

```bash
# Clone the repository (if using version control)
# or create the directory structure as is

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Configuration

1. Update the skill manifest in `skill-package/skill.json`:
   - Replace placeholder URIs for icons
   - Add privacy policy and terms of use URLs if required

2. Update AWS Lambda function configuration:
   - In `infrastructure/cfn-deployer/skill-stack.yaml`, replace the empty REED_API_KEY with your actual API key:
     ```yaml
     Environment:
       Variables:
         REED_API_KEY: 'your-reed-api-key'
     ```

### 5. Deployment

```bash
# Deploy the skill
ask deploy

# Note: During first deployment, you'll need to:
# 1. Copy the Skill ID from the Alexa Developer Console
# 2. Update ask-resources.json with the Skill ID
# 3. Re-run ask deploy
```

## Usage

Once deployed, you can interact with the skill using commands like:

- "Alexa, open UK Job Finder"
- "Find software engineer jobs in London"
- "Save job number 1"
- "List my saved jobs"

## Features

- Search jobs by title and location
- Filter by salary range
- Save interesting jobs for later
- List saved jobs
- Voice-first interaction design

## Project Structure

```
uk-job-finder/
├── lambda/                      # Lambda function code
│   └── lambda_function.py
├── skill-package/
│   ├── interactionModels/      # Voice interaction model
│   │   └── custom/
│   │       └── en-GB.json
│   └── skill.json              # Skill manifest
├── infrastructure/
│   └── cfn-deployer/
│       └── skill-stack.yaml    # AWS CloudFormation template
├── requirements.txt            # Python dependencies
├── ask-resources.json          # ASK CLI configuration
└── README.md
```

## Development Notes

- The skill uses DynamoDB to store saved jobs
- Lambda function handles all the skill logic
- Reed.co.uk API is used for job searches
- Skill is limited to UK market only
- Uses ASK SDK v2 for Python

## Troubleshooting

1. If deployment fails:
   - Check AWS credentials are correctly configured
   - Verify Reed API key is correctly set
   - Ensure all required permissions are in place

2. If skill doesn't respond:
   - Check Lambda function logs in AWS CloudWatch
   - Verify skill invocation name matches
   - Test utterances match interaction model

3. If job search fails:
   - Verify Reed API key is valid
   - Check Reed API response in Lambda logs
   - Ensure network connectivity from Lambda

## Security Notes

- API keys are stored as environment variables
- DynamoDB table uses server-side encryption
- User data is handled according to Alexa's privacy requirements
- Lambda function uses minimal IAM permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
