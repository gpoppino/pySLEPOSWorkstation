#!/usr/bin/python2

import sys
import getopt
import subprocess

class WorkstationModelParser:

    def __init__(self):
        self.__branchDict = {}
        self.__currentWorkstationDict = {}
        self.__workstations = []

    def __addWorkstation(self):
        if self.__currentWorkstationDict != {}:
            self.__workstations.append(self.__currentWorkstationDict)
        self.__currentWorkstationDict = {}

    def __insertBranchAttribute(self, key, value):
        self.__branchDict[ key ] = value

    def insertAttribute(self, line):
        line = line.strip()
        if line == "":
            self.__addWorkstation()
            return

        data = line.split(":", 1)

        if data[0] in ["c", "o", "ou", "store"]:
            self.__insertBranchAttribute(data[0], data[1].strip())
            return

        self.__currentWorkstationDict[ data[0] ] = data[1].strip()

    def getWorkstations(self):
        return self.__workstations

    def getBranch(self):
        return self.__branchDict

    def __repr__(self):
        return "Branch: %s\nWorkstations: %s" % (self.__branchDict, self.__workstations)


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
        for workstation in self.__workstations:
            if workstation['roleBased'] == "True":
                subprocess.call(["/usr/sbin/posAdmin", "--base", self.__buildLDAPBase(), "--add", "--scWorkstation", \
                    "--cn", workstation['cn'], "--ipHostNumber", workstation['ipAddress'], "--macAddress", workstation['macAddress'], \
                    "--scRoleBased", "TRUE", "--scRefPcDn", workstation['cashRegisterDN'], "--scPosRegisterType", workstation['cashRegisterType'], \
                    "--scRoleDn", workstation['roleDN']])
            else:
                subprocess.call(["/usr/sbin/posAdmin", "--base", self.__buildLDAPBase(), "--add", "--scWorkstation", \
                    "--cn", workstation['cn'], "--ipHostNumber", workstation['ipAddress'], "--macAddress", workstation['macAddress'], \
                    "--scRoleBased", "FALSE", "--scRefPcDn", workstation['cashRegisterDN'], "--scPosRegisterType", workstation['cashRegisterType']])

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

    workstationCreator = WorkstationCreator(workstationModelParser.getBranch(), workstationModelParser.getWorkstations())
    workstationCreator.createWorkstations()

if __name__ == "__main__":
    main(sys.argv)
