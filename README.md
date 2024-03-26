# Disconnected workload identity

1. Create an RSA keypair: `./1-create-key.py keys/gk`
2. Generate identity provider's JWKS: `./2-idp-jwks.py keys/gk`
3. Update pool provider in terraform with correct JWKs, and apply
4. Generate a token (once) using the private key: `./3-sign-token.py keys/gk > token`. The signed token contains a claims with information of the current process using opentelemetry resource detector (for the fun).
Here, the identity provider and the workload is the same, the workload generates an identity for itself.
5. Generate a credential file, no request to api, a static file without credentials:
```
PROJECT_ID="..." PROJECT_NUMBER="..." POOL_ID="pool" PROVIDER_ID="provider" gcloud iam workload-identity-pools create-cred-config  \
  projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/providers/$PROVIDER_ID \
  --service-account=wi-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --output-file=sts-creds.json  \
  --credential-source-file=$(pwd)/token
```
6. Test setup: `gcloud auth login --cred-file=sts-creds.json && gcloud auth list && gcloud auth print-access-token && gcloud pubsub topics list --project $PROJECT_ID`

# JwtFS

It provides a filesystem, at it's mountpoint there's a single `jwt` file.
The filesystem generates a signed token with a claim including information of the caller.
It uses `fuse_get_context` to get the PID of the caller, and grabs inforamtions of this process.
To use it:

1. mount the filesytem `python3 JwtFs.py /mnt/jwtfs /path/to/private.pem`
2. generate the same credential config as the previous step, with the credential-source-file in the mounted filesystem:
```
PROJECT_ID="..." PROJECT_NUMBER="..." POOL_ID="pool" PROVIDER_ID="provider" gcloud iam workload-identity-pools create-cred-config  \
  projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/providers/$PROVIDER_ID \
  --service-account=wi-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --output-file=sts-creds.json  \
  --credential-source-file=/mnt/jwtfs/jwt
```
3. Test setup: `gcloud auth login --cred-file=sts-creds.json && gcloud auth list && gcloud auth print-access-token && gcloud pubsub topics list --project $PROJECT_ID`