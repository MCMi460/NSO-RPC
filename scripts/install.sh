#!/bin/bash
#
# This is intended for Ubuntu Linux
# although it may work for other distributions
# Please contact me if this fails
#

function checkDir {
  if [ ! -d $1 ]
  then
    sudo mkdir $1
  fi
}

# Only try and install pip if its missing
if pip --version &>/dev/null; then
  sudo apt-get install python3-pyqt5
else
  sudo apt-get install python3-pyqt5 python3-pip
fi

cd ../client
python3 -m pip install -r requirements.txt

executableDir='/opt/NSO-RPC/'

if [ -d $executableDir ]
then
  echo 'Installation already exists, would you like to overwrite it?'
  read -p '[Y/N] ' confirm
  confirm=$(echo $confirm | tr 'a-z' 'A-Z')
  if [[ ! $confirm =~ ^Y ]]
  then
    exit
  fi
  sudo rm -r $executableDir
elif [ ! -d $executableDir ]
then
  sudo mkdir $executableDir
fi

sudo cp -a './' $executableDir

# Begin creating .desktop alias
execDir='/usr/share/applications'
execFile=$execDir'/nsorpc.desktop'
checkDir $execDir
sudo touch $execFile

iconDir='/usr/share/pixmaps'
checkDir $iconDir

sudo cp './icon.svg' $iconDir'/nso.svg'

content="[Desktop Entry]\nType=Application\nName=Nintendo Switch Online Rich Presence\nGenericName=NSO-RPC\nComment=Display your Nintendo Switch game status on Discord!\nExec=bash -c 'cd /opt/NSO-RPC && python3 app.py'\nIcon=nso.svg\nTerminal=false\nCategories=Game;Application;Utility;"
printf "$content" | sudo tee $execFile > /dev/null
sudo chmod +x $execFile
