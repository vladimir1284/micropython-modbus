#!/bin/bash
# title         :read_registers_rtu.sh
# description   :Read Modbus registers via Serial RTU based on register JSON
# author        :brainelectronics
# date          :20221203
# version       :0.1.1
# usage         :sh read_registers_rtu.sh \
#                /dev/tty.SLAB_USBtoUART \
#                example.json \
#                10
#                Register file and modbus unit are optional
# notes         :Install python3 and its requirements file to use this script.
# bash_version  :3.2.53(1)-release
#=============================================================================

connection_port=$1
register_file_path=$2
modbus_unit=$3

if [[ -z "$register_file_path" ]]; then
    register_file_path=../registers/example.json
    echo "No register file given, using default at $register_file_path"
fi

if [[ -z "$modbus_unit" ]]; then
    modbus_unit=10
    echo "No modbus unit given, using default $modbus_unit"
fi

echo "Read registers defined in $register_file_path via RS485 on $connection_port @ $modbus_unit"

python3 ../modules/read_device_info_registers.py \
--file=$register_file_path \
--connection=rtu \
--address=$connection_port \
--unit=$modbus_unit \
--baudrate=9600 \
--print \
--pretty \
--debug \
--verbose=3
