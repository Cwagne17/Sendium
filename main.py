#!/usr/bin/env python3

"""A tool that use the SMTP protocol to draft and send an email about system information.
"""
    
__author__ = "Chris Wagner"
__copyright__ = "Copyright 2023, Chris Wagner"
__email__ = "cwagne17@students.towson.edu"

import cpuinfo
import os
import requests
import json
import platform
import psutil
import shutil
import logging
import ssl
import smtplib
from smtplib import SMTPAuthenticationError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
## Sets up logging configuration

logger = logging.getLogger(__name__)

logging.basicConfig(   
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("output.log"),
        logging.StreamHandler()
    ]
)

app_pass_2fv = "https://myaccount.google.com/security?utm_source=OGB&utm_medium=act#signin"
allow_less_secure_app = "https://myaccount.google.com/u/1/lesssecureapps?pli=1&pageId=none"

SENDER_EMAIL=""
PASSWORD=""
RECIPIENT_EMAIL=""

PUBLIC_IP=""
OS_NAME_AND_TYPE=""
DISK_AVAIL=""
MEM_AVAIL=""
MEM_TOTAL=""
CPU_NAME=""
CPU_SPEED=""
SERVICES=[]

def set_machine_information():
    """Sets the machine information."""
    global PUBLIC_IP, OS_NAME_AND_TYPE, DISK_AVAIL, MEM_AVAIL, MEM_TOTAL, CPU_NAME, CPU_SPEED, SERVICES
    
    # Set the OS name and type
    OS_NAME_AND_TYPE = platform.platform() 
    
    # Set the public IP address
    response = requests.get("https://api.ipify.org?format=json")
    PUBLIC_IP = json.loads(response.text)["ip"]
    
    # Set the available disk space
    DISK_AVAIL = round((shutil.disk_usage("/").free)/(1024**3), 2)
    
    # Set Memory information
    MEM_AVAIL = round(psutil.virtual_memory().available/(1024**3), 2)
    MEM_TOTAL = round(psutil.virtual_memory().total/(1024**3), 2)
    
    # Set CPU information
    CPU_NAME = cpuinfo.get_cpu_info()["brand_raw"]
    # CPU_SPEED = cpuinfo.get_cpu_info()["hz_actual_friendly"]

    # Aggregate list of active services
    SERVICES = []
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
        except psutil.NoSuchProcess:
            pass
        else:
            SERVICES.append(pinfo['name'])
    set(SERVICES)
    

def build_email_message():
    return f"""
        <html>
            <body>
                <h1>{OS_NAME_AND_TYPE} - {PUBLIC_IP}</h1>

                <h2>Hardware Information</h2>
                
                <table style='border:1px solid #b3adad; border-collapse:collapse; padding:5px;'>
                    <thead style='border:1px solid #b3adad; padding:5px; background: #8fe0e6; color: #313030;'>
                        <tr>
                            <th>Name</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody style='border:1px solid #b3adad; text-align:center; padding:5px; background: #ffffff; color: #313030;'>
                        <tr>
                            <td>Available Memory</td>
                            <td>{MEM_AVAIL} GB</td>
                        </tr>
                        <tr>
                            <td>RAM Size</td>
                            <td>{MEM_TOTAL} GB</td>
                        </tr>
                        <tr>
                            <td>Available Disk</td>
                            <td>{DISK_AVAIL} GB</td>
                        </tr>
                        <tr>
                            <td>CPU Name</td>
                            <td>{CPU_NAME}</td>
                        </tr>
                        <tr>
                            <td>CPU Speed</td>
                            <td>{CPU_SPEED} Mhz</td>
                        </tr>
                </table>
                
                <h2>Services</h2>
                
                <p>{SERVICES}</p>
            </body>
        </html>
        """

def send_email():
    """Sends an email using the SMTP protocol.
    """
    # Create SMTP object
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        # Identify yourself to an ESMTP server using EHLO
        smtp.ehlo()
        # Put SMTP connection in TLS (Transport Layer Security) mode
        smtp.starttls(context=ssl.create_default_context())
        try:
            # Log in on an SMTP server that requires authentication
            smtp.login(SENDER_EMAIL, PASSWORD)
        except SMTPAuthenticationError as err:
            print(str(err))
        email_message = MIMEMultipart()
        email_message["From"] = SENDER_EMAIL
        email_message["To"] = RECIPIENT_EMAIL
        email_message["Subject"] = "Sendium - System Information"
        email_message.attach(MIMEText(build_email_message(), "html"))
        smtp.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, email_message.as_string())

def options():
    """Displays the global variables."""
    print(f"""
    Name                Value
    ----                -----      
          
    SENDER_EMAIL:       {SENDER_EMAIL}
    PASSWORD:           {PASSWORD}
    
    RECIPIENT_EMAIL:    {RECIPIENT_EMAIL}
    """)

def get_variable(variable):
    """Gets a variable."""
    if variable == "SENDER_EMAIL":
        print(f"\nSENDER_EMAIL: {SENDER_EMAIL}\n")
    elif variable == "PASSWORD":
        print(f"\nPASSWORD: {PASSWORD}\n")
    elif variable == "RECIPIENT_EMAIL":
        print(f"\nRECIPIENT_EMAIL: {RECIPIENT_EMAIL}\n")
    else:
        print(bcolors.FAIL + bcolors.BOLD + "\nInvalid variable name. Valid variables are: SENDER_EMAIL, PASSWORD, RECIPIENT_EMAIL.\n" + bcolors.ENDC)

def set_variable(variable, value):
    """Sets a variable to a value."""
    if variable == "SENDER_EMAIL":
        global SENDER_EMAIL
        SENDER_EMAIL = value
    elif variable == "PASSWORD":
        global PASSWORD
        PASSWORD = value
    elif variable == "RECIPIENT_EMAIL":
        global RECIPIENT_EMAIL
        RECIPIENT_EMAIL = value
    else:
        print(bcolors.FAIL + bcolors.BOLD + "\nInvalid variable name. Valid variables are: SENDER_EMAIL, PASSWORD, RECIPIENT_EMAIL.\n" + bcolors.ENDC)

def output_options():
    print("""
    Command      Description
    -------      -----------
    ?            Help menu
    clear        Clears the screen
    draft        Drafts an email
    get          Gets a context specific variable
    help         Help menu
    options      Displays global variables
    quit         Quits the program
    set          Sets a context specific variable
    send         Sends an email
    """)

def handle_input():
    while True:
        command = input(bcolors.OKGREEN + "(Sendium)" + bcolors.ENDC + " > ")
        
        if command == "?": output_options()
        elif command == "clear": os.system("clear")
        elif command == "draft": print("Drafting email...")
        elif command.startswith("get"):
            split_command = command.split()
            if len(split_command) != 2: print(bcolors.FAIL + bcolors.BOLD + "\nInvalid command. `get` requires 1 argument.\nUsage: `get VARIABLE`\n" + bcolors.ENDC); continue
            get_variable(split_command[1])
        elif command == "help": output_options()
        elif command == "options": options()
        elif command == "quit" or command == "q": exit()
        elif command.startswith("set"):
            split_command = command.split()
            if len(split_command) != 3: print(bcolors.FAIL + bcolors.BOLD + "\nInvalid command. `set` requires 2 arguments.\nUsage: `set VARIABLE value`\n" + bcolors.ENDC); continue
            set_variable(split_command[1], split_command[2])
        elif command == "send": send_email()
        else: print(bcolors.FAIL + bcolors.BOLD + "\nInvalid command. Type `help` to see a list of commands.\n" + bcolors.ENDC)
        
def intro():
    print(bcolors.OKBLUE + bcolors.BOLD + """
          
 _____                _ _                 
/  ___|              | (_)                
\ `--.  ___ _ __   __| |_ _   _ _ __ ___  
 `--. \/ _ \ '_ \ / _` | | | | | '_ ` _ \ 
/\__/ /  __/ | | | (_| | | |_| | | | | | |
\____/ \___|_| |_|\__,_|_|\__,_|_| |_| |_|

""" + bcolors.ENDC + bcolors.OKCYAN + bcolors.BOLD + """
Sendium is a simple tool that sends system information to an email address.
Currently, it only has support for Gmail accounts.

To get started type `help` to see a list of commands.
    """ + bcolors.ENDC)

if __name__ == "__main__":
    set_machine_information()

    intro()
    
    handle_input()
