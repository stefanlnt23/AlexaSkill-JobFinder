# Manual Skill Update Instructions

1. **Update Skill Permissions**
   - Go to the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
   - Select the "UK Job Finder" skill
   - Click on "Tools" in the left sidebar
   - Select "Permissions"
   - Enable the following permissions:
     - [x] Customer Email Address
     - [x] Customer Name

2. **Test Email Permission**
   - Go to the "Test" tab in the Alexa Developer Console
   - Enable testing in "Development" mode
   - Try the following commands:
     ```
     "Alexa, open UK Job Finder"
     "Alexa, ask UK Job Finder to search for software developer jobs"
     "Alexa, save job number one"
     ```
   - Check the CloudWatch logs to verify the email is being retrieved

3. **Verify DynamoDB**
   - Go to the AWS Console
   - Navigate to DynamoDB
   - Open the table: `ask-UKJobFinder-default-skillStack-1734364051331-saved-jobs`
   - Check that new job entries include the `user_email` field

4. **Test Web Application**
   - Start the web application:
     ```bash
     cd uk-job-finder-web
     npm run dev
     ```
   - Open http://localhost:3000
   - Log in with your Amazon account
   - Verify that your saved jobs appear

5. **Troubleshooting**
   If jobs don't appear:
   - Check the browser console for API errors
   - Verify the email in the session matches the email in DynamoDB
   - Check CloudWatch logs for Lambda function errors
   - Verify the DynamoDB UserEmailIndex is active

The CloudFormation stack and Lambda function have already been updated to support email storage and querying. This manual update will complete the permission setup needed for email access.
