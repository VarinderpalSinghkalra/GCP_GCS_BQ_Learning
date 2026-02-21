#!/bin/bash
apt update -y
apt install -y docker.io unzip
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

cd /opt
wget https://d6opu47qoi4ee.cloudfront.net/reactle.zip
unzip reactle.zip
docker build -t reactle .
docker run -d -p 80:80 reactle