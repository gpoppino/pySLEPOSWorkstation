#!/usr/bin/python2

import unittest
from pySLEPOSWorkstation import ModelValidator, WorkstationFileReader, WorkstationModelParser

class TestModelValidator(unittest.TestCase):

    def setUp(self):
        self.__modelValidator = ModelValidator()

    def test_isIPv4Address(self):
        self.assertTrue(self.__modelValidator.isIPv4Address("192.168.1.1"))
        self.assertFalse(self.__modelValidator.isIPv4Address("192.168.11"))
        self.assertFalse(self.__modelValidator.isIPv4Address("168.1.1"))
        self.assertFalse(self.__modelValidator.isIPv4Address("1923.168.1.1"))
        self.assertFalse(self.__modelValidator.isIPv4Address("192.168.1.A"))

    def test_isMACAddress(self):
        self.assertTrue(self.__modelValidator.isMACAddress('52:58:C1:53:12:71'))
        self.assertFalse(self.__modelValidator.isMACAddress('5:58:C1:53:12:71'))
        self.assertFalse(self.__modelValidator.isMACAddress('55:58:C153:12:71'))
        self.assertFalse(self.__modelValidator.isMACAddress('55:58:C1:53:12:71:44'))
        self.assertFalse(self.__modelValidator.isMACAddress('55:58:C1:53:12:'))

    def test_isBranchAttribute(self):
        self.assertTrue(self.__modelValidator.isBranchAttribute('c'))
        self.assertTrue(self.__modelValidator.isBranchAttribute('o'))
        self.assertTrue(self.__modelValidator.isBranchAttribute('ou'))
        self.assertTrue(self.__modelValidator.isBranchAttribute('store'))
        self.assertFalse(self.__modelValidator.isBranchAttribute('cn'))

    def test_isWorkstationAttribute(self):
        self.assertTrue(self.__modelValidator.isWorkstationAttribute('cn'))
        self.assertTrue(self.__modelValidator.isWorkstationAttribute('ipAddress'))
        self.assertTrue(self.__modelValidator.isWorkstationAttribute('macAddress'))
        self.assertTrue(self.__modelValidator.isWorkstationAttribute('cashRegisterType'))
        self.assertTrue(self.__modelValidator.isWorkstationAttribute('cashRegisterDN'))
        self.assertTrue(self.__modelValidator.isWorkstationAttribute('roleBased'))
        self.assertTrue(self.__modelValidator.isWorkstationAttribute('roleDN'))
        self.assertFalse(self.__modelValidator.isWorkstationAttribute('scCashRegister'))

    def test_isBranchComplete(self):
        branchComplete = {'c': 'ar', 'o': 'home', 'ou': 'desk', 'store': 'computer'}
        self.assertTrue(branchComplete)
        branchInComplete = {'o': 'home', 'ou': 'desk', 'store': 'computer'}
        self.assertTrue(branchInComplete)

    def test_hasDuplicateIPAddresses(self):
        self.assertTrue(self.__modelValidator.hasDuplicateIPAddresses([{'ipAddress': '192.168.1.22'}, {'ipAddress': '192.168.1.22'}, \
            {'ipAddress': '192.168.1.23'}]))
        self.assertFalse(self.__modelValidator.hasDuplicateIPAddresses([{'ipAddress': '192.168.1.21'}, {'ipAddress': '192.168.1.22'}, \
            {'ipAddress': '192.168.1.23'}]))

class TestModelParser(unittest.TestCase):

    def setUp(self):
        self.__workstationModelParser = WorkstationModelParser()

        workstationFileReader = WorkstationFileReader("model")
        workstationFileReader.populateModel(self.__workstationModelParser)

    def test_Workstations(self):
        self.assertEqual(self.__workstationModelParser.getWorkstations(), \
            [{'cn': 'REG040', 'ipAddress': '192.168.1.21', 'macAddress': '52:55:00:58:12:73', \
                'cashRegisterType': 'NCR7600-1001-8801', \
                    'cashRegisterDN': 'cn=CR-NCR7600-1001-8801,cn=RoleOneScreen,cn=global,o=myorg,c=ar', \
                        'roleBased': 'True', 'roleDN': 'cn=RoleOneScreen,cn=global,o=myorg,c=ar'},
             {'cn': 'REG041', 'ipAddress': '192.168.1.22', 'macAddress': '52:58:00:53:12:71', \
                 'cashRegisterType': 'NCR7600-2000-8801', \
                     'cashRegisterDN': 'cn=CR-NCR7600-2000-8801,cn=global,o=myorg,c=ar', 'roleBased': 'False'}])

    def test_Branch(self):
        self.assertEqual(self.__workstationModelParser.getBranch(), {'c':'ar', 'o': 'myorg', 'ou': 'myou', \
            'store': 'mystore'})
        self.assertNotEqual(self.__workstationModelParser.getBranch(), {'c':'pe', 'o': 'myorg', 'ou': 'myou', \
            'store': 'mystore'})

if __name__ == '__main__':
    unittest.main()
