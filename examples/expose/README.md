# Expose issue

Run the following commands to setup your environment:

```bash
kubectl create namespace temp
kubectl apply -f manifests/
```

Run the following `kait` command to start the debugging process:
```bash
kait debug "The site deployment in the temp namespace is supposed to be exposed to clients outside of the Kubernetes cluster by the sitelb service. However, requests sent to the service do not reach the deployment's pods. Resolve the service configuration issue so the requests sent to the service do reach the deployment's pods." --output-dir="."
```
