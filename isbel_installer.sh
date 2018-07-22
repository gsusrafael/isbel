#!/bin/bash
#
# ISBEL installer, version 1.0
#  Author - Jesus Sanchez
#  Usage: see usage() function, below

##
# Constants Section
##

IVERSION="1.0"

IEXEC="SocketDaemon.pyc utils/register_pyc.py utils/runcobol.sh"
ICONF="isbel.xml isbel.dtd"
IFILES="daemon.pyc
ProcessLogger.pyc
SocketService.pyc
XmlConfigParser.pyc
XmlValidateDTD.pyc"


Usage() {
    echo "iinstaller - an installer for ISBEL integrator"
    echo "Usage: iinstaller [-p {prefix}] [-v] [-V] [-h]"
    echo "  -p   install the files using the {prefix} path"
    echo "  -v   turns on the verbose debug execution mode"
    echo "  -V   shows the program version and exit"
    echo "  -h   shows this usage message"
}

# Routines declaration

SetPrefix() {
    if [ $# -eq 1 ];
    then
        echo "$1"
    else
        echo "/usr/local"
    fi
    return $?
}

ShowVersion() {
    echo "Version [$IVERSION]"
    return 0
}

Iinstall() {
    if [ $# -eq 1 ];
    then
        if SetPrefix $1 &> /dev/null;
        then
           PREFIX=$(SetPrefix $1)
        else
            echo "error en el proceso de instalacion..."
            echo "abortando."
            return 2
        fi

        echo "Preparando para instalar bajo el directorio $1";
        echo 
        echo "presione cualquier tecla para continuar..."
        read -n 1
            
        echo "Copiando librerias..."
        for ifile in $IFILE;
        do
            cp -v $ifile $PREFIX/lib/python2.6/site-packages/
        done

        echo "Copiando ejecutables..."
        for ifile in $IEXEC;
        do
            if [ "$ifile" = "utils/register_pyc.py" ];
            then
                cp -v $ifile /usr/local/sbin
                chmod -v 755 /usr/local/sbin/$(basename $ifile)
            else
                cp -v $ifile /usr/local/bin/
                chmod -v 755 /usr/local/bin/$(basename $ifile)
            fi
        done

        echo "Copiando archivos de configuracion..."
        for ifile in $ICONF;
        do
            cp -v $ifile /etc
        done
        return $?
    else
        Usage
        return $?
    fi
}

# Main running block
while getopts "p:Vvh" arg;
do
    case $arg in
        p)
            arg_prefix=${OPTARG[0]}
        ;;
        V)
            ShowVersion
            exit $?
        ;;
        v)
            set -x
            set -v
        ;;
        h|*)
            Usage
            exit 1
        ;;
    esac
done

shift $(($OPTIND - 1))

if [ -z "$arg_prefix" ];
then
    echo "Iinstall /usr"
else
    echo "Iinstall $arg_prefix"
fi

exit $?
