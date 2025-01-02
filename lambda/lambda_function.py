# C:\Users\stefan\Desktop\CODE\uk-job-finder\lambda\lambda_function.py

import os
import json
import boto3
import requests
from base64 import b64encode
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard, AskForPermissionsConsentCard
from ask_sdk_model.services import ServiceException
from ask_sdk_model.services.service_exception import ServiceException
from ask_sdk_core.exceptions import AskSdkException

# Required permissions
PERMISSIONS = [
    "alexa::profile:email:read",
    "alexa::profile:given_name:read"
]

# Initialize DynamoDB only if table name is provided
try:
    DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE')
    if DYNAMODB_TABLE:
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        table = dynamodb.Table(DYNAMODB_TABLE)
    else:
        print("Warning: DYNAMODB_TABLE environment variable not set")
except Exception as e:
    print(f"Error initializing DynamoDB: {str(e)}")

# Reed API configuration
REED_API_KEY = os.environ.get('REED_API_KEY')
if not REED_API_KEY:
    print("Warning: REED_API_KEY environment variable not set")
REED_API_BASE = 'https://www.reed.co.uk/api/1.0'

def sanitize_ssml(text):
    """Remove or replace characters that may cause SSML parsing issues."""
    if not text:
        return ""
    # Replace ampersand and remove angle brackets
    text = text.replace("&", " and ")
    text = text.replace("<", "")
    text = text.replace(">", "")
    return text.strip()

def get_user_profile(handler_input):
    """Get user's profile information including email"""
    try:
        print("Starting get_user_profile function")
        
        service_client_fact = handler_input.service_client_factory
        if not service_client_fact:
            print("No service client factory available")
            return None, None

        ups_service = service_client_fact.get_ups_service()
        if not ups_service:
            print("No UPS service available")
            return None, None

        email = None
        name = None

        try:
            print("Attempting to get user email...")
            email = ups_service.get_profile_email()
            print("Successfully retrieved user email")
        except ServiceException as e:
            print(f"ServiceException getting email: {str(e)}")
            if e.status_code == 403:
                print("Permission denied - need to request email permission")
                return "PERMISSION_REQUIRED", None
        except Exception as e:
            print(f"Unexpected error getting user email: {str(e)}")

        try:
            print("Attempting to get user name...")
            name = ups_service.get_profile_given_name()
            print("Successfully retrieved user name")
        except ServiceException as e:
            print(f"ServiceException getting name: {str(e)}")
        except Exception as e:
            print(f"Unexpected error getting user name: {str(e)}")

        return email, name
    except Exception as e:
        print(f"Error in get_user_profile: {str(e)}")
        return None, None

def request_permissions(handler_input, message):
    """Create a response requesting permissions"""
    print(f"Requesting permissions with message: {message}")
    speech = f"{message} To grant permission, please check your Alexa app."
    speech = sanitize_ssml(speech)
    
    permissions_card = AskForPermissionsConsentCard(permissions=PERMISSIONS)
    
    return handler_input.response_builder.speak(speech)\
        .set_card(permissions_card)\
        .set_should_end_session(False)\
        .response

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        print("Handling launch request")
        
        speech_text = "Welcome to UK Job Finder. You can search for jobs by saying something like 'find software engineer jobs in London' or ask me to list your saved jobs."
        
        try:
            # Try to personalize greeting if permissions are granted
            if handler_input.service_client_factory:
                email, name = get_user_profile(handler_input)
                
                if email == "PERMISSION_REQUIRED":
                    return request_permissions(
                        handler_input,
                        "Welcome to UK Job Finder. To provide a personalized experience, I need permission to access your name and email."
                    )
                
                if name:
                    speech_text = f"Welcome back {name}! " + speech_text
        except Exception as e:
            print(f"Error getting user profile in launch: {str(e)}")
        
        speech_text = sanitize_ssml(speech_text)
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Welcome", speech_text)).set_should_end_session(False)
        return handler_input.response_builder.response

class SearchJobIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SearchJobIntent")(handler_input)

    def handle(self, handler_input):
        if not REED_API_KEY:
            speech_text = "I'm sorry, but I'm not able to search for jobs right now. Please try again later."
            speech_text = sanitize_ssml(speech_text)
            handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("Error", speech_text)).set_should_end_session(False)
            return handler_input.response_builder.response
            
        slots = handler_input.request_envelope.request.intent.slots
        
        job_type = slots["jobType"].value if "jobType" in slots and slots["jobType"].value else None
        location = slots["location"].value if "location" in slots and slots["location"].value else None
        min_salary = slots["minSalary"].value if "minSalary" in slots and slots["minSalary"].value else None
        max_salary = slots["maxSalary"].value if "maxSalary" in slots and slots["maxSalary"].value else None
        distance = slots["distance"].value if "distance" in slots and slots["distance"].value else None
        contract_type = slots["jobContractType"].value if "jobContractType" in slots and slots["jobContractType"].value else None
        time_type = slots["jobTimeType"].value if "jobTimeType" in slots and slots["jobTimeType"].value else None
        
        # Normalize job type synonyms
        JOB_TYPE_SYNONYMS = {
            "dev": "developer",
            "programmer": "developer",
            "coder": "developer",
            "software developer": "software engineer",
            "nurse": "nurse",
            "doctor": "doctor",
            "teacher": "teacher",
            "accountant": "accountant",
            "electrician": "electrician",
            "mechanic": "mechanic",
            "chef": "chef",
            "architect": "architect",
            "marketing manager": "marketing manager",
            "project manager": "project manager",
            "data scientist": "data scientist",
            "data analyst": "data analyst",
            "graphic designer": "graphic designer",
            "web developer": "web developer",
            "cloud engineer": "cloud engineer"
        }

        if job_type and job_type.lower() in JOB_TYPE_SYNONYMS:
            job_type = JOB_TYPE_SYNONYMS[job_type.lower()]
        
        # Basic validation
        if not job_type and not location:
            speech_text = (
                "Please specify what kind of job you're looking for, "
                "or where you want to work. For example, say 'find software engineer jobs in London'."
            )
            speech_text = sanitize_ssml(speech_text)
            handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("Job Search", speech_text)).set_should_end_session(False)
            return handler_input.response_builder.response
        
        # Build search parameters
        params = {}
        if job_type:
            params['keywords'] = job_type
        
        if location:
            params['locationName'] = location
        
        if distance:
            try:
                distance_val = int(distance)
                if 1 <= distance_val <= 50:
                    params['distanceFromLocation'] = distance_val
                else:
                    params['distanceFromLocation'] = 20
            except ValueError:
                params['distanceFromLocation'] = 20
        else:
            params['distanceFromLocation'] = 20
        
        # Salary filters
        if min_salary:
            try:
                params['minimumSalary'] = int(min_salary)
            except ValueError:
                pass
        
        if max_salary:
            try:
                params['maximumSalary'] = int(max_salary)
            except ValueError:
                pass
        
        # Contract type
        if contract_type:
            ctype = contract_type.lower()
            if ctype in ["permanent"]:
                params['permanent'] = 'true'
            elif ctype in ["contract"]:
                params['contract'] = 'true'
            elif ctype in ["temp", "temporary"]:
                params['temp'] = 'true'

        # Time type
        if time_type:
            ttype = time_type.lower().replace(" ", "")
            if ttype in ["fulltime"]:
                params['fullTime'] = 'true'
            elif ttype in ["parttime"]:
                params['partTime'] = 'true'

        try:
            # Call Reed API
            session = requests.Session()
            session.auth = (REED_API_KEY, '')
            
            response = session.get(f'{REED_API_BASE}/search', params=params)
            response.raise_for_status()
            data = response.json()
            
            jobs = data.get('results', [])
            
            if not jobs:
                speech_text = (
                    "I couldn't find any jobs matching your criteria. "
                    "Try different search terms or adjust your filters."
                )
                card_text = speech_text
            else:
                top_jobs = jobs[:3]
                speech_text = "Here are the top matches: "
                
                # We'll build a more nicely formatted card text
                card_text = "Top Results:\n\n"
                
                for i, job in enumerate(top_jobs, 1):
                    job_title = sanitize_ssml(job.get('jobTitle', 'Unknown title'))
                    employer = sanitize_ssml(job.get('employerName', 'Unknown employer'))
                    location_name = sanitize_ssml(job.get('locationName', 'Unknown location'))
                    
                    if job.get('minimumSalary') and job.get('maximumSalary'):
                        salary_str = f"between {job['minimumSalary']} and {job['maximumSalary']} pounds"
                    elif job.get('minimumSalary'):
                        salary_str = f"{job['minimumSalary']} pounds"
                    else:
                        salary_str = "undisclosed"
                    
                    salary_str = sanitize_ssml(salary_str)
                    
                    speech_text += (
                        f"Number {i}: {job_title} at {employer} "
                        f"in {location_name} with a salary {salary_str}. "
                    )
                    
                    # Format card text for better readability
                    card_text += (
                        f"{i}. {job_title}\n"
                        f"   Employer: {employer}\n"
                        f"   Location: {location_name}\n"
                        f"   Salary: {salary_str}\n\n"
                    )
                
                speech_text += (
                    "Would you like to save any of these jobs? "
                    "Just say 'save job number' followed by the number."
                )
                
                card_text += (
                    "Would you like to save any of these jobs?\n"
                    "Say: \"Save job number 1\"\n\n"
                    "Other commands you can try:\n"
                    "- \"List my saved jobs\"\n"
                    "- \"Find permanent full-time nursing jobs in Manchester\"\n"
                    "- \"Find marketing manager jobs with a minimum salary of 30000\"\n"
                )
            
                # Store jobs in session attributes
                session_attr = handler_input.attributes_manager.session_attributes
                session_attr['current_jobs'] = top_jobs
                
        except Exception as e:
            speech_text = "I'm having trouble searching for jobs right now. Please try again later."
            card_text = speech_text
            print(f"Error searching jobs: {str(e)}")
        
        speech_text = sanitize_ssml(speech_text)
        card_text = sanitize_ssml(card_text)
        
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Job Search Results", card_text)).set_should_end_session(False)
        return handler_input.response_builder.response

class SaveJobIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SaveJobIntent")(handler_input)

    def handle(self, handler_input):
        if not DYNAMODB_TABLE:
            speech_text = "I'm sorry, but I'm not able to save jobs right now. Please try again later."
            speech_text = sanitize_ssml(speech_text)
            handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("Error", speech_text)).set_should_end_session(False)
            return handler_input.response_builder.response
            
        try:
            email, name = get_user_profile(handler_input)
            
            if email == "PERMISSION_REQUIRED":
                return request_permissions(
                    handler_input,
                    "To save jobs, I need permission to access your email address. This helps you view your saved jobs on the website."
                )
            
            if not email:
                return request_permissions(
                    handler_input,
                    "I need permission to access your email address to save jobs. Please grant permission in the Alexa app."
                )
            
            slots = handler_input.request_envelope.request.intent.slots
            job_number = int(slots["jobNumber"].value) if "jobNumber" in slots and slots["jobNumber"].value else None
            
            session_attr = handler_input.attributes_manager.session_attributes
            current_jobs = session_attr.get('current_jobs', [])
            
            if not current_jobs:
                speech_text = "Please search for jobs first before trying to save them."
            elif not job_number or job_number < 1 or job_number > len(current_jobs):
                speech_text = "Please specify a valid job number from the search results."
            else:
                try:
                    job = current_jobs[job_number - 1]
                    user_id = handler_input.request_envelope.context.system.user.user_id
                    
                    item = {
                        'user_id': user_id,
                        'job_id': str(job['jobId']),
                        'job_title': job['jobTitle'],
                        'employer': job['employerName'],
                        'location': job['locationName'],
                        'url': f"https://www.reed.co.uk/jobs/{job['jobId']}",
                        'user_email': email
                    }
                    
                    if name:
                        item['user_name'] = name
                        
                    table.put_item(Item=item)
                    
                    speech_text = f"I've saved the {job['jobTitle']} position at {job['employerName']} to your saved jobs."
                except Exception as e:
                    speech_text = "I had trouble saving that job. Please try again later."
                    print(f"Error saving job: {str(e)}")
        except Exception as e:
            speech_text = "I had trouble processing your request. Please try again."
            print(f"Error in SaveJobIntentHandler: {str(e)}")
        
        speech_text = sanitize_ssml(speech_text)
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Save Job", speech_text)).set_should_end_session(False)
        return handler_input.response_builder.response

class ListSavedJobsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ListSavedJobsIntent")(handler_input)

    def handle(self, handler_input):
        if not DYNAMODB_TABLE:
            speech_text = "I'm sorry, but I'm not able to list saved jobs right now. Please try again later."
            speech_text = sanitize_ssml(speech_text)
            handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("Error", speech_text)).set_should_end_session(False)
            return handler_input.response_builder.response
            
        try:
            email, name = get_user_profile(handler_input)
            if email == "PERMISSION_REQUIRED":
                return request_permissions(
                    handler_input,
                    "To list your saved jobs, I need permission to access your email address."
                )
            
            user_id = handler_input.request_envelope.context.system.user.user_id
            
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
            )
            
            if not response['Items']:
                speech_text = "You haven't saved any jobs yet. Try searching for jobs first!"
            else:
                speech_text = "Here are your saved jobs: "
                for job_item in response['Items']:
                    job_title = sanitize_ssml(job_item['job_title'])
                    employer = sanitize_ssml(job_item['employer'])
                    location = sanitize_ssml(job_item['location'])
                    speech_text += f"{job_title} at {employer} in {location}. "
                speech_text += "You can find the full details on Reed.co.uk."
                
        except Exception as e:
            speech_text = "I had trouble retrieving your saved jobs. Please try again later."
            print(f"Error listing saved jobs: {str(e)}")
        
        speech_text = sanitize_ssml(speech_text)
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Saved Jobs", speech_text)).set_should_end_session(False)
        return handler_input.response_builder.response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = (
            "You can search for jobs by saying 'find' followed by the type of job and location, "
            "like 'find software engineer jobs in London'. You can specify distance and salary, for example: "
            "'find permanent full-time nursing jobs in Manchester with a minimum salary of 30000 within 10 miles'. "
            "After searching, you can save jobs by saying 'save job number' followed by the number. "
            "You can also say 'list my saved jobs' to review your saved positions."
        )
        
        speech_text = sanitize_ssml(speech_text)
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Help", speech_text)).set_should_end_session(False)
        return handler_input.response_builder.response

class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speech_text = "Goodbye! Come back when you're ready to continue your job search."
        speech_text = sanitize_ssml(speech_text)
        
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Goodbye", speech_text)).set_should_end_session(True)
        return handler_input.response_builder.response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class AllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print(f"Error handled: {str(exception)}")
        speech_text = "Sorry, I had trouble processing that request. Please try again."
        speech_text = sanitize_ssml(speech_text)
        
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Error", speech_text)).set_should_end_session(False)
        return handler_input.response_builder.response

# Initialize the skill builder with the API client
sb = CustomSkillBuilder(api_client=DefaultApiClient())

# Register handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SearchJobIntentHandler())
sb.add_request_handler(SaveJobIntentHandler())
sb.add_request_handler(ListSavedJobsIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(AllExceptionHandler())

# Lambda handler
lambda_handler = sb.lambda_handler()
