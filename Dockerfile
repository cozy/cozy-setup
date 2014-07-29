FROM ubuntu:trusty
MAINTAINER Michiel de Jong
RUN echo "deb http://archive.ubuntu.com/ubuntu precise universe" >> /etc/apt/sources.list
RUN apt-get -y update
RUN apt-get install -y python python-pip python-dev software-properties-common
RUN pip install fabric fabtools
RUN apt-get install -y wget
RUN wget https://raw.githubusercontent.com/cozy/cozy-setup/master/fabfile.py
RUN apt-get install -y openssh-server
RUN useradd sudoer
RUN echo "sudoer	ALL=(ALL:ALL) ALL" >> /etc/sudoers
RUN echo "sudoer:hi" | chpasswd
RUN mkdir /home/sudoer
RUN chown sudoer /home/sudoer
RUN echo "env={'password': 'hi'}" >> ./fabfile2.py
RUN cat ./fabfile.py >> ./fabfile2.py
RUN /etc/init.d/ssh start && fab -H sudoer@localhost install -f ./fabfile2.py --password=hi
RUN userdel sudoer

EXPOSE 9104
CMD supervisord -n -c /etc/supervisor/supervisord.conf
