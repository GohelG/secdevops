# DevSecOps Infrastructure Installation Guide

This guide covers the systematic installation and setup of Docker, Trivy, MariaDB, Grafana, and Prometheus on Ubuntu/Debian-based systems.

---

## 1. Installation (Docker)

### Step 1.1: Remove Conflicting Packages
Ensure old or conflicting container runtimes are completely purged from the system before proceeding:
```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do 
  sudo apt-get remove -y \$pkg
done
```

### Step 1.2: Set Up Docker's Apt Repository
1. **Update system index and install prerequisites:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y ca-certificates curl
   ```

2. **Add Docker's official GPG key:**
   ```bash
   sudo install -m 0755 -d /etc/apt/keyrings
   sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
   sudo chmod a+r /etc/apt/keyrings/docker.asc
   ```

3. **Add the stable repository to your system sources:**
   ```bash
   echo \
     "deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
     \((. /etc/os-release && echo "\)VERSION_CODENAME") stable" | \
     sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

### Step 1.3: Install Docker Engine
Update your package index again and install the latest Docker components:
```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Step 1.4: Verify the Installation
Run the official test image using elevated privileges:
```bash
sudo docker run hello-world
```

### Step 1.5: Run Docker Without Sudo (Optional)
1. **Create the docker group and add your user:**
   ```bash
   sudo groupadd docker
   sudo usermod -aG docker \$USER
   ```

2. **Apply the new group membership changes:**
   ```bash
   newgrp docker
   ```

3. **Test running without sudo:**
   ```bash
   docker run hello-world
   ```

### Step 1.6: Manage Docker Services
Ensure both core container daemons are configured to launch automatically at startup:
```bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
sudo systemctl is-enabled docker
```

---

## 2. Installation (Trivy)

Trivy is a lightweight, highly accurate vulnerability scanner that requires zero configuration to start.

### Step 2.1: Install via Official APT Repository
1. **Install dependencies:**
   ```bash
   sudo apt-get install -y wget gnupg lsb-release
   ```

2. **Download and add the public GPG key:**
   ```bash
   wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
   ```

3. **Add the repository to your sources list:**
   ```bash
   echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee /etc/apt/sources.list.d/trivy.list
   ```

4. **Update the package list and install Trivy:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y trivy
   ```

5. **Verify the installation:**
   ```bash
   trivy --version
   ```

---

## 3. Installation (MariaDB)

Grafana requires an active, external relational database management backend like MariaDB or MySQL to handle targeted storage requirements smoothly.

### Step 3.1: Install Prerequisites
```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https curl software-properties-common
```

### Step 3.2: Set Up the Official MariaDB Repository
```bash
curl -LsS https://mariadb.com | sudo bash
```

### Step 3.3: Install MariaDB Server
```bash
sudo apt-get update
sudo apt-get install -y mariadb-server
```

### Step 3.4: Manage Database Services
```bash
sudo systemctl start mariadb
sudo systemctl enable mariadb
sudo systemctl status mariadb
```

### Step 3.5: Secure the MariaDB Installation
Execute the automated wizard to lock down server settings:
```bash
sudo mariadb-secure-installation
```

**Recommended responses during configuration prompts:**
* **Enter current password for root**: Press `Enter` (it is blank by default).
* **Switch to unix_socket authentication?**: Type `Y` and press `Enter`.
* **Change the root password?**: Type `Y` and enter a strong, custom root password.
* **Remove anonymous users?**: Type `Y`.
* **Disallow root login remotely?**: Type `Y`.
* **Remove test database and access to it?**: Type `Y`.
* **Reload privilege tables now?**: Type `Y`.

### Step 3.6: Verify Your Database Connection
```bash
sudo mariadb -u root -p
```

### Step 3.7: Provision a Database and User Account for Grafana
Run the following SQL statements inside your active database shell console session:
```sql
-- Create database
CREATE DATABASE grafana_db;

-- Create database user and password
CREATE USER 'grafana_db_user'@'localhost' IDENTIFIED BY 'password123';

-- Grant privileges 
GRANT ALL PRIVILEGES ON grafana_db.* TO 'grafana_db_user'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;

-- Verify grants 
SHOW GRANTS FOR 'grafana_db_user'@'localhost';
```

---

## 4. Installation (Grafana)

### Step 4.1: Install Dependencies 
```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https software-properties-common wget gnupg
```

### Step 4.2: Add the Official Grafana GPG Key
```bash
sudo mkdir -p /etc/apt/keyrings
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
```

### Step 4.3: Add the Grafana APT Repository (Standard OSS Edition)
```bash
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
```

### Step 4.4: Install Grafana OSS
```bash
sudo apt-get update
sudo apt-get install -y grafana
```

### Step 4.5: Start and Enable the Grafana Service
```bash
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
sudo systemctl status grafana-server
```

### Step 4.6: Initial UI Login Portal
Open your web browser and navigate to: `http://localhost:3000` (or your remote server's IP address).

* **Default Username**: `admin`
* **Default Password**: `admin`

---

## 5. Installation (Prometheus)

### Step 5.1: Install and Start Prometheus
```bash
sudo apt-get update
sudo apt-get install -y prometheus

sudo systemctl enable prometheus
sudo systemctl start prometheus
sudo systemctl status prometheus
```

### Step 5.2: Configure Scrape Targets
1. **Open the primary runtime configuration file:**
   ```bash
   sudo nano /etc/prometheus/prometheus.yml
   ```

2. **Verify or adjust the evaluation block target arrays:**
   ```yaml
   global:
     scrape_interval: 15s

   scrape_configs:
     - job_name: 'prometheus'
       static_configs:
         - targets: ['localhost:9090']
   ```

3. **Save changes and restart the daemon engine:**
   ```bash
   sudo systemctl restart prometheus
   ```

### Step 5.3: Connect Prometheus Inside Grafana Dashboard
1. **Open Grafana UI**: Visit `http://localhost:3000` and authentication log in.
2. **Navigate to Data Sources**: Click the **Connections** menu icon (left sidebar) $\rightarrow$ select **Data sources**.
3. **Add Data Source**: Click the **Add data source** button.
4. **Select Prometheus**: Choose **Prometheus** from the list of engine choices.
5. **Configure Connection Properties**: Enter `http://localhost:9090` inside the active HTTP URL reference field.
6. **Save and Test**: Scroll down to the bottom and click **Save & test**. You should see a green verification confirmation stating: *"Data source is working"*.

### Step 5.4: Import a Ready-Made Dashboard
1. Click the **Dashboards** icon in the sidebar navigation interface pane, click **New**, and choose **Import**.
2. Enter a Grafana community ID number (e.g., `3662` or `1860` for general node stats) or upload a custom JSON payload configuration template structure.
