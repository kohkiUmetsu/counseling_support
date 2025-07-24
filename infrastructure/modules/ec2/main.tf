resource "aws_security_group" "bastion" {
  name_prefix = "${var.project_name}-${var.environment}-bastion-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-bastion-sg"
    Environment = var.environment
  }
}

# Get the latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

resource "aws_instance" "bastion" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.key_pair_name
  
  subnet_id              = var.public_subnet_ids[0]
  vpc_security_group_ids = [aws_security_group.bastion.id]
  
  associate_public_ip_address = true

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y postgresql15
    
    # Install psql client for PostgreSQL
    amazon-linux-extras enable postgresql15
    yum install -y postgresql15
    
    # Create a connection script
    cat << 'SCRIPT' > /home/ec2-user/connect-db.sh
#!/bin/bash
echo "PostgreSQL Connection Helper"
echo "Main DB: psql -h ${var.db_endpoint} -U ${var.db_username} -d counseling_db"
echo "Vector DB: psql -h ${var.vector_db_endpoint} -U ${var.vector_db_username} -d counseling_vector_db"
echo ""
echo "Select database to connect:"
echo "1) Main Database"
echo "2) Vector Database"
read -p "Enter choice (1-2): " choice

case $choice in
  1)
    psql -h ${var.db_endpoint} -U ${var.db_username} -d counseling_db
    ;;
  2)
    psql -h ${var.vector_db_endpoint} -U ${var.vector_db_username} -d counseling_vector_db
    ;;
  *)
    echo "Invalid choice"
    ;;
esac
SCRIPT
    
    chmod +x /home/ec2-user/connect-db.sh
    chown ec2-user:ec2-user /home/ec2-user/connect-db.sh
  EOF

  tags = {
    Name        = "${var.project_name}-${var.environment}-bastion"
    Environment = var.environment
    Role        = "Bastion"
  }
}