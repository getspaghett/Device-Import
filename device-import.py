#!/usr/bin/env python3
from collections import Counter
from datetime import datetime
import yaml
import pynetbox
from glob import glob
import os

import settings
from netbox_api import NetBox

from hw import HardwareInfo

from device_type_template import DeviceType

import re

def find_vendor(dmi, vendors):
    '''
    Find the vendor from the dmi output in the list of vendors provided by the device-type library repo.
    Returns true when a vendor matches the dmi output, false otherwise.
    This function contains a list of possible matched vendors, not sure if this is useful yet.
    TODO: Split into two functions
    '''
    dmi_vendor = dmi.manufacturer().lower()
    match = False
    possible_matches = []
    for vendor in vendors:
        if dmi_vendor in (vendor.get('name')).lower():
            possible_matches.append(vendor.get('name'))
            if dmi_vendor == (vendor.get('name')).lower():
                print(f'Vendor found in DMI ({dmi_vendor}) matches vendor in Netbox ({vendor.get("name")})')
                match = True
                break
    if match == False:
        print(f'Vendor found in DMI ({dmi_vendor}) does not match any vendor in Netbox')
        print(f'Possible matches: {possible_matches}')
    return match

def boolVendorMatch(dmi, vendors) -> bool:
    '''
    Returns true if the vendor listed in the dmi tables matches any vendor in the list of vendors provided by the device-type library repo.
    '''
    dmi_vendor = dmi.manufacturer().lower()
    match = False
    for vendor in vendors:
        if dmi_vendor == (vendor.get('name')).lower():
            match = True
            break
    return match

def getMatchedVendor(dmi, vendors) -> str:
    '''
    Returns the vendor name that matches the vendor listed in the dmi tables.
    '''
    dmi_vendor = dmi.manufacturer().lower()
    matchedVendor = ""
    match = False
    for vendor in vendors:
        if dmi_vendor == (vendor.get('name')).lower():
            match = True
            matchedVendor = vendor.get('name')
            break
    if match == False:
        print(f'Vendor found in DMI ({dmi_vendor}) does not match any vendor in Netbox')
        matchedVendor = dmi_vendor
    return matchedVendor

def getPossibleMatches(dmi, vendors) -> list:
    '''
    Returns a list of possible matches for the vendor listed in the dmi tables.
    '''
    dmi_vendor = dmi.manufacturer().lower()
    match = False
    possible_matches = []
    for vendor in vendors:
        if dmi_vendor in (vendor.get('name')).lower():
            possible_matches.append(vendor.get('name'))
            if dmi_vendor == (vendor.get('name')).lower():
                print(f'Vendor found in DMI ({dmi_vendor}) matches vendor in Netbox ({vendor.get("name")})')
                match = True
                break
    if match == False:
        print(f'Vendor found in DMI ({dmi_vendor}) does not match any vendor in Netbox')
        print(f'Possible matches: {possible_matches}')
    return possible_matches

def saveToYAML(my_device_type: DeviceType = None, filename: str = ''):
    assert isinstance(my_device_type, DeviceType)
    if filename == '':
        filename = HardwareInfo().node + '.yaml'
    with open(filename, 'w') as file:
        yaml.dump(my_device_type.getYAML(), file, sort_keys=False, explicit_start=True)
    print('YAML file created')

def checkVendorInNetbox(dmi, netbox) -> bool:
    '''
    Returns true if the vendor listed in the dmi tables matches any vendor that is in Netbox.
    '''
    dmi_vendor = dmi.manufacturer().lower()
    match = False
    for vendor in netbox.get_manufacturers():
        if dmi_vendor == (vendor.get('name')).lower():
            match = True
            break
    return match

def checkVendorInDTLRepo(dmi, vendors) -> bool:
    '''
    Returns true if the vendor listed in the dmi tables matches any vendor in the list of vendors provided by the device-type library repo.
    '''
    dmi_vendor = dmi.manufacturer().lower()
    match = False
    for vendor in vendors:
        if dmi_vendor == (vendor.get('name')).lower():
            match = True
            break
    return match

def main():
    my_device = DeviceType()
    startTime = datetime.now()
    args = settings.args

    # Init Hardware Info Class
    dmi = HardwareInfo().getDmiInfo()# some of the pre-defined queries
    print('Manufacturer:\t', dmi.manufacturer())
    print('Model:\t\t', dmi.model())
    print('Firmware:\t', dmi.firmware())
    print('Serial number:\t', dmi.serial_number())
    print('Processor type:\t', dmi.cpu_type())
    print('Number of CPUs:\t', dmi.cpu_num())
    print('Cores count:\t', dmi.total_enabled_cores())
    print('Total RAM:\t{} GB'.format(dmi.total_ram()))
    print('# DIMM Slots:\t', dmi.total_dimm_slots())
    print('Chassis Type:\t', dmi.chassis_type())
    my_device.manufacturer = dmi.manufacturer()
    my_device.model = dmi.model()
    my_device.slug = re.sub('\W+', '-', my_device.model.lower())

    netbox = NetBox(settings)
    files, vendors = settings.dtl_repo.get_devices(
        f'{settings.dtl_repo.repo_path}/device-types/', args.vendors)
    repo_vendors = vendors
    nb_vendors = netbox.get_manufacturers()
    settings.handle.log(f'{len(vendors)} Vendors Found')
    device_types = settings.dtl_repo.parse_files(files, slugs=args.slugs)
    settings.handle.log(f'{len(device_types)} Device-Types Found')

    # Commented to not create vendors and device_types on Netbox yet.
    # netbox.create_manufacturers(vendors)
    # netbox.create_device_types(device_types)
    
    print("Debug: -----")
    match = boolVendorMatch(dmi, vendors)
    print(f'Vendor Match: {match}')
    matchedVendor = getMatchedVendor(dmi, vendors)
    print(f'Matched Vendor: {matchedVendor}')
    #saveToYAML(my_device)
    if netbox.modules:
        settings.handle.log("Modules Enabled. Creating Modules...")
        files, vendors = settings.dtl_repo.get_devices(
            f'{settings.dtl_repo.repo_path}/module-types/', args.vendors)
        settings.handle.log(f'{len(vendors)} Module Vendors Found')
        module_types = settings.dtl_repo.parse_files(files, slugs=args.slugs)
        settings.handle.log(f'{len(module_types)} Module-Types Found')
        # Commented to not create module_types yet.
        # netbox.create_manufacturers(vendors)
        # netbox.create_module_types(module_types)

    settings.handle.log('---')
    settings.handle.verbose_log(
        f'Script took {(datetime.now() - startTime)} to run')
    settings.handle.log(f'{netbox.counter["added"]} devices created')
    settings.handle.log(
        f'{netbox.counter["updated"]} interfaces/ports updated')
    settings.handle.log(
        f'{netbox.counter["manufacturer"]} manufacturers created')
    if settings.NETBOX_FEATURES['modules']:
        settings.handle.log(
            f'{netbox.counter["module_added"]} modules created')
        settings.handle.log(
            f'{netbox.counter["module_port_added"]} module interface / ports created')


if __name__ == "__main__":
    main()
