#!/usr/bin/env python

import sys
import os
import subprocess
import re
import shutil
from datetime import datetime
import json
import argparse
from dotenv import dotenv_values


def loadEnvFile():
    global dotenv
    dotenv = {}
    if os.path.exists(".env"):
        dotenv = dotenv_values(".env")
    return


def getBW():
    bw_cli = "bw"
    global bw_cli_path
    bw_cli_path = shutil.which(bw_cli)
    
    if bw_cli_path is None:
        print("The path to " + bw_cli + " was not found.")
        sys.exit(1)
    
    return


def bwLogin():
    global serverurl
    if (args.docker):
        serverurl = os.environ['BW_SERVER']
    else:
        serverurl = args.server

    if (args.debug):
        print(f"Server: {serverurl}")
    
    # Retrieve bw status so we can change the server if necessary
    getStatus = subprocess.Popen([bw_cli_path, 'status'], stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
    getStatus.wait()
    out, err = getStatus.communicate()
    bwStatus = json.loads(out.decode())

    if (args.debug):
        print(f"serverURL: {bwStatus['serverUrl']}")
        print(f"status: {bwStatus['status']}")
    if (args.docker):
        print(bwStatus)
        
    # Set BW login server
    if (bwStatus['serverUrl'] != serverurl):
        if (bwStatus['status'] == "unauthenticated"):
            setServer = subprocess.Popen([bw_cli_path, 'config', 'server', serverurl], stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
            setServer.wait()
            out, err = setServer.communicate()
            errcode = setServer.returncode
            
            if (args.docker):
                print(out.decode())
            if (err):
                print(f"Error: {err.decode()}")
                print(f"Error code: {errcode}")
                sys.exit(errcode)
    
    # Show configured bw login server
    showServer = subprocess.Popen([bw_cli_path, 'config', 'server'], stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
    showServer.wait()
    out, err = showServer.communicate()
    
    if (args.docker):
        print(out.decode())
    if (args.debug):
        print(f"BW config: {out.decode()}")
    
    # Login
    global bwEmail
    if (args.docker):
        bwEmail = os.environ['BW_EMAIL']
    elif (args.email is None) and not (args.docker):
        bwEmail = str(dotenv['email'])
    elif (args.email) and not (args.docker):
        bwEmail = args.email
    else:
        print("An email is required")
        sys.exit(2)
    
    if (args.docker):
        bwPassword = os.environ['BW_PASSWORD']  
    elif (args.password is None) and not (args.docker):
        bwPassword = str(dotenv['password'])
    elif (args.password) and not (args.docker):
        bwPassword = args.password
    else:
        print("A password is required")
        sys.exit(3)
        
    login = subprocess.Popen([bw_cli_path, 'login', bwEmail, bwPassword], stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    login.wait()
    out, err = login.communicate()
    
    if (args.docker):
        print(out.decode())
    if (err):
        if re.match(r"You are already logged in", err.decode()) is None:
            print(f"Error: {err.decode()}")
            print(f"Error code: {login.returncode}")
            sys.exit(login.returncode)

    # Unlock the vault
    unlockVault = subprocess.Popen([bw_cli_path, 'unlock', bwPassword, '--raw'], stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    unlockVault.wait()
    out, err = unlockVault.communicate()
    
    if (err):
        print(f"Error: {err.decode()}")
        print(f"Error code: {unlockVault.returncode}")
        sys.exit(unlockVault.returncode)
    
    global bw_session
    bw_session = out.decode()

    if (args.docker):
        print(bw_session)
    if (args.debug):
        print(f"BW session: {bw_session}")

    return


def bwUserBackup():
    now = datetime.now()
    global filePath
    filePath = args.output + "/" + now.strftime("%Y") + "/" + now.strftime("%m") + "/" + now.strftime("%d") + "/"
    if (args.debug):
        print(f"File path: {filePath}")
    
    # Backup user vault
    exportUserVault = subprocess.Popen([bw_cli_path, 'export', '--session', bw_session , '--format', 'encrypted_json', '--output', filePath + bwEmail + "_passwords.enc"], 
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exportUserVault.wait()
    out, err = exportUserVault.communicate()
    
    if (args.docker):
        print(out.decode())
    if (err):
        print(f"Error: {err.decode()}")
        print(f"Error code: {exportUserVault.returncode}")
        sys.exit(exportUserVault.returncode)
    
    return


def bwOrgBackup():
    if (args.debug) or (args.docker):
        print(f"File path: {filePath}")
    bwOrgs = []
    # List Orgs
    listOrgs = subprocess.Popen([bw_cli_path, 'list', 'organizations', '--session', bw_session], 
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    listOrgs.wait()
    out, err = listOrgs.communicate()
    bwOrgs = json.loads(out.decode())
    
    if (args.docker):
        print(f"Match: {bwOrgs}, Length: {len(bwOrgs)}")
    if (err):
        print(f"Error: {err.decode()}")
        print(f"Error code: {listOrgs.returncode}")
        sys.exit(listOrgs.returncode)
    
    for org in bwOrgs:
        # bw export --organizationid 7063feab-4b10-472e-b64c-785e2b870b92 --format json --output /Users/myaccount/Downloads/
        exportOrgVault = subprocess.Popen([bw_cli_path, 'export', '--session', bw_session , '--organizationid', org["id"], '--format', 'encrypted_json', '--output', filePath + org["name"] + "_passwords.enc"], 
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exportOrgVault.wait()
        out, err = exportOrgVault.communicate()
        
        if (args.docker):
            print(out.decode())
        if (err):
            print(f"Error: {err.decode()}")
            print(f"Error code: {exportOrgVault.returncode}")
            sys.exit(exportOrgVault.returncode)
    return


def bwLogout():
    logout = subprocess.Popen([bw_cli_path, 'logout'], stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    logout.wait()
    out, err = logout.communicate()
    
    if (args.docker):
        print(out.decode())
    if (err):
        if re.match(r"You are not logged in.", err.decode()) is None:
            print(f"Error: {err.decode()}")
            print(f"Error code: {logout.returncode}")
            sys.exit(logout.returncode)
    return


def main():
    loadEnvFile()
    
    global args
    parser = argparse.ArgumentParser(prog='vwbackup',
                description='This program is a wrapper around Bitwarden CLI to create backups')
    parser.add_argument("-o", "--output", help="Full path to output folder (Defaults to /app/output for docker container)", default="/app/output")
    parser.add_argument("-s", "--server", help="Server URL if using self hosted instance")
    parser.add_argument("--email", help="User email login")
    parser.add_argument("--password", help="User password for login (fairly insecure)")
    parser.add_argument("--orgs", help="Backup the organizations you have access to export", action='store_true')
    parser.add_argument("--docker", help="Docker mode", action='store_true')
    parser.add_argument("--debug", help="Debug output", action='store_true')
    args = parser.parse_args()
    
    getBW()
    
    if (args.debug):
        print(f"Args debug: {args.debug}")
        print("bw found at: " + bw_cli_path)
        print(f"Args output folder: {args.output}")
        print(f"Args email: {args.email}")
        print(f"Args password: {args.password}")
        print(f"Args server: {args.orgs}")
        print(f"Args server: {args.server}")
        print(f"Args docker: {args.docker}")
        if (args.docker):
            print(f"Env email: {os.environ['BW_EMAIL']}")
            print(f"Env password: {os.environ['BW_PASSWORD']}")
        if (dotenv):
            print(f"Dotenv: {dotenv}")
            print(f"Dotenv Email: {str(dotenv['email'])}")
            print(f"Dotenv Password: {str(dotenv['password'])}")
        
    bwLogin()
    
    bwUserBackup()
    
    if (args.docker) or (args.orgs):
        bwOrgBackup()
    
    bwLogout()
    
    
main()