#!/bin/sh

# ©2023 Zebra Technologies Corp. and/or its affiliates.
#version=v1.0.0-6

# Please assign the location of "Command Line Utility" binary application.
clu_binary_location=""

# Condition to check the binary path of the CLU binary if the user does not set the $command_line_binary_location
if [ -z "$clu_binary_location" ]
then 
    if [ -e CLU ] # Check if a CLU binary exist in the current directory
    then
        clu_binary=./CLU
    else
        CLU 2> NULL # Execute the command and check if it is available in the $PATH environment 
        if [ $? -eq 0 ]
        then 
            clu_binary=CLU # Run the CLU command if it is available in the $PATH environment variable locations
        else 
            echo "CLU binary not available. Exiting..."
            exit 1 # Exit the application if CLU binary not available
        fi
    fi
else
    clu_binary=$clu_binary_location/CLU
fi

# Execute the CLU command with provided arguments
if [ "$#" -eq 3 ]; then
    $clu_binary "$1" "$2" "$3"
    
elif [ "$#" -eq 1 ]; then
    $clu_binary "$1"

elif [ "$#" -eq 4 ]; then
    $clu_binary "$1" "$2" "$3" "$4"

elif [ "$#" -eq 5 ]; then
     $clu_binary "$1" "$2" "$3" "$4" "$5"

elif [ "$#" -eq 0 ]; then
     $clu_binary
fi

# Catch the 'status' return value 
if [ $? -eq 0 ];then
    echo "Executed Command Successful"
else    
    echo "Executed Command Unsuccessful"
fi





