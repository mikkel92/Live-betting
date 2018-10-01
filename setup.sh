# Set up the paths required for data analysis (edit for personal config)

#Get path to this script
#Note: Handles many use cases (e.g. '.' vs 'source', sym links, etc) 
#Stolen from: http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in
SCRIPT_PATH="${BASH_SOURCE[0]}";
if ([ -h "${SCRIPT_PATH}" ]) then
while([ -h "${SCRIPT_PATH}" ]) do SCRIPT_PATH=`readlink "${SCRIPT_PATH}"`; done
fi
pushd . > /dev/null
cd `dirname ${SCRIPT_PATH}` > /dev/null
SCRIPT_PATH=`pwd`;
popd  > /dev/null

echo ""
echo "Setting up VPN paths {"

# path to mullvad
export MULLVAD_DIR=/Applications/MullvadVPN.app/Contents/Resources/mullvad

# path to expressvpn
export VPN_DIR=/Applications/ExpressVPN.app/Contents/MacOS/ExpressVPN


echo ""
echo "}"
echo "Done"