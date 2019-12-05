# pySLEPOSWorkstation

Creates SLEPOS workstations in batch from a text file

## Model

In order to load a group of workstations (scWorkstation objects) to the LDAP database of a SLEPOS11 implementation, it is necessary to first work on the *model* file that has the information of these workstations and a store or location (scLocation object).

A model file has a key and value format. This is an example of a locatiton and a workstation entry:

```yaml
c: ar
o: myorg
ou: myou
store: mystore

cn: REG040
ipAddress: 192.168.1.21
macAddress: 52:55:00:58:12:73
cashRegisterType: NCR7600-1001-8801
cashRegisterDN: cn=CR-NCR7600-1001-8801,cn=RoleOneScreen,cn=global,o=myorg,c=ar
roleBased: True
roleDN: cn=RoleOneScreen,cn=global,o=myorg,c=ar
```

## Execution

Running the script is done in the following ways:

`python2 pySLEPOSWorkstation -i model`

This loads the workstations specified in the *model* file to the store described at the top of the file.

You may also load workstations to many stores, in the following way:

```bash
for model in store1015 store1016 sto1017;
do
    python2 pySLEPOSWorkstation -i ${model}
done
```

## Verifying results

Once the script has been executed, you may verify the results in this way:

`# posAdmin --query --full`

## Requirements

The script requires:

* To be run as *root* user.
* *Python 2* version.
