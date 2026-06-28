===============================================================================================================================================================================
### Installation (Docker) ###
===============================================================================================================================================================================

## Step 1.1: Uninstall Conflicting Packages
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove -y $pkg; done

## Step 1.2: Set Up Docker's Apt Repository
# 1. Update system index and install prerequisites:
sudo apt-get update
sudo apt-get install -y ca-certificates curl

# 2. Add Docker's official GPG key:
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://docker.com -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# 3. Add the repository to your system sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://github.com \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

## Step 1.3: Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

## Step 1.4: Verify the Installation
sudo docker run hello-world

# Run Docker Without Sudo (Optional)
# 1. Create the docker group and add your user
sudo groupadd docker
sudo usermod -aG docker $USER

# 2. Apply the new group membership changes
newgrp docker

# 3. Test running without sudo
docker run hello-world

## Step 1.5: Start/Enable Docker Services and Verify
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
sudo systemctl is-enabled docker

===============================================================================================================================================================================
### Installation (Trivy) ###
===============================================================================================================================================================================

## Install & Configure Trivy (Trivy is a lightweight, highly accurate vulnerability scanner that requires zero configuration to start.) 
## Step 1.1: Install via Official APT Repository
# 1. Install dependencies
sudo apt-get install -y wget gnupg lsb-release

# 2. Download and add the public GPG key
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null

# 3. Add the repository to your sources list
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee -a /etc/apt/sources.list.d/trivy.list

# 4. Update the package list
sudo apt-get update

# 5. Install Trivy
sudo apt-get install -y trivy

# 6. Verify the Installation
trivy --version

===============================================================================================================================================================================
### Installation (MariaDB) ###
===============================================================================================================================================================================

## BBefore installing Grafana, We need to install MySQL or MariaDB and have it running properly.
# Step 1: Install Prerequisites
sudo apt-get update
sudo apt-get install -y apt-transport-https curl software-properties-common

# Step 2: Set Up the Official MariaDB Repository
curl -LsS https://mariadb.com | sudo bash

# Step 3: Install MariaDB Server
sudo apt-get update
sudo apt-get install -y mariadb-server

# Step 4: Start/Enable Database Services and Verify
sudo systemctl start mariadb
sudo systemctl enable mariadb
sudo systemctl status mariadb

# Step 5: Secure the MariaDB Installation (Crucial)
sudo mariadb-secure-installation

# During the prompt, the system will ask we a series of questions. It is highly recommended to answer as follows:
* Enter current password for root: Press Enter (it is blank by default).
* Switch to unix_socket authentication? Type Y and press Enter.
* Change the root password? Type Y and enter a strong, custom root password.
* Remove anonymous users? Type Y.
* Disallow root login remotely? Type Y.
* Remove test database and access to it? Type Y.
* Reload privilege tables now? Type Y.

# Step 6: Test Your Database Connection
sudo mariadb -u root -p

# Step 7: Creating a new database and user account with specific privileges for Grafana.
# Create database
CREATE DATABASE grafana_db;

# Create database user and password
CREATE USER 'grafana_db_user'@'localhost' IDENTIFIED BY 'password123';

# Grant privileges 
GRANT ALL PRIVILEGES ON grafana_db.* TO 'grafana_db_user'@'localhost';

# Flush privileges
FLUSH PRIVILEGES;

# Verify grants 
SHOW GRANTS FOR 'grafana_db_user'@'localhost';

===============================================================================================================================================================================
### Installation (Grafana) ###
===============================================================================================================================================================================

## Step 1.1: Install dependencies 
sudo apt-get update
sudo apt-get install -y apt-transport-https software-properties-common wget gnupg

## Step 2.1: Add the Official Grafana GPG Key:
sudo mkdir -p /etc/apt/keyrings
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null

## Step 3.1: Add the Grafana APT Repository(For the standard Open Source (OSS) Edition):
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

## Step 4.1: Install Grafana
sudo apt-get update
sudo apt-get install -y grafana

## Step 4.1: Start and Enable the Grafana Service & Verify Grafana Service is running
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
sudo systemctl status grafana-server

## Step 6.1: Open a browser window and navigate to http://localhost:3000 (or replace localhost with your remote server's IP address).
Log in using the system default credentials:
Username: admin
Password: admin

===============================================================================================================================================================================
### Installation (Prometheus) ###
===============================================================================================================================================================================

## Step 1: Install and Start Prometheus
# 1. Install Prometheus
sudo apt-get update
sudo apt-get install -y prometheus

# 2. Enable and verify the service
sudo systemctl enable prometheus
sudo systemctl start prometheus
sudo systemctl status prometheus

## Step 2: Configure Scrape Targets
# 1. Open the configuration file
sudo nano /etc/prometheus/prometheus.yml

# 2. Verify or add a scrape job
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

# 3. Save and restart Prometheus
sudo systemctl restart prometheus

# Step 3: Connect Prometheus inside Grafana
1. Open Grafana: Go to http://localhost:3000 in your web browser and log in.
2. Navigate to Data Sources: Click the Connections icon (or gear icon) in the left sidebar and select Data sources.
3. Add Data Source: Click the Add data source button.
4. Select Prometheus: Choose Prometheus from the list of available source types.
5. Configure the URL: In the Connection or HTTP URL field, enter exactly. (http://localhost:9090)
6. Save and Test: Scroll down to the bottom of the page and click Save & test.You should see a green success message stating: "Data source is working".

# Step 4: Import a Ready-Made Dashboard
1. In Grafana's left sidebar, click the Plus (+) icon or Dashboards menu, and select Import.
2. Type 3662 (the official Prometheus Mixin dashboard ID) into the Import via grafana.com text box.
3. Click Load.
4. Select your Prometheus data source from the dropdown menu at the bottom.
5. Click Import.