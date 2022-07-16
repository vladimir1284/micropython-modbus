#!/bin/bash
# title         :read_registers_tcp.sh
# description   :Read Modbus registers via TCP based on register JSON
# author        :brainelectronics
# date          :20220708
# version       :0.1.0
# usage         :sh read_registers_tcp.sh \
#                192.168.178.188 \
#                example.json \
#                502
#                Register file and modbus port are optional
# notes         :Install python3 and its requirements file to use this script.
# bash_version  :3.2.53(1)-release
#=============================================================================

connection_address=$1
register_file_path=$2
modbus_port=$3

if [[ -z "$register_file_path" ]]; then
    register_file_path=example.json
    echo "No register file given, using default at $register_file_path"
fi

if [[ -z "$modbus_port" ]]; then
    modbus_port=255
    echo "No modbus unit given, using default $modbus_port"
fi

echo "Read registers defined in $register_file_path via TCP from $connection_address"

python3 ../modules/read_device_info_registers.py \
--file=$register_file_path \
--connection=tcp \
--address=$connection_address \
--port=$modbus_port \
--print \
--pretty \
--debug \
--verbose=3
