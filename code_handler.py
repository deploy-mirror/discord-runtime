import secrets
import json
from role_handler import check_role
from message_handler import general_message


def code_verification(code_a_verifier):
    file = "codes.json"
    data = read_json(file)
    for code in data["codes"]:
        if code["key"] == code_a_verifier:
            if code["single"] == True:
                remove_code_by_code(code_a_verifier)
            return code
            
    return False


#message is the obj
#get the full command ($code add role 1)
async def add_code(message):
    split_role = message.content.split(" ", 2)
    if split_role[2].endswith(" 1"):
        single = True
        role = split_role[2].rsplit(" ", 1)[0].strip()
    else:
        role = split_role[2].strip()
        single = False

    if check_role(message.guild, role):
        code = secrets.token_hex(20)
    
        json_code = {
        "key" : code,
        "role" : role,
        "single" : single
        }
        #adding to json
        data = read_json("codes.json")
        data["codes"].append(json_code)
        save_json("codes.json", data)

        await general_message(message.channel, code)
    else:
        await general_message(message.channel, "role dosen't exist")
    

#only the code
def remove_code_by_code(code_to_remove):
    data = read_json("codes.json")
    data["codes"] = [code for code in data["codes"] if code["key"] != code_to_remove]
    save_json("codes.json", data)


#get the message obj
def remove_code_by_command(message):
    splited_message = message.content.split()
    data = read_json("codes.json")
    data["codes"] = [code for code in data["codes"] if code["key"] != splited_message[2]]
    save_json("codes.json", data)


def remove_all_codes():
    data = read_json("codes.json")
    data["codes"] = []
    save_json("codes.json", data)


#get the message obj
async def show_codes(message):
    data = read_json("codes.json")
    
    # Use a single string to collect all codes and send it in one message
    formatted_message = "```\n"  # Start the code block

    for code in data["codes"]:
        formatted_message += f"Code: {code['key']}\nRole: {code['role']}\nSingle-use: {code['single']}\n\n"

    formatted_message += "```"  # End the code block

    await general_message(message.channel, formatted_message)


def read_json(file):
    with open(file, "r") as full:
        data = json.load(full)
        return data

def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

