#!/bin/bash

if [ "${AUTHORIZED_KEYS}" != "**None**" ]; then
    echo "=> Found authorized keys"
    mkdir -p /home/mongo/.ssh
    chmod 700 /home/mongo/.ssh
    touch /home/mongo/.ssh/authorized_keys
    chmod 600 /home/mongo/.ssh/authorized_keys
    IFS=$'\n'
    arr=$(echo ${AUTHORIZED_KEYS} | tr "," "\n")
    for x in $arr
    do
        x=$(echo $x |sed -e 's/^ *//' -e 's/ *$//')
        cat /home/mongo/.ssh/authorized_keys | grep "$x" >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo "=> Adding public key to /home/mongo/.ssh/authorized_keys: $x"
            echo "command=\"/import.py \$SSH_ORIGINAL_COMMAND\",no-port-forwarding,no-x11-forwarding,no-agent-forwarding $x" >> /home/mongo/.ssh/authorized_keys
        fi
    done
fi

exec /usr/sbin/sshd -D

