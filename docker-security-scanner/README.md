## 🐳 Docker Security Scanner
An automated vulnerability assessment environment using Trivy to scan, filter, and audit Docker images for production readiness.

## 📁 Folder Structure

```text
docker-security-scanner/
├── config/          # Scanner configurations (e.g., .trivyignore)
├── dockerfiles/     # Application Dockerfiles
├── reports/         # Scan outputs (JSON, HTML, TXT)
└── scripts/         # Automation scripts for CI/CD pipelines
```

---

## 🚀 Getting Started

### 1. Repository Setup
Initialize the structured directory to organize your Dockerfiles, scan configurations, and audit reports:

```bash
mkdir docker-security-scanner && cd docker-security-scanner
mkdir -p dockerfiles config reports scripts
touch README.md
```

### 2. Install & Configure Trivy
Trivy is a lightweight, zero-configuration vulnerability scanner for container images.

#### Ubuntu/Debian Installation
```bash
sudo apt-get update && sudo apt-get install -y wget apt-transport-https gnupg lsb-release

# Add Trivy repository key
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null

# Add repository source list (using 'generic' ensures compatibility across Ubuntu releases)
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee /etc/apt/sources.list.d/trivy.list

# Update packages and install
sudo apt-get update && sudo apt-get install -y trivy
```

---

## 🔍 Running Vulnerability Scans
This setup compares a historically vulnerable base image (`python:3.8-slim`) against a hardened, minimal base image (`alpine:latest`).

### Step 1: Pull Sample Images
```bash
docker pull python:3.8-slim
docker pull alpine:latest
```

### Step 2: Run a Standard Scan
Execute a basic terminal-based analysis of the target image:

```bash
trivy image python:3.8-slim
```

### Step 3: Filter by Severity & Save Report
Isolate high-risk vulnerabilities and generate a structured text report inside the `reports/` directory:

```bash
trivy image --severity HIGH,CRITICAL --format table --output reports/python_scan.txt python:3.8-slim
```

### Step 4: Scan the Secure Baseline
Verify the attack surface reduction by scanning the minimal Alpine image:

```bash
trivy image alpine:latest
```

---

## 📊 Generating HTML Reports

### 1. Download the official Aqua Security template
```bash
wget https://githubusercontent.com
```

### 2. Run the scan using the downloaded template
The `@` prefix before the template file name is mandatory for Trivy to locate the file properly.

```bash
trivy image --format template --template "@html.tpl" -o reports/report.html ubuntu:latest
```

---

## 📊 Understanding Scan Logs
When reviewing terminal output or generated files (like `reports/python_scan.txt`), Trivy structures logs into four core metrics:

| Column Header | Purpose | Example |
|---|---|---|
| **Library / Total** | The OS package or application dependency containing the flaw. | `openssl`, `glibc` |
| **Vulnerability ID** | The unique CVE identifier pointing to patch details. | `CVE-2023-XXXX` |
| **Severity** | Risk ranking used to prioritize remediation workflows. | `HIGH`, `CRITICAL` |
| **Installed vs Fixed** | The current package version vs the minimum required secure version. | `1.1.1t-r0 -> 1.1.1u-r0` |