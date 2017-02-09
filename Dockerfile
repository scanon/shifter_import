FROM centos:7

RUN yum -y install openssh-server mongo-client

RUN rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-7.noarch.rpm && yum -y install python python-pip

RUN useradd -m mongo && \
    mkdir /home/mongo/.ssh && \
    chown mongo /home/mongo/.ssh && \
    chmod 600 /home/mongo/.ssh && \
    echo  'command="/import.py $SSH_ORIGINAL_COMMAND",no-port-forwarding,no-x11-forwarding,no-agent-forwarding ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA5nqz8jf9PL4NBwfx0j/n8PR9G8MW8YqmFNk7Qnij8najEWb+hjzUVAhNMuAhVGknzSQKAaeuxehuoGj/qD6zINd7V9i8Yl74oh9ekk4uvDZRUmaEGI6xRtUocGQ7VnloZRcmXbHHJGnTVbZf8jmOQKDzZvC3v9kmFBImUpjdUm6ZoEM8wUDXUX/l6St8+VSLQ54achVya/Lzy3KMBaFghBtJ2s15cwKphfBTYAT7LR0++1s1GTx2Pz2KwoBfHEI+HP/W+4MSoFE57+r1103+7ONv7Uu7HYRxbdU/wN+Fz6X7EUGVD06hhC8YQ1GUzoUlH/K7kJQ7lEVZeRaJUorjdw==' > /home/mongo/.ssh/authorized_keys && \
    chmod 600 /home/mongo/.ssh/authorized_keys  && \
    chown mongo /home/mongo/.ssh/authorized_keys 

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD . /

RUN \
    mkdir /var/run/sshd && \
    echo "   StrictHostKeyChecking no" >> /etc/ssh/ssh_config  && \
    rm -f /etc/ssh/ssh_host_ecdsa_key /etc/ssh/ssh_host_rsa_key && \
    ssh-keygen -q -N "" -t dsa -f /etc/ssh/ssh_host_ecdsa_key && \
    ssh-keygen -q -N "" -t rsa -f /etc/ssh/ssh_host_rsa_key && \
    sed -i "s/#UsePrivilegeSeparation.*/UsePrivilegeSeparation no/g" /etc/ssh/sshd_config

EXPOSE 22


CMD [ "/run.sh" ]
