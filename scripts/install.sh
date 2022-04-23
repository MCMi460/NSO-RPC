#
# This is intended for Ubuntu Linux
# although it may work for other distributions
# Please contact me if this fails
#

cd ../client
sudo apt-get install python3-pyqt5
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
execFile=$HOME'/Desktop/nsorpc.desktop'
touch $execFile

printf $'[Desktop Entry]\nType=Application\nName=Nintendo Switch Online Rich Presence\nGenericName=NSO-RPC\nComment=Display your Nintendo Switch game status on Discord!\nExec=bash -c "cd /opt/NSO-RPC && python3 app.py"\nIcon=icon\nTerminal=false\nCategories=Game;Application;Utility;' > $execFile
chmod +x $execFile
