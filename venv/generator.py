import json
import random
import argparse
import datetime
import configparser
import cProfile
import pstats

parser = argparse.ArgumentParser()
parser.parse_args()

config = configparser.ConfigParser()
config.read("generator.ini")

# Get all of the values from the INI file. Stored in short names in this code
user_count = config.getint("DEFAULT","User Count")
starting_phone_mac = config.get("DEFAULT","Starting Phone MAC")
email_domain = config.get("DEFAULT","Email Domain")
device_pool_count = config.getint("DEFAULT","Number of Device Pools")
workspace_frequency = config.getint("DEFAULT","Percentage of Users as Workspaces")
disable_phone = config.getboolean("DEFAULT",'Disable Phones', fallback=False)
phone_frequency = config.getint("DEFAULT","Percentage of User with Phones", fallback=90)
disable_csf = config.getboolean("DEFAULT","Disable CSF", fallback=False)
csf_frequency = config.getint("DEFAULT","Percentage of users with CSF", fallback=50)
disable_bot = config.getboolean("DEFAULT","Disable BOT", fallback=False)
bot_frequency = config.getint("DEFAULT","Percentage of users with BOT", fallback=50)
disable_tct = config.getboolean("DEFAULT","Disable TCT", fallback=False)
tct_frequency = config.getint("DEFAULT","Percentage of users with TCT", fallback=50)
disable_tab = config.getboolean("DEFAULT","Disable TAB", fallback=False)
tab_frequency = config.getint("DEFAULT","Percentage of users with TAB", fallback=50)
disable_random_owner = config.getboolean("DEFAULT","Disable Random Owner", fallback=False)
random_owner_frequency = config.getint("DEFAULT","Percentage of Random Owners", fallback=50)
disable_random_user_id = config.getboolean("DEFAULT","Disable Random User ID", fallback=False)
random_user_frequency = config.getint("DEFAULT","Percentage of Random User IDs", fallback=50)
disable_random_blank_emask = config.getboolean("DEFAULT","Disable Random Blank EMASK", fallback=False)
random_blank_emask_frequency = config.getint("DEFAULT","Percentage of Random Blank EMASK", fallback=50)
disable_random_emask = config.getboolean("DEFAULT","Disable Random EMASK", fallback=False)
random_emask_frequency = config.getint("DEFAULT","Percentage of Random EMASK", fallback=50)
disable_random_blank_email_id = config.getboolean("DEFAULT","Disable Random Blank Email", fallback=False)
random_blank_email_frequency = config.getint("DEFAULT","Percentage of Random Blank Email", fallback=50)
disable_random_sccp_phones = config.getboolean("DEFAULT","Disable Random SCCP Phones", fallback=False)
random_sccp_phones_frequency = config.getint("DEFAULT","Percentage of Random SCCP Phones", fallback=50)
disable_random_device_primary_extension_1 = config.getboolean("DEFAULT","Disable Device Random Primary Extension 1", fallback=False)
random_device_primary_extension_1_frequency = config.getint("DEFAULT","Percentage of Device Random Primary Extension 1", fallback=50)
disable_random_extension_length = config.getboolean("DEFAULT","Disable Random Extension Length", fallback=False)
random_extension_length_frequency = config.getint("DEFAULT","Percentage of Random Extension Length", fallback=50)

# Open all of the JSON lkibraries and store them for later
with open("workspace_names.json", "r") as fh:
    workspace_names = json.load(fh)
with open("device_pools.json", "r") as fh:
    device_pools = json.load(fh)
with open('first_names.json', 'r') as fh:
    first_names = json.load(fh)
with open('last_names.json', 'r') as fh:
    last_names = json.load(fh)
with open("phone_fields.json") as fh:
    phone_fields = json.load(fh)
with open("user_template.json") as fh:
    user_template = json.load(fh)
with open("8865.json", "r") as fh:
    phone_template = json.load(fh)
with open("CSF.json", "r") as fh:
    csf_template = json.load(fh)
with open("BOT.json", "r") as fh:
    bot_template = json.load(fh)
with open("TAB.json", "r") as fh:
    tab_template = json.load(fh)
with open("TCT.json", "r") as fh:
    tct_template = json.load(fh)

# Write the header lines to the phones.csv and users.csv files
phonefile = open("phones.csv" , "w")
phonefile.write(",".join(phone_fields))
phonefile.write("\n")

userfile = open("users.csv", "w")
userfile.write(",".join(list(user_template.keys())))
userfile.write("\n")

generated = {}      # A dictionary to hold stats of generated data

# The next two lines are for debugging and performance analytics
profile = cProfile.Profile()
profile.enable()

# Now start looping through and creating, using user_count as the loop range
for x in range(user_count):
    this_user = {}      # Dict to hold all of the created data
    if random.choices([0,1], weights=(100-workspace_frequency,workspace_frequency))[0] == 1:    # Randomly decide if this is a workspace
        # Assign a Device Pool, DN and Partition
        index = random.randrange(0, device_pool_count)
        this_user['device_pool'] = device_pools[index]['name']
        this_user['partition'] = device_pools[index]['pt1']
        this_user['external_phone_number_mask'] = device_pools[index]['emask']
        if not "dn1_current" in device_pools[index]:
            device_pools[index]['dn1_current'] = device_pools[index]['dn1_start']
        this_user['dn1'] = device_pools[index]['dn1_current']
        device_pools[index]['dn1_current'] += 1

        # Create a workspace-specific name, and blank values for the ones a workspace doesn't need
        this_user["first_name"] = this_user['dn1']
        this_user["last_name"] = random.choice(workspace_names)
        this_user["full_name"] = str(this_user['first_name']) + " " + this_user['last_name']
        this_user["user_name"] = ""
        this_user["user_id_1"] = ""
        this_user["user_id_2"] = ""
        this_user["owner_user_id"] = ""

        this_user['has_phone'] = True   # All workspaces have phones
        # Assign a MAC ID for the phone
        this_user['phone_mac'] = str(starting_phone_mac)[-12:]
        this_user['device_name'] = "SEP" + this_user['phone_mac']
        this_user['ext_descr'] = str(this_user['dn1']) + " in " + this_user['partition']
        # And increment so we are ready for the next one
        tmp = int(str(starting_phone_mac), base=16)
        tmp += 1
        starting_phone_mac = hex(tmp)

        # Workspaces don't have soft clients
        this_user['has_csf'] = False
        this_user['has_tab'] = False
        this_user['has_tct'] = False
        this_user['has_bot'] = False
    else:   # This is a person
        # Let's give them a name
        this_user['first_name'] = random.choice(first_names)
        this_user['last_name'] = random.choice(last_names)
        this_user['full_name'] = this_user['first_name'] + " " + this_user['last_name']

        # Build the username
        this_user['user_name'] = this_user['first_name'][0:2] + this_user['last_name'] + str(random.randrange(1,99))

        # Assign a Device Pool, DN and Partition
        index = random.randrange(0, device_pool_count)
        this_user['device_pool'] = device_pools[index]['name']
        this_user['partition'] = device_pools[index]['pt1']
        this_user['external_phone_number_mask'] = device_pools[index]['emask']
        if not "dn1_current" in device_pools[index]:
            device_pools[index]['dn1_current'] = device_pools[index]['dn1_start']
        this_user['dn1'] = device_pools[index]['dn1_current']
        device_pools[index]['dn1_current'] += 1

        # Assign email
        this_user['email'] = this_user['user_name'] + email_domain

        this_user['ext_descr'] = str(this_user['dn1']) + " in " + this_user['partition']

        # Random Owner ID
        if (random.choices([0,1], weights=(100-random_owner_frequency,random_owner_frequency))[0] == 1) and not (disable_random_owner):
            this_user['owner_user_id'] = this_user['user_name']
        else:
            this_user['owner_user_id'] = ""
        # Random User
        if (random.choices([0,1], weights=(100-random_user_frequency,random_user_frequency))[0] == 1) and not (disable_random_user_id):
            this_user['user_id_1'] = this_user['user_name']
            this_user['user_id_2'] = ""
        else:
            this_user['user_id_1'] = ""
            this_user['user_id_2'] = ""

        if (random.choices([0,1], weights=(100-phone_frequency,phone_frequency))[0] == 1) and not (disable_phone):
            this_user['has_phone'] = True
            # Assign a MAC ID for the phone
            this_user['phone_mac'] = str(starting_phone_mac)[-12:]
            this_user['device_name'] = "SEP" + this_user['phone_mac']
            # And increment so we are ready for the next one
            tmp = int(str(starting_phone_mac), base=16)
            tmp += 1
            starting_phone_mac = hex(tmp)
        else:
            this_user['has_phone'] = False
        if (random.choices([0,1], weights=(100-csf_frequency, csf_frequency))[0] == 1) and not (disable_csf):
            this_user['jabber_csf'] = "CSF" + this_user['user_name']
            this_user['jabber_owner_id'] = this_user['user_name']
            this_user['has_csf'] = True
        else:
            this_user['has_csf'] = False
        if (random.choices([0,1], weights=(100-bot_frequency, bot_frequency))[0] == 1) and not (disable_bot):
            this_user['jabber_bot'] = "BOT" + this_user['user_name']
            this_user['jabber_owner_id'] = this_user['user_name']
            this_user['has_bot'] = True
        else:
            this_user['has_bot'] = False
        if (random.choices([0,1], weights=(100-tct_frequency, tct_frequency))[0] == 1) and not (disable_tct):
            this_user['jabber_tct'] = "TCT" + this_user['user_name']
            this_user['jabber_owner_id'] = this_user['user_name']
            this_user['has_tct'] = True
        else:
            this_user['has_tct'] = False
        if (random.choices([0,1], weights=(100-tab_frequency, tab_frequency))[0] == 1) and not (disable_tab):
            this_user['jabber_tab'] = "TAB" + this_user['user_name']
            this_user['jabber_owner_id'] = this_user['user_name']
            this_user['has_tab'] = True
        else:
            this_user['has_tab'] = False

    if this_user['has_phone']:

        writeline = []
        for key in phone_template:
            if len(phone_template[key]) > 0:
                if phone_template[key][0] == "{":
                    mykey = phone_template[key]
                    mykey = mykey.replace("{", "")
                    mykey = mykey.replace("}", "")
                    mykey = mykey.replace(" ", "_")
                    writeline.append(this_user[mykey])
                else:
                    if "," in phone_template[key]:
                        writeline.append(f"\"{phone_template[key]}\"")
                    else:
                        writeline.append(phone_template[key])
            else:
                writeline.append(phone_template[key])
        phonefile.write(",".join(str(v) for v in writeline))
        phonefile.write("\n")

    if this_user['has_csf']:
        writeline = []
        for key in csf_template:
            if len(csf_template[key]) > 0:
                if csf_template[key][0] == "{":
                    mykey = csf_template[key]
                    mykey = mykey.replace("{", "")
                    mykey = mykey.replace("}", "")
                    mykey = mykey.replace(" ", "_")
                    writeline.append(this_user[mykey])
                else:
                    if "," in csf_template[key]:
                        writeline.append(f"\"{csf_template[key]}\"")
                    else:
                        writeline.append(csf_template[key])
            else:
                writeline.append(csf_template[key])
        phonefile.write(",".join(str(v) for v in writeline))
        phonefile.write("\n")

    if this_user['has_bot']:
        writeline = []
        for key in bot_template:
            if len(bot_template[key]) > 0:
                if bot_template[key][0] == "{":
                    mykey = bot_template[key]
                    mykey = mykey.replace("{", "")
                    mykey = mykey.replace("}", "")
                    mykey = mykey.replace(" ", "_")
                    writeline.append(this_user[mykey])
                else:
                    if "," in bot_template[key]:
                        writeline.append(f"\"{bot_template[key]}\"")
                    else:
                        writeline.append(bot_template[key])
            else:
                writeline.append(bot_template[key])
        phonefile.write(",".join(str(v) for v in writeline))
        phonefile.write("\n")

    if this_user['has_tct']:
        writeline = []
        for key in tct_template:
            if len(tct_template[key]) > 0:
                if tct_template[key][0] == "{":
                    mykey = tct_template[key]
                    mykey = mykey.replace("{", "")
                    mykey = mykey.replace("}", "")
                    mykey = mykey.replace(" ", "_")
                    writeline.append(this_user[mykey])
                else:
                    if "," in tct_template[key]:
                        writeline.append(f"\"{tct_template[key]}\"")
                    else:
                        writeline.append(tct_template[key])
            else:
                writeline.append(tct_template[key])
        phonefile.write(",".join(str(v) for v in writeline))
        phonefile.write("\n")

    if this_user['has_tab']:
        writeline = []
        for key in tab_template:
            if len(tab_template[key]) > 0:
                if tab_template[key][0] == "{":
                    mykey = tab_template[key]
                    mykey = mykey.replace("{", "")
                    mykey = mykey.replace("}", "")
                    mykey = mykey.replace(" ", "_")
                    writeline.append(this_user[mykey])
                else:
                    if "," in tab_template[key]:
                        writeline.append(f"\"{tab_template[key]}\"")
                    else:
                        writeline.append(tab_template[key])
            else:
                writeline.append(tab_template[key])
        phonefile.write(",".join(str(v) for v in writeline))
        phonefile.write("\n")

    # Now write the user.csv file
    writeline = []
    for key in user_template:
        value = user_template.get(key, "")
        if len(value) > 0 and value[0] == "{":
            value = value.replace("{", "")
            value = value.replace("}", "")
            value = value.replace(" ", "_")
            writeline.append(this_user.get(value, ""))
        else:
            writeline.append(value)
    userfile.write(",".join(str(v) for v in writeline))
    userfile.write("\n")

phonefile.close()
userfile.close()

profile.disable()
ps = pstats.Stats(profile)
#ps.print_stats()
input("Done. Press Enter to continue...")