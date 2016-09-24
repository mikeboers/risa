

Installation
------------

# Install our dependencies (system-wide).
# ntp is required to keep the clocks accurate
pacman -S python-setuptools python-pip make gcc ntp
pip install rpi.gpio

# Create a group for those who have permission to do GPIO.
groupadd --system gpio

# Create the user for running as.
useradd -m -d /var/lib/risa risa
usermod -aG gpio risa

# If you want to be in that group too!
usermod -aG gpio mikeboers

# Setup the config; atleast SECRET and DEVICE_NAME
touch /etc/risa
chown risa:risa /etc/risa
chmod ug=rw,o= /etc/risa
vi /etc/risa # EDIT HERE

# Setup systemd
cp etc/systemd/* /etc/systemd/system/
systemctl enable gpio-perms
systemctl start gpio-perms
