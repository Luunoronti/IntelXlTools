# xl520_unlock (2x1GBe and 2x10GBe)

under ubuntu linux
```shell
git clone
cd folder
ip link show (note names, like eno1, eno4, etc)
sudo python3 intel_x520_patcher.py
reboot
```



# xl710_unlock

This program unlocks intel xl710 NICs.

## Usage

```shell
# ./xl710_unlock -n enp4s0f0
EMP SR offset: 0x67a8
PHY offset: 0x68f6
PHY data struct size: 0x000c
MISC: 0x6b0c <- locked
MISC: 0x6b0c <- locked
MISC: 0x6b0c <- locked
MISC: 0x6b0c <- locked
Ready to fix it? [y/N]: y
```
