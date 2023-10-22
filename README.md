# Part C: Integration Testing
This repository is used for to accomodate the CI process of setting up an API along with its associated database. 

After the API and Database are up and running, the workflow runs a variety of CRUD tests against the API to assert full functionality.
The docker is then destroyed and cleaned-up .

## Github Actions

The file that contains all of the workflow's actions is located within the **.github/workflows** directory. The following steps are being dictated within the "ci.yml" file :


 - Checkout Repository - Fetch the source code from the repository
 - Set up Docker Compose - Initiates the docker containers
 - Delay for 5 seconds - A 5 seconds delay is implemented, to account for the containers' delay right after they are up
 - Run CRUD Tests - Newman CRUD tests are run against the API
 - Upload Artifacts - An html file is being  exported as an artifact (Can be accessed **after the test has finished running**)
 - Tear Down Docker Containers - Removes both the containers and any associated volumes, effectively cleaning up the environment created by the Docker Compose

## Tests

Within the "tests" directory, the newman (Postman) collection and environment files are present. These files contain the scripts used to test against the API. 