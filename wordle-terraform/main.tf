provider "aws" {
  region = "us-east-1"
}

# Ubuntu 22.04 AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# Key Pair (using docker-key.pub)
resource "aws_key_pair" "wordle_key" {
  key_name   = "wordle-key"
  public_key = file("docker-key.pub")
}

# Security Group
resource "aws_security_group" "wordle_sg" {
  name        = "wordle-sg"
  description = "Allow SSH and HTTP"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
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
resource "aws_instance" "wordle_instance" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.medium"
  key_name               = aws_key_pair.wordle_key.key_name
  vpc_security_group_ids = [aws_security_group.wordle_sg.id]
  user_data              = file("user_data.sh")

  tags = {
    Name = "Wordle-Docker-Assignment"
  }
}