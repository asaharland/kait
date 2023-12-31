# Probe issue

This example shows a failing Service due to an incorrectly configured readiness probe that is pointing to the incorrect port

Run the following commands to setup your environment:
```bash
kubectl create namespace hosting
kubectl apply -f manifests/
```

Run the following `kait` command to start the debugging process:
```bash
kait debug "A Service in the hosting Namespace is not responding to requests." --output-dir="."
```
