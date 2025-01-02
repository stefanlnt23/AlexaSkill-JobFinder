# Deployment Instructions

## Prerequisites
- AWS CLI configured with appropriate credentials
- ASK CLI configured and logged in
- Python 3.9+ installed
- Node.js and npm installed

## Deployment Steps

1. **Update CloudFormation Stack and Deploy Skill**
   ```bash
   python deploy.py
   ```
   This will:
   - Update the CloudFormation stack with the new DynamoDB index
   - Deploy the updated Lambda function with email permissions
   - Update the skill manifest with email permissions

2. **Verify DynamoDB Table Updates**
   - Open AWS Console
   - Go to DynamoDB
   - Find the table: `ask-UKJobFinder-default-skillStack-1734364051331-saved-jobs`
   - Verify the `UserEmailIndex` is created and active
   - Check that the table has the `user_email` attribute defined

3. **Test the Alexa Skill**
   - Open the Alexa developer console
   - Go to the Test tab
   - Try the following commands:
     ```
     "Alexa, open UK Job Finder"
     "Alexa, ask UK Job Finder to search for software developer jobs"
     "Alexa, save job number one"
     ```
   - Check DynamoDB to verify the job is saved with your email

4. **Start the Web Application**
   ```bash
   cd uk-job-finder-web
   npm run dev
   ```
   - Open http://localhost:3000
   - Log in with your Amazon account
   - You should see your saved jobs

## Troubleshooting

### DynamoDB Issues
1. **Missing Email in Saved Jobs**
   - Check Lambda logs in CloudWatch
   - Verify the skill has email permissions in skill.json
   - Test saving a new job through Alexa

2. **UserEmailIndex Not Working**
   - Verify the index is active in DynamoDB
   - Check IAM permissions for the web app's AWS credentials
   - Look for errors in the web app's console

3. **Permission Errors**
   - Verify AWS credentials in .env.local
   - Check IAM user has correct DynamoDB permissions
   - Ensure the role has access to the UserEmailIndex

### Alexa Skill Issues
1. **Email Permission Errors**
   - Verify skill.json has email permission
   - Re-deploy the skill using ASK CLI
   - Check Lambda logs for permission errors

2. **Job Saving Errors**
   - Check Lambda logs in CloudWatch
   - Verify DynamoDB permissions
   - Test with debug logging enabled

### Web Application Issues
1. **Login Problems**
   - Check NextAuth configuration
   - Verify Amazon OAuth settings
   - Look for CORS or redirect issues

2. **Jobs Not Loading**
   - Check browser console for errors
   - Verify email is being passed correctly
   - Test DynamoDB queries directly

## Monitoring and Logs

1. **Lambda Logs**
   - CloudWatch Logs > Log Groups > /aws/lambda/ask-UKJobFinder-*
   - Look for email retrieval logs
   - Check DynamoDB operation logs

2. **Web App Logs**
   - Browser console for frontend errors
   - Server logs for API issues
   - DynamoDB operation logs

3. **DynamoDB Metrics**
   - Monitor index usage
   - Check read/write capacity
   - Look for throttling issues

## Rollback Procedure

If issues occur, you can rollback:

1. **CloudFormation Stack**
   ```bash
   aws cloudformation rollback-stack --stack-name ask-UKJobFinder-default-skillStack-1734364051331
   ```

2. **Skill Version**
   ```bash
   ask skill rollback --skill-id amzn1.ask.skill.your-skill-id
   ```

3. **Web Application**
   - Revert to previous .env.local
   - Restore previous API configuration

## Support

If you encounter any issues:
1. Check CloudWatch logs
2. Review DynamoDB streams
3. Test queries in AWS Console
4. Verify email permissions
5. Check OAuth configuration
