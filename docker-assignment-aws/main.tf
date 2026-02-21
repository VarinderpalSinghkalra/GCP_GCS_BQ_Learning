provider "aws" {
  region = var.region
}

# Get Latest Ubuntu 22.04 AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# Key Pair
resource "aws_key_pair" "docker_key" {
  key_name   = "docker-assignment-key"
  public_key = file(var.public_key_path)
}

# Security Group
resource "aws_security_group" "docker_sg" {
  name = "docker-assignment-sg"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "docker_instance" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.docker_key.key_name
  vpc_security_group_ids = [aws_security_group.docker_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              set -e
              apt update -y
              apt install -y wget

              # Install Docker (Assignment Script)
              wget https://d6opu47qoi4ee.cloudfront.net/dockerinstallscript.sh
              bash dockerinstallscript.sh

              usermod -aG docker ubuntu
              chown ubuntu:ubuntu -R /opt
              cd /opt

              # Busybox test
              docker run --rm busybox:latest /bin/echo "Hello world"

              # Download Dockerfile
              wget https://d6opu47qoi4ee.cloudfront.net/project-container/Dockerfile

              # Build Image
              docker build -t helloworld .

              # Run Container (Tomcat 8080 -> 80)
              docker run -d -p 80:8080 helloworld
              EOF

  tags = {
    Name = "Docker-Assignment-Exact"
  }
}