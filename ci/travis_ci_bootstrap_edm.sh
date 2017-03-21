EDM_VERSION=1.5.0
EDM_VERSION_MAJOR=1.5
if [[ ${TRAVIS_OS_NAME} == "osx" ]]
then
    # download and install EDM
    FILENAME=edm_${EDM_VERSION}.pkg
    wget https://package-data.enthought.com/edm/osx_x86_64/${EDM_VERSION_MAJOR}/$FILENAME
    sudo installer -pkg $FILENAME -target /
else
    # download and install EDM
    FILENAME=edm_${EDM_VERSION}_linux_x86_64.sh
    wget https://package-data.enthought.com/edm/rh5_x86_64/${EDM_VERSION_MAJOR}/$FILENAME
    chmod u+x $FILENAME
    ./$FILENAME -b -p ~
    export PATH="~/bin:${PATH}"
fi

# install pip and invoke into default EDM environment
edm install -y pip invoke coverage
