#!/bin/bash
#
# This is intended for Ubuntu Linux
# although it may work for other distributions
# Please contact me if this fails
#

if [ ! -d './NSO-RPC' ]
then
    git clone 'https://github.com/MCMi460/NSO-RPC'
fi

cd './NSO-RPC/scripts'
chmod +x './install.sh'
./install.sh