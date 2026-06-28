name: "DevSecOps Container Security Pipeline"

on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main" ]

jobs:
  security-audit:
    name: Build & Scan Container
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Build Local Test Image
      run: |
        docker build -t my-app:${{ github.sha }} .

    # Sprint 1 & 2: Running Trivy vulnerability scan with strict exit code gates
    - name: Run Trivy Security Scan (FAIL on CRITICAL)
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'my-app:${{ github.sha }}'
        format: 'table'
        # Sprint 5: Uses .trivyignore to manage known, approved exceptions
        ignore-unfixed: true
        vuln-type: 'os,library'
        severity: 'HIGH,CRITICAL'
        # Exit code 1 forces the pipeline build to fail if critical issues are found
        exit-code: '1' 

    # Sprint 3: Generate detailed JSON file report if the build fails or passes
    - name: Generate Structured Vulnerability Report
      if: always()
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'my-app:${{ github.sha }}'
        format: 'json'
        output: 'vulnerability-report.json'

    # Sprint 3: Push real-time alert updates to engineering communication channels
    - name: Send Slack/Teams Notification on Failure
      if: failure()
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      run: |
        curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"*Security Gate Failure!* Container image `my-app:${{ github.sha }}` failed structural security validation scanning. High/Critical vulnerabilities detected. Check the pipeline logs immediately."}' \
        $SLACK_WEBHOOK_URL
