#!/bin/bash
# title         :write_registers_tcp.sh
# description   :Write Modbus registers via TCP based on register JSON
# author        :brainelectronics
# date          :20221203
# version       :0.1.1
# usage         :sh write_registers_tcp.sh \
#                192.168.178.69 \
#                set-example.json \
#                502
#                Register file and modbus port are optional
# notes         :Install python3 and its requirements file to use this script.
# bash_version  :3.2.53(1)-release
#=============================================================================

connection_address=$1
register_file_path=$2
modbus_port=$3

if [[ -z "$register_file_path" ]]; then
    register_file_path=../registers/set-example.json
    echo "No register file given, using default at $register_file_path"
fi

if [[ -z "$modbus_port" ]]; then
    modbus_port=255
    echo "No modbus unit given, using default $modbus_port"
fi

echo "Write registers defined in $register_file_path via TCP from $connection_address"

python3 ../modules/write_device_info_registers.py \
--file=$register_file_path \
--connection=tcp \
--address=$connection_address \
--port=$modbus_port \
--print \
--pretty \
--debug \
--verbose=3
