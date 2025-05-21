#!/usr/bin/env python3
#
# Simple Intel x520 EEPROM patcher
# Modifies the EEPROM to unlock the card for non-intel branded SFP modules.
#
# Copyright 2020,2021,2022 Andreas Thienemann <andreas@bawue.net>
#
# Licensed under the GPLv3
#
# Based on research described at https://forums.servethehome.com/index.php?threads/patching-intel-x520-eeprom-to-unlock-all-sfp-transceivers.24634/
#
# Quick explanation of what's going on:
# Looking at the Intel driver at e.g. https://elixir.bootlin.com/linux/v5.8/source/drivers/net/ethernet/intel/ixgbe/ixgbe_type.h#L2140 we can see
# that the bit 0x1 at Address 0x58 contains a configuration setting whether the card allows any SFP modules or if Intel specific ones are enforced
# by the driver.
#
# Addr Bitstring
# 0x58 xxxxxxx0 means Intel specific SFPs
# 0x58 xxxxxxx1 means any SFP is allowed.
#
# Using the parameter allow_unsupported_sfp for the kernel module we can tell the driver to accept any SFPs.
# But this tool will flip the right bit 1 to make that change permanent in the configuration bits in the EEPROM,
# thus making kernel module parameters unnecessary.
#

import subprocess
import sys

# Supported cards. If your card is supported but not listed here, please add a comment
# with your PCI IDs at https://gist.github.com/ixs/dbaac42730dea9bd124f26cbd439c58e
card_ids = {
    "0x10fb": "82599ES 10-Gigabit SFI/SFP+ Network Connection",
    "0x154d": "Ethernet 10G 2P X520 Adapter",
}

try:
    intf = sys.argv[1]
except IndexError:
    print("%s <interface>" % sys.argv[0])
    exit(255)

print("Verifying interface %s." % intf)

try:
    with open("/sys/class/net/%s/device/vendor" % intf) as f:
        vdr_id = f.read().strip()

    with open("/sys/class/net/%s/device/device" % intf) as f:
        dev_id = f.read().strip()
except IOError:
    print("Can't read interface data.")
    exit(2)

if vdr_id in ("0x8086"):
    print("Recognized an Intel manufactured card.")
else:
    print("No Intel manufactured card found.")
    exit(3)
if dev_id in card_ids:
    print("Recognized the %s card." % card_ids[dev_id])
else:
    print("No recognized x520-based card found.")
    exit(3)

# Read eeprom at offset 0x58
output = subprocess.check_output(
    ["ethtool", "-e", intf, "offset", "0x58", "length", "1"]
).decode("utf-8")

# Parse ethtool output and convert the value into a binary string
val = output.strip().split("\n")[-1].split()[-1]
val_bin = int(val, 16)

print("EEPROM Value at 0x58 is 0x%s (%s)." % (val, bin(val_bin)))
if val_bin & 0b00000001 == 1:
    print("Card is already unlocked for all SFP modules. Nothing to do.")
    exit(1)
if val_bin & 0b00000001 == 0:
    print("Card is locked to Intel only SFP modules. Patching EEPROM...")
    new_val = val_bin | 0b00000001
    print("New EEPROM Value at 0x58 will be %s (%s)" % (hex(new_val), bin(new_val)))

# The "magic" value we need in order to write to a intel card is "0x<device_id><vendor_id>"
magic = "%s%s" % (dev_id, vdr_id[2:])

cmd = [
    "ethtool",
    "-E",
    intf,
    "magic",
    str(magic),
    "offset",
    "0x58",
    "value",
    hex(new_val),
    "length",
    "1",
]

print("About to run %s" % " ".join(cmd))
if (
    input(
        "This operation will write data to your ethernet card eeprom. Type 'yes' to confirm: "
    ).lower()
    != "yes"
):
    print("Operation aborted.")
    exit(1)

output = subprocess.check_output(cmd).decode("utf-8")
if len(output) == 0:
    print("Sucess!")
    print("Reboot the machine for changes to take effect...")
    exit(0)
else:
    print(output)
