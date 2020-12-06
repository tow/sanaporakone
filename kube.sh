#!/bin/bash
set -euf -o pipefail

VERSION=0.1.5

# create a docker image and import it to local registry
sudo docker build -t spk:"$VERSION" . && sudo docker save spk:"$VERSION" | microk8s ctr image import -

template=`cat deployment.yaml.template | sed "s/{{VERSION}}/$VERSION/g"`

# redeploy
echo "$template" | microk8s kubectl apply -f -

# re-expost
microk8s kubectl apply -f service.yaml
