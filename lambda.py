"""
Dungeon Beasts
"""

from __future__ import print_function
import random
import json
import urllib
import boto3
from boto3.dynamodb.conditions import Key, Attr

VERSION = 1.0

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Dungeon Beasts. " \
        "You can ask me to look up a beast from the D&D 5th edition Monster Manual by name. " \
        "For example, you can say tell me about Skeletons and I'll tell you what I know about them. " \
        "What would you like me to find for you?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "For instructions on what you can say, please say help me."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Dungeon Beasts. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def handle_session_stop_request():
    card_title = "Stop"
    speech_output = "Ok."
    should_end_session = true
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    #print("on_session_started requestId=" + session_started_request['requestId']
    #      + ", sessionId=" + session['sessionId'])
    print("on_session_started")


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    #print("on_launch requestId=" + launch_request['requestId'] +
    #      ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    print("Version: " + str(VERSION))
    print("intent_name:" + intent_name)

    # Dispatch to your skill's intent handlers
    if intent_name == "ListSourcesIntent":
        return list_sources(intent, session)
    elif intent_name == "BeastNameIntent":
        return beast_by_name(intent, session)
    elif intent_name == "MoreInfoIntent":
        return more_beast_info(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent":
        return handle_session_end_request()
    elif intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent " + intent_name)


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    #print("on_session_ended requestId=" + session_ended_request['requestId'] +
    #      ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    #print("event.session.application.applicationId=" +
    #      event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


# --------------- Functions for the core of Dungeon Beasts  -----------------

def get_dynamodb_conn():
    dynamodb = boto3.resource('dynamodb') #, endpoint_url='http://localhost:8000')
    return dynamodb

def list_sources(intent, session):
    card_title = "D&D Bestiary Sources"
    session_attributes = {}
    should_end_session = False
    source_list_arr = []
    speech_output = ""
    reprompt_text = ""

    try:
        dynamodb = get_dynamodb_conn()
        bestiary = dynamodb.Table('Bestiary_sources').scan()
        sources = bestiary['Items']
        for source in sources:
            source_list_arr.append(str(source['name']))

    except Exception as e:
        print("error list_sources: ", e)
        should_end_session = True
        reprompt_text = ""

    speech_output = ", ".join(sorted(source_list_arr))

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def beast_by_name(intent, session):
    card_title = "D&D Beast By Name"
    should_end_session = False
    beast_name = ""

    print("beast_by_name: ", intent['slots'])

    try:
        beast_info = ""
        session_attributes = ""
        single_beast = False
        beast_name = singularize((intent['slots']['beastName']['value']).title())

        print('Beast name: ', beast_name)

        if "beast_name" in session.get('attributes', {}):
            print('Session beast name: ', session['attributes']['beast_name'])
            if session['attributes']['beast_name'] == beast_name:
                single_beast = True
            speech_output, reprompt_text, session_attributes = find_beast_info(beast_name, single_beast)
        else:
            speech_output, reprompt_text, session_attributes = find_beast_info(beast_name)

    except Exception as e:
        print("error beast_by_name: ", e, "beast_name: " + beast_name)
        beast_info = "I couldn't find that beast."
        reprompt_text = ""
        speech_output = beast_name + ". " + beast_info
        should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def create_beast_name_attributes(beast_name):
    return {"beast_name": beast_name}

def find_beast_info(beast_name, single_beast=False):
    dynamodb = get_dynamodb_conn()
    bestiary = dynamodb.Table('Bestiary')
    bestiary_names = dynamodb.Table('Bestiary_names')
    speech_output = ""
    reprompt_text = ""
    session_attributes = ""

    if single_beast:
        #print("Looking for single beast true")
        speech_output, reprompt_text = find_single_beast(bestiary, beast_name)
    else:
        beast_group_items = find_groups(bestiary_names, beast_name)
        if len(beast_group_items) == 0:
            #print("Looking for single beast")
            speech_output, reprompt_text = find_single_beast(bestiary, beast_name)
        else:
            speech_output, reprompt_text = group_beasts_response(beast_group_items)

    session_attributes = create_beast_name_attributes(beast_name)
    return speech_output, reprompt_text, session_attributes


def find_groups(bestiary_names, beast_name):
    response = bestiary_names.scan(
        FilterExpression = Attr('group_name').begins_with(beast_name)
    )
    beast_group_items = response['Items']
    #print('Groups: ', beast_group_items)
    return beast_group_items

def find_single_beast(bestiary, beast_name):
    response = bestiary.get_item(
                Key={
                    'name': beast_name
                })
    #print(response)
    beast_data = response['Item']
    alignment = "Alignment: " + beast_data['alignment']
    ac = "AC: " + str(beast_data['ac'])
    hp = "HP: " + beast_data['hp']
    cr = "Challenge Rating: " + beast_data['cr']
    beast_info = ac + ". " + hp + ". " + cr + ". " + alignment
    print(beast_info)
    speech_output = beast_name + ". " + beast_info
    reprompt_text = "Say 'more' if you want more information about " + beast_name
    speech_output = speech_output + ". " + reprompt_text
    return speech_output, reprompt_text

def group_beasts_response(beast_group_items):
    beasts = beast_group_items[0]["beasts"]
    speech_output = "I found the following beasts: " + beasts
    reprompt_text = "Tell me which one you want by saying its name."
    return speech_output + ". " + reprompt_text, reprompt_text

def more_beast_info(intent, session):
    card_title = "D&D Beast More Info"
    should_end_session = True
    reprompt_text = ""
    session_attributes = {}

    if "beast_name" in session.get('attributes', {}):
        beast_name = session['attributes']['beast_name']
        #print('==============', beast_name)
        card_title = card_title + " For " + beast_name
        try:
            dynamodb = get_dynamodb_conn()
            bestiary = dynamodb.Table('Bestiary')
            beast_info = ""

            response = bestiary.get_item(
                Key={
                    'name': beast_name
                }
            )
            beast_data = response['Item']

            size        = "Size: " + beast_data['size'] + ". "
            beast_type  = "Type: " + beast_data['type'] + ". "
            speed       = "Speed: " + beast_data['speed'] + ". "
            beast_str   = "Strength: " + str(beast_data['str']) + ". "
            beast_dex   = "Dexterity: " + str(beast_data['dex']) + ". "
            beast_con   = "Constitution: " + str(beast_data['con']) + ". "
            beast_int   = "Intelligence: " + str(beast_data['int']) + ". "
            beast_wis   = "Wisdom: " + str(beast_data['wis']) + ". "
            beast_cha   = "Charisma: " + str(beast_data['cha']) + ". "
            skill       = "Skill: " + safe_str(beast_data['skill']) + ". "
            passive     = "Passive: " + safe_str(beast_data['passive']) + ". "
            resist      = "Resist: " + safe_str(beast_data['resist']) + ". "
            vulnerable  = "Vulnerable: " + safe_str(beast_data['vulnerable']) + ". "
            immune      = "Immune: " + safe_str(beast_data['immune']) + ". "
            senses      = "Senses: " + safe_str(beast_data['senses']) + ". "
            languages   = "Languages: " + safe_str(beast_data['languages']) + ". "
            traits      = "Traits: " + ", ".join(beast_data['traits']) + ". "
            actions     = "Actions: " + ", ".join(beast_data['actions']) + ". "
            legendaries = "Legendaries: " + get_legendaries(beast_data['legendaries']) + ". "
            source      = "Source: " + beast_data['source'] + ". "

            beast_info = size + beast_type + speed + beast_str + beast_dex + \
                         beast_con + beast_int + beast_wis + beast_cha + \
                         skill + passive + resist + vulnerable + immune + \
                         senses + languages + traits + actions + legendaries + \
                         source

            #print(response)
            print(beast_info)


        except Exception as e:
            print("error beast_by_name: ", e, "beast_name: " + beast_name)
            beast_info = " I couldn't find that beast."
            reprompt_text = ""
            should_end_session = True

        speech_output = beast_name + ". " + beast_info
    else:
        speech_output = "There was no beast to look up."


    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def safe_str(s):
    return 'None' if s is None else str(s)

def get_legendaries(legendaries):
    if len(legendaries) == 0:
        return "None"
    else:
        ", ".join(beast_data['legendaries'])


def singularize(name):
    new_name = name
    # starting with a brute force approach
    if name == "Apes":
        new_name = "Ape"
    if name == "Dragons":
        new_name = "Dragon"
    if name == "Orcs":
        new_name = "Orc"
    if name == "Skeletons":
        new_name = "Skeleton"
    if name == "Wolves":
        new_name = "Wolf"
    if name == "Vampires":
        new_name = "Vampire"
    return new_name
