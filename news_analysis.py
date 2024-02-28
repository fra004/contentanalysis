import poe
import logging
import sys
import time
import re
import kg_import
import openai
import certifi
certifi.where()

openai.api_key = "<your api key>"


def split_string_by_comma_and_slash(input_string):
    # Using re.split() with a regular expression to handle ',' and '/'
    result_using_re_split = re.split(r',|/', input_string)
    result_using_re_split = [s.strip() for s in result_using_re_split if s.strip()]
    
    return result_using_re_split

def split_string_by_comma_and_semicolon(input_string):
    # Using re.split() with a regular expression to handle ',' and ';'
    result_using_re_split = re.split(r',|;|\\n', input_string)
    result_using_re_split = [s.strip() for s in result_using_re_split if s.strip()]
    
    return result_using_re_split

def remove_single_characters(input_string):
    words = input_string.split()
    filtered_words = [word for word in words if len(word) > 1]
    result_string = ' '.join(filtered_words)
    return result_string

def remove_pattern_matches(input_string):
    pattern = r'\b[A-Za-z]+[0-9]+\b'  # Regular expression pattern for characters followed by numbers
    result_string = re.sub(pattern, '', input_string)
    return result_string

def remove_iptc_code(input_string):
    # Use regular expression to find all digits (\d) and replace them with an empty string
    result_string = re.sub(r'\d', '', input_string)
    result_string = re.sub(r'IPTC code:', '', result_string)
    result_string = re.sub(r'IPTC code', '', result_string)
    result_string = re.sub(r'IPTC:', '', result_string)
    result_string = re.sub(r'IPTC news code:', '', result_string)
    result_string = re.sub(r'IPTC news code', '', result_string)
    result_string = re.sub(r'IPTC news:', '', result_string)
    result_string = re.sub(r'IPTC', '', result_string)
    result_string = re.sub(r'\(', '', result_string)
    result_string = re.sub(r'\)', '', result_string)
    result_string = remove_pattern_matches(result_string)
    return remove_single_characters(result_string)

def parse_key_value_data(articleUrl, title, publicationDate, articleText, data_string, summary, authorStr):
    publisher = re.sub(r'https://www.', '', articleUrl)
    publisher = re.sub(r'/.*', '', publisher)
    print("PUBLISHER-NAME: " + publisher)
          
    a_id = [kg_import.createArticleInDB(articleUrl, title, [], publicationDate, publisher, summary, authorStr)]
    print(data_string)
    print("\n")
    # Split the data string by lines to separate key-value pairs
    lines = data_string.strip().split('\n')
    
    # Initialize an empty dictionary to store the parsed data
    parsed_data = {}
    
    # Process each line to extract key-value pairs
    counter = 0
    e_id = [0]
    et_id = [0]
    iptc_id = [0]

    for line in lines:
        line = line.strip()
        if len(line) == 0:
           continue
        if line.startswith("{") or line.startswith("}") or line.startswith("[") or line.startswith("]"):
           continue 
           
        # Split each line by the first occurrence of ':' to separate key and value
        if not line.startswith("-") and ':' in line: 
          key, value = line.split(':', 1)
          key = key.strip()  # Remove leading and trailing spaces from the key
          value = value.strip()  # Remove leading and trailing spaces from the value
          if counter == 0:
            print("Event name:" +value)
            e_id[0] = kg_import.createEventInDB(value, a_id[0])
            kg_import.createArticle_to_Event_relation(a_id, e_id)



          if counter == 1:
            eventType = remove_iptc_code(value)
            print("Event Type: "+ eventType)

            if len(eventType) > 0:
              eventTypes = split_string_by_comma_and_slash(eventType)
              for eventType in eventTypes:
                eventType = eventType.strip()
                et_id[0] = kg_import.createEventTypeInDB(eventType)
                kg_import.createEvent_to_EventType_relation(e_id, et_id)

                if len(eventType) > 0: 
                  iptc_id[0] = kg_import.createIPTC_MediaTopic_InDB(eventType)
                  kg_import.createEvent_to_IPTC_relation(e_id, iptc_id)

          if counter == 2:
            print("Involved Person: "+value)
            if len(value) > 0:
               names = split_string_by_comma_and_semicolon(value)
               for name in names:
                  p_name = name.strip()
                  if p_name == "[" or p_name == "]":
                    continue
                  p_id = [kg_import.createPersonInDB(p_name)]
                  kg_import.createEvent_to_Person_relation(e_id, p_id)
          if counter == 3:
            print("Location: "+value)
            if len(value) > 0:
               locs = split_string_by_comma_and_semicolon(value)
               for location in locs:
                  l_name = location.strip()
                  if l_name == "Unknown" or l_name == "[" or l_name == "]":
                    continue
                     
                  loc_id = [kg_import.createLocationInDB(l_name)]
                  kg_import.createEvent_to_Location_relation(e_id, loc_id)
          # Store the key-value pair in the dictionary
          parsed_data[key] = value
          counter = counter +1 
        else:
           if line.strip().startswith("-"):
              hypen, str = line.split('-', 1)
              line = str.strip()
           print(line)
           if counter == 4:
              if len(line) > 0:
                locs = split_string_by_comma_and_semicolon(line)
                for location in locs:
                  l_name = location.strip()
                  if l_name == "Unknown" or l_name == "[" or l_name == "]":
                    continue
                     
                  loc_id = [kg_import.createLocationInDB(l_name)]
                  kg_import.createEvent_to_Location_relation(e_id, loc_id)
           if counter == 3:
              if len(line) > 0:
                names = split_string_by_comma_and_semicolon(line)
                for name in names:
                  p_name = name.strip()
                  if p_name == "[" or p_name == "]":
                    continue
                  p_id = [kg_import.createPersonInDB(p_name)]
                  kg_import.createEvent_to_Person_relation(e_id, p_id)
            
    return a_id[0]


def parse_key_value_data_to_update_eventType(articleUrl, data_string):
    
    print(data_string)
    print("\n")
    # Split the data string by lines to separate key-value pairs
    lines = data_string.strip().split('\n')
    
    # Initialize an empty dictionary to store the parsed data
    parsed_data = {}
    
    # Process each line to extract key-value pairs
    counter = 0
    e_id = [0]
    et_id = [0]
    iptc_id = [0]
    e_id[0] = kg_import.findEventByArticleUrl(articleUrl)
    kg_import.deleteEvent_to_EventType_relation(e_id)
    kg_import.deleteEvent_to_IPTC_relation(e_id)
    
    for line in lines:
        line = line.strip()
        if len(line) == 0:
           continue
        if line.startswith("{") or line.startswith("}") or line.startswith("[") or line.startswith("]"):
           continue 
           
        # Split each line by the first occurrence of ':' to separate key and value
        if not line.startswith("-") and ':' in line: 
          key, value = line.split(':', 1)
          key = key.strip()  # Remove leading and trailing spaces from the key
          value = value.strip()  # Remove leading and trailing spaces from the value
          
          if counter == 1:
            eventType = remove_iptc_code(value)
            print("Event Type: "+ eventType)

            if len(eventType) > 0:
              eventTypes = split_string_by_comma_and_slash(eventType)
              for eventType in eventTypes:
                eventType = eventType.strip()
                iptc_id = [0]
                et_id[0] = kg_import.createEventTypeInDB(eventType)
                kg_import.createEvent_to_EventType_relation(e_id, et_id)
                iptc_id[0] = kg_import.createIPTC_MediaTopic_InDB(eventType)
                kg_import.createEvent_to_IPTC_relation(e_id, iptc_id)

          
          counter = counter +1 
        
       


def processArticleTextwithOpenAI(articleUrl, title, publicationDate, articleText, authorStr):
  #prompt = "If the following news is about any conflict, violence, human rights violation, disaster, write the name of the event, type of event, place, involved person, number of casualty in key-value format. Otherwise, simply say ‘No’ \n News: "

  openai.api_key = "<WRITE YOUR API KEY HERE>"

  model = "gpt-3.5-turbo"

  prompt = "Write the name of the event, type of the event, involved person and locations from the following news in key-value format. The keys must be 'Event name', 'Event type', 'Involved persons', 'Locations'. Use IPTC media topic name while writing values for 'Event type'. If there are more values for 'Involved persons' and 'Locations' write them as bullet points on different lines. Write full name while mentioning involved persons and locations. Write only name of persons if they are known. No need to include any unknown person.  Also do not need to write the designation or position of the persons.   \n News: " + articleText
  
  response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the appropriate model name
        messages=[
            {"role": "system", "content": "You are an assistant that is going to help me classifying news article texts and extracting useful information. "},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
  )
    
  response = response.choices[0].message['content'].strip()

  #print("*************")
  
  prompt = "Write a summary of the following news including the main event reported in the news. Do not write more than 150 words in the summary.  \n News: " + articleText
  summary =  openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the appropriate model name
        messages=[
            {"role": "system", "content": "You are an assistant that is going to help me summarizing news article texts. "},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
  )
  
  summary = summary.choices[0].message['content'].strip()
  

  return parse_key_value_data(articleUrl, title, publicationDate, articleText, response, summary, authorStr)
  

def processArticleText_to_update_IPTC_withOpenAI(articleUrl, articleText):
  #prompt = "If the following news is about any conflict, violence, human rights violation, disaster, write the name of the event, type of event, place, involved person, number of casualty in key-value format. Otherwise, simply say ‘No’ \n News: "

  openai.api_key = "<YOUR API KEY>"

  model = "gpt-3.5-turbo"

  prompt = "Write the name of the event, type of the event, involved person and locations from the following news in key-value format. The keys must be 'Event name', 'Event type', 'Involved persons', 'Locations'. Use IPTC media topic name while writing values for 'Event type'. If there are more values for 'Involved persons' and 'Locations' write them as bullet points on different lines. Write full name while mentioning involved persons and locations. Write only name of persons if they are known. No need to include any unknown person.  Also do not need to write the designation or position of the persons.   \n News: " + articleText
  
  response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the appropriate model name
        messages=[
            {"role": "system", "content": "You are an assistant that is going to help me classifying news article texts and extracting useful information. "},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
  )
    
  response = response.choices[0].message['content'].strip()


  return parse_key_value_data_to_update_eventType(articleUrl, response)
  


def processArticleTextAndGenerateSummarywithOpenAI(articleUrl, articleText):
  
  openai.api_key = "<YOUR API KEY >"

  model = "gpt-3.5-turbo"
  
  #print("*************")
  
  prompt = "Write a summary of the following news including the main event reported in the news. Do not write more than 150 words in the summary.  \n News: " + articleText
  summary =  openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the appropriate model name
        messages=[
            {"role": "system", "content": "You are an assistant that is going to help me summarizing news article texts. "},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
  )
  
  summary = summary.choices[0].message['content'].strip()
  

  return summary
  


  #time.sleep(5)