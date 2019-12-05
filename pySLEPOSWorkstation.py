#!/usr/bin/python2
"""
pySLEPOSWorkstation: Adds SLEPOS workstations in batch mode to a LDAP database
Copyright (C) 2019 Geronimo Poppino

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import sys
import getopt
import socket
import subprocess

class WorkstationModelParser:

    def __init__(self):
        self.__branchDict = {}
        self.__currentWorkstationDict = {}
        self.__workstations = []
        self.__skip = False

        self.__modelValidator = ModelValidator()

    def __addWorkstation(self):
        if self.__currentWorkstationDict != {}:
            self.__workstations.append(self.__currentWorkstationDict)

    def __insertBranchAttribute(self, key, value):
        self.__branchDict[ key ] = value

    def insertAttribute(self, line):
        line = line.strip()
        if line == "":
            if not self.__skip:
                self.__addWorkstation()
            self.__currentWorkstationDict = {}
            self.__skip = False
            return

        data = line.split(":", 1)
        value = data[1].strip()

        if self.__modelValidator.isBranchAttribute(data[0]):
            self.__insertBranchAttribute(data[0], value)
            return

        if self.__modelValidator.isWorkstationAttribute(data[0]):
            if self.__modelValidator.validateWorkstationValue(data[0], value):
                self.__currentWorkstationDict[ data[0] ] = value
            else:
                self.__skip = True
                return

    def getWorkstations(self):
        return self.__workstations

    def getBranch(self):
        return self.__branchDict

    def validate(self):
        return self.__modelValidator.isBranchComplete(self.__branchDict)

    def __repr__(self):
        return "Branch: %s\nWorkstations: %s" % (self.__branchDict, self.__workstations)


class ModelValidator:

    def __init__(self):
        self.__validBranchAttributes = ['c', 'o', 'ou', 'store']
        self.__validWorkstationAttributes = ['cn', 'ipAddress', 'macAddress', 'cashRegisterType', 'cashRegisterDN', \
            'roleBased', 'roleDN']

    def isBranchAttribute(self, attr):
        return attr in self.__validBranchAttributes

    def isWorkstationAttribute(self, attr):
        return attr in self.__validWorkstationAttributes

    def isBranchComplete(self, branch):
        attrs = branch.keys()
        for key in self.__validBranchAttributes:
            if key not in attrs:
                return False
        return True

    def validateWorkstationValue(self, attr, value):
        if attr == 'ipAddress':
            return self.isIPv4Address(value)

        if attr == 'macAddress':
            return self.isMACAddress(value)

        return True

    def isIPv4Address(self, ipAddress):
        try:
            socket.inet_pton(socket.AF_INET, ipAddress)
        except AttributeError:  # no inet_pton here, sorry
            try:
                socket.inet_aton(ipAddress)
            except socket.error:
                return False
            return ipAddress.count('.') == 3
        except socket.error:  # not a valid address
            return False

        return True

    def isMACAddress(self, mac):
        return re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower())


class WorkstationFileReader:

    def __init__(self, filename):
        self.__filename = filename

    def populateModel(self, workstationModelParser):
        with open(self.__filename) as f:
            for line in f:
                workstationModelParser.insertAttribute(line)


class WorkstationCreator:

    def __init__(self, branch, workstations):
        self.__branch = branch
        self.__workstations = workstations

    def __buildLDAPBase(self):
        return "cn=" + self.__branch['store'] + ",ou=" + self.__branch['ou'] + ",o=" + self.__branch['o'] + ",c=" + self.__branch['c']

    def createWorkstations(self):

        resultsProcessor = ResultsProcessor(self.__branch)

        for workstation in self.__workstations:
            posAdminCmd = ["/usr/sbin/posAdmin", "--base", self.__buildLDAPBase(), "--add", "--scWorkstation", \
                "--cn", workstation['cn'], "--ipHostNumber", workstation['ipAddress'], \
                "--macAddress", workstation['macAddress'].upper(), "--scRefPcDn", workstation['cashRegisterDN'], \
                "--scPosRegisterType", workstation['cashRegisterType']]

            if workstation['roleBased'].upper() == "TRUE":
                posAdminCmd += ["--scRoleBased", "TRUE", "--scRoleDn", workstation['roleDN']]
            else:
                posAdminCmd += ["--scRoleBased", "FALSE"]

            retValue = subprocess.call(posAdminCmd)

            resultsProcessor.showResult(workstation, retValue)

        resultsProcessor.showSummary()

class ResultsProcessor:

    def __init__(self, branch):
        self.__branch = branch
        self.__failedCounter = 0
        self.__addedWorkstations = []
        self.__failedWorkstations = []

    def showResult(self, workstation, retValue):
        msg = "Store: " + self.__branch['store'] + ". Workstation: " + workstation['cn']

        if retValue == 0:
            print(msg + "... added successfully!")
            self.__addedWorkstations.append(workstation['cn'])
        else:
            print(msg + "... failed to be added :-(")
            self.__failedCounter += 1
            self.__failedWorkstations.append(workstation['cn'])

    def showSummary(self):
        print("== Summary for Store %s =="% self.__branch['store'])
        print("Successfully added workstations:")
        print(self.__addedWorkstations)
        print("Failed workstations:")
        print(self.__failedWorkstations)
        print("Failed counter: %d"% self.__failedCounter)


def showHelp(cmd):
    print cmd + " -i model"

def getStoreModelFile(argv):

    try:
        opts, args = getopt.getopt(argv[1:],"i:", )
    except getopt.GetoptError:
        showHelp(argv[0])
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-i':
            return arg

    showHelp(argv[0])
    sys.exit(2)


def main(argv):
    workstationModelParser = WorkstationModelParser()

    f = getStoreModelFile(argv)
    workstationFileReader = WorkstationFileReader(f)
    workstationFileReader.populateModel(workstationModelParser)

    if not workstationModelParser.validate():
        print("Imcomplete or invalid data in model file! Aborting...")
        return 1

    workstationCreator = WorkstationCreator(workstationModelParser.getBranch(), workstationModelParser.getWorkstations())
    workstationCreator.createWorkstations()

if __name__ == "__main__":
    main(sys.argv)
