import os
import re
import json
import operator
import datetime
from types import SimpleNamespace
from django.utils.text import slugify

import convo

class ConvoReader():

    inbox_path = "/messages/inbox/" # TODO: Handle filepath with and without extra '/'
    file_name_pattern = r"(message_\d{1}.json)"
    group_thread_type = "RegularGroup"
    text_msg_type = "Generic"
    timestamp_field_name = "timestamp_ms" # FIXME: extremely mixed handling of specifc Json field labels


    def __init__(self, root_path: str, output_path: str, user_name: str):
        self.file_path = root_path + self.inbox_path
        self.convos = dict()
        self.persons = dict()
        self.user = convo.User(user_name, root_path)

        # Identify all conversations in directory
        convo_list = os.listdir(self.file_path)

        # Extract each conversation
        for convo_path in convo_list:
            curr_convo = self.extract_convo(self.file_path + convo_path)
            self.user.convos[curr_convo.convo_name] = curr_convo

            file_output_path = root_path + "/" + output_path + "/"
            file_output_path += "/" + slugify(curr_convo.convo_name) + ".txt"

            print("Complete:", file_output_path)

            with open(file_output_path, "w", encoding="utf8") as file_obj:
                file_obj.write(str(curr_convo))

    def get_or_create_convo_side(self, curr_convo: Convo, person_name: str) -> ConvoSide:

        if not person_name in curr_convo.convo_sides:
            if person_name in self.persons:
                chosen_person = self.persons[person_name]
            else:
                chosen_person = Person(person_name)
                self.persons[person_name] = chosen_person
            
            curr_convo.participants[person_name] = chosen_person
            curr_convo.convo_sides[person_name] = convo.ConvoSide(chosen_person)

        return curr_convo.convo_sides[person_name]

    def setup_convo(self, file_path: str) -> Convo:

        # Load json as string
        with open(file_path, encoding = "utf8") as file_obj:
            raw_json_str = file_obj.read()

        # Convert JSON to dictionary
        raw_convo = json.loads(raw_json_str)

        # Get all participants from json object into list
        convo_persons = [x["name"] for x in raw_convo["participants"]]

        # Check participants for existing persons and create new persons where
        # necessary
        curr_participants = self.user.get_or_create_persons(convo_persons)

        # TODO: verify there are no other threadtypes
        is_group = raw_convo["thread_type"] == self.group_thread_type
        is_active = raw_convo["is_still_participant"]

        return convo.Convo(raw_convo["title"], curr_participants, is_active, is_group)


    def extract_json_files(self, json_list) -> list[str]:

        message_list = []

        # Extract all messages into single linked-list for sorting as
        # number/order is unknown
        for json_path in json_list:

            # Load json as string
            with open(json_path, encoding = "utf8") as file_obj:
                raw_json_str = file_obj.read()

            # Convert JSON to list of messages
            curr_json = json.loads(raw_json_str)["messages"]
            processed_messages = [SimpleNamespace(**x) for x in curr_json]

            message_list.extend(processed_messages)

        return message_list

    def get_start_time(self, messages) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(messages[0].timestamp_ms // 1000)

    
    def extract_convo(self, file_path) -> Convo:

        # Identify all json files corresponding to conversation
        json_list = os.listdir(file_path)
        json_list = [x for x in json_list if re.match(self.file_name_pattern, x)]

        # Add file path
        json_list = [file_path + "/" + x for x in json_list]

        curr_convo = self.setup_convo(json_list[0])

        # Get sorted list of messsages
        messages_list = self.extract_json_files(json_list)
        messages_list.sort(key=operator.attrgetter(self.timestamp_field_name))

        # Get first conversation side (unique combination of person and
        # conversation)
        first_sender = messages_list[0].sender_name
        curr_convo_side = self.get_or_create_convo_side(curr_convo, first_sender)
        curr_block_msg_count = 0
        curr_block_char_count = 0
        curr_block_start_time = get_start_time(messages_list)

        # Extract first person to send a message
        curr_convo.convo_starter = curr_convo_side.person

        for msg in messages_list:
            if msg.sender_name == curr_convo_side.get_name():
                curr_block_msg_count += 1
                if msg.type == self.text_msg_type and hasattr(msg, "content"):
                    curr_block_char_count += len(msg.content)

            else:
                # Update summary statistics
                curr_convo_side.msg_count += curr_block_msg_count
                curr_convo_side.char_count += curr_block_char_count
                curr_convo_side.add_block_msg_count(curr_block_msg_count, curr_block_start_time)

                # Reset counters TODO: create separate function for counter reset?
                curr_convo_side = self.get_or_create_convo_side(curr_convo, msg.sender_name)
                curr_block_msg_count = 1
                curr_block_char_count = 0
                curr_block_start_time = get_start_time(messages_list)

                if msg.type == self.text_msg_type and hasattr(msg, "content"):
                    curr_block_char_count = len(msg.content)

        del messages_list

        return curr_convo