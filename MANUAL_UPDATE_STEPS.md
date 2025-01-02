# Manual Skill Update Steps

## 1. Update Skill Permissions in Alexa Developer Console

1. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Select the "UK Job Finder" skill
3. Click on "Tools" in the left sidebar
4. Select "Permissions"
5. Enable these permissions:
   - [x] Customer Email Address
   - [x] Customer Name
6. Click "Save Permissions"

## 2. Test the Skill

1. Go to the "Test" tab in the Alexa Developer Console
2. Enable testing in "Development" mode
3. Type or say:
   ```
   open uk job finder
   ```
4. Then:
   ```
   search for software developer jobs
   ```
5. After results appear:
   ```
   save job number one
   ```

## 3. Verify DynamoDB Entry

1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to DynamoDB
3. Open table: `ask-UKJobFinder-default-skillStack-1734364051331-saved-jobs`
4. Check that the new entry includes:
   - user_id (Alexa format)
   - user_email
   - job details

## 4. Test Web Application

1. Start the web application:
   ```bash
   cd uk-job-finder-web
   npm run dev
   ```
2. Open http://localhost:3000
3. Log in with your Amazon account
4. Verify that the job you saved through Alexa appears

## 5. Debug Information

If the job doesn't appear in the web interface:

1. Check the browser's developer console for API errors
2. In DynamoDB, verify:
   - The email in the saved job matches your Amazon account email
   - The UserEmailIndex is active
3. In the web application, check:
   - The session info shows your email
   - The debug panel shows the DynamoDB query details

## 6. Troubleshooting

If you encounter issues:

1. **Email Permission Error**
   - Double-check permissions are enabled in Alexa Developer Console
   - Try saving a new job through Alexa
   - Check Lambda CloudWatch logs for permission errors

2. **DynamoDB Issues**
   - Verify the UserEmailIndex is active
   - Check the email field is being stored correctly
   - Try querying the table directly in AWS Console

3. **Web Application Issues**
   - Verify the session contains your email
   - Check the API response in Network tab
   - Look for errors in browser console

## Need Help?

If you continue to experience issues:
1. Check CloudWatch logs for Lambda function errors
2. Verify DynamoDB table structure and indexes
3. Test the skill in the Alexa Developer Console
4. Review web application API responses

The infrastructure changes (CloudFormation stack, Lambda function, DynamoDB table) are already in place. This manual update just ensures the skill has the correct permissions to access the user's email.
