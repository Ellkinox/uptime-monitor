# Uptime Monitor

A small web application that shows whether websites are up, with their HTTP
code and response time.

**Live:** http://uptime-199494562.eu-west-3.elb.amazonaws.com

## How it works

```
Browser -> AWS Load Balancer -> frontend (nginx) -> backend (FastAPI)
```

- **frontend**: nginx serves the web page and forwards `/api/` calls to the backend.
- **backend**: a Python API that checks each website and keeps the result for 30 seconds.
- Both run as separate containers, on AWS ECS Fargate.
- Every push to `main` runs the tests, builds the images and deploys to AWS.

## Repository

| Path | Content |
|---|---|
| `backend/` | API, tests, Dockerfile |
| `frontend/` | Web page, nginx configuration, Dockerfile |
| `docker-compose.yml` | Run the application locally |
| `.github/workflows/ci-cd.yml` | CI/CD pipeline (test, build, deploy) |
| `infra/` | AWS infrastructure (Terraform) |

## Clone

```
git clone https://github.com/Ellkinox/uptime-monitor.git
cd uptime-monitor
```

## Run locally

Requirement: Docker.

```
docker compose up --build
```

Open http://localhost:8080. Stop with `Ctrl+C`, or `docker compose down`.

The list of websites is set with `SITES` in `docker-compose.yml`.

## Run the tests

```
docker run --rm -v "${PWD}:/src" -w /src python:3.12-slim sh -c "pip install -r backend/requirements.txt pytest httpx && pytest backend"
```

## Deploy

The infrastructure is created once with Terraform (requires the AWS CLI,
configured with `aws configure`):

```
cd infra
terraform init
terraform apply
```

After that, every push to `main` deploys automatically. The pipeline needs
four GitHub secrets (Settings > Secrets and variables > Actions):
`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`.

To remove everything: `terraform destroy` in `infra/`.

## Load test

Script `load-test.js` (k6): 20 virtual users call the API every second for
2 minutes.

```js
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "30s", target: 20 }, // go up to 20 users
    { duration: "1m", target: 20 },  // stay at 20 users
    { duration: "30s", target: 0 },  // go back down
  ],
};

export default function () {
  const response = http.get(`${__ENV.URL}/api/status`);
  check(response, { "status is 200": (r) => r.status === 200 });
  sleep(1);
}
```

Run it against the live application (PowerShell):

```
docker run --rm -v "${PWD}:/scripts" -e URL=http://uptime-199494562.eu-west-3.elb.amazonaws.com grafana/k6 run /scripts/load-test.js
```

To test with more backend containers:

```
cd infra
terraform apply -var backend_count=4
```

## What is missing / next improvements

- **Automate Terraform**: run `terraform plan` / `apply` in the pipeline, with the state stored in S3.
- **Autoscaling**: add or remove backend containers automatically based on CPU or traffic.
- **Monitoring and alerts**: a CloudWatch dashboard and an alarm when the site or a monitored website goes down.
- **HTTPS**: a domain name and a certificate (AWS ACM) on the load balancer.
- **Better frontend**: proper CSS, mobile layout, history and uptime percentage per website.
- **Safer deployments**: tag images with the commit id instead of `latest`, and use GitHub OIDC instead of AWS access keys.
