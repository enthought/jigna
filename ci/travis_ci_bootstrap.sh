# Install edm and geckodriver for selenium firefox

EDM_VERSION=1.5.0
EDM_VERSION_MAJOR=1.5
cd $HOME
if [[ ${TRAVIS_OS_NAME} == "osx" ]]
then
    # download and install EDM
    FILENAME=edm_${EDM_VERSION}.pkg
    wget https://package-data.enthought.com/edm/osx_x86_64/${EDM_VERSION_MAJOR}/$FILENAME
    sudo installer -pkg $FILENAME -target /
    wget https://github.com/mozilla/geckodriver/releases/download/v0.15.0/geckodriver-v0.15.0-macos.tar.gz
else
    # download and install EDM
    FILENAME=edm_${EDM_VERSION}_linux_x86_64.sh
    wget https://package-data.enthought.com/edm/rh5_x86_64/${EDM_VERSION_MAJOR}/$FILENAME
    chmod u+x $FILENAME
    ./$FILENAME -b -p ~
    wget https://github.com/mozilla/geckodriver/releases/download/v0.15.0/geckodriver-v0.15.0-linux64.tar.gz
fi

mkdir -p ~/bin
cd ~/bin
tar xvf ~/geckodriver-*.tar.gz
