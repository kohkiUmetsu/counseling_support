#!/bin/bash

# Bastion Host Database Connection Script
# Usage: ./connect-bastion.sh [option]
# Options: ssh, db-main, db-vector, help

set -e

# Configuration - これらの値はTerraform outputから取得してください
BASTION_IP="${BASTION_IP:-}"
KEY_PATH="${KEY_PATH:-~/.ssh/counseling-support-dev-key.pem}"
DB_USERNAME="${DB_USERNAME:-counseling_user}"
VECTOR_DB_USERNAME="${VECTOR_DB_USERNAME:-vector_user}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_usage() {
    echo "Counseling Support - Bastion Host Connection Helper"
    echo ""
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  ssh         - SSH to bastion host"
    echo "  db-main     - Connect to main PostgreSQL database"
    echo "  db-vector   - Connect to vector PostgreSQL database"
    echo "  setup       - Initial setup and configuration"
    echo "  help        - Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  BASTION_IP           - Public IP of bastion host (required)"
    echo "  KEY_PATH             - Path to SSH private key (default: ~/.ssh/counseling-support-dev-key.pem)"
    echo "  DB_USERNAME          - Main database username (default: counseling_user)"
    echo "  VECTOR_DB_USERNAME   - Vector database username (default: vector_user)"
    echo ""
    echo "Examples:"
    echo "  BASTION_IP=1.2.3.4 $0 ssh"
    echo "  BASTION_IP=1.2.3.4 $0 db-main"
}

check_requirements() {
    if [ -z "$BASTION_IP" ]; then
        echo -e "${RED}Error: BASTION_IP environment variable is required${NC}"
        echo "Get the bastion IP from: terraform output bastion_public_ip"
        exit 1
    fi
    
    if [ ! -f "$KEY_PATH" ]; then
        echo -e "${RED}Error: SSH key file not found at $KEY_PATH${NC}"
        echo "Make sure you have the correct SSH key file."
        exit 1
    fi
    
    # Check SSH key permissions
    if [ "$(stat -f %A "$KEY_PATH" 2>/dev/null || stat -c %a "$KEY_PATH" 2>/dev/null)" != "400" ]; then
        echo -e "${YELLOW}Warning: SSH key permissions should be 400${NC}"
        echo "Run: chmod 400 $KEY_PATH"
    fi
}

ssh_to_bastion() {
    echo -e "${GREEN}Connecting to bastion host...${NC}"
    ssh -i "$KEY_PATH" ec2-user@"$BASTION_IP"
}

connect_main_db() {
    echo -e "${GREEN}Connecting to main PostgreSQL database...${NC}"
    ssh -i "$KEY_PATH" ec2-user@"$BASTION_IP" -t "
        echo 'Connecting to main database...'
        ./connect-db.sh
    "
}

connect_vector_db() {
    echo -e "${GREEN}Connecting to vector PostgreSQL database...${NC}"
    ssh -i "$KEY_PATH" ec2-user@"$BASTION_IP" -t "
        echo 'Connecting to vector database...'
        echo '2' | ./connect-db.sh
    "
}

setup_environment() {
    echo -e "${GREEN}Setting up connection environment...${NC}"
    
    echo "1. Get bastion IP from Terraform:"
    echo "   cd infrastructure/environments/dev"
    echo "   terraform output bastion_public_ip"
    echo ""
    
    echo "2. Ensure SSH key exists:"
    echo "   ls -la $KEY_PATH"
    echo ""
    
    echo "3. Test connection:"
    echo "   BASTION_IP=<your-bastion-ip> $0 ssh"
    echo ""
    
    echo "4. Connect to databases:"
    echo "   BASTION_IP=<your-bastion-ip> $0 db-main"
    echo "   BASTION_IP=<your-bastion-ip> $0 db-vector"
}

# Main script logic
case "${1:-help}" in
    "ssh")
        check_requirements
        ssh_to_bastion
        ;;
    "db-main")
        check_requirements
        connect_main_db
        ;;
    "db-vector")
        check_requirements
        connect_vector_db
        ;;
    "setup")
        setup_environment
        ;;
    "help"|*)
        print_usage
        ;;
esac