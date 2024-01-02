# Welcome to my Recipes REST API
This project is fully functioning REST API which allows users to create, read, update and delete recipes. Additionally, users may create and add tags to recipes, and filter recipes by ingredients and/or tags. The project features a full user account creation and authentication system, with passwords stored as a SHA-256 hash in the database.

Access the deployed project here: http://ec2-51-20-1-67.eu-north-1.compute.amazonaws.com/api/docs/
<br><br>
## Features
- Users can create and sign in/out of their account using an e-mail address and securely stored password. Recipes, tags, and ingredients created by a user are assigned to their user ID.
- Users can create (POST), retreive (GET), full update (PUT), partial update (PATCH) or delete (DELETE) recipes, tags or ingredients using the Swagger UI, by submitting a valid request to any of the API endpoints, which requires filling form fields or submitting a valid JSON body. The UI provides hints and feedback to assist the user in making a valid request to any of the endpoints.
- Users have the option to retreive a filtered list of recipes by passing in a comma-seperated list of ingredient and/or tag IDs.
<br><br>


## Architecture Overview
<br>
### Deployment
The project is containerized using Docker and deployed on a single AWS EC2 VPS.
![image](https://github.com/daniel-maxwell/RESTful-Recipes-API/assets/66431847/c0a0a3ad-dc80-4082-b751-2bbbc5d6160d)
<br>
### Basic Components
The Django app is executed using a uWSGI web server gateway interface. Persistant data (sqlite data, static files) are stored in Docker volumes. A reverse proxy Nginx server handles requests in to the application.
![Overview](https://github.com/daniel-maxwell/RESTful-Recipes-API/assets/66431847/a59a2f01-3f0d-49bd-a974-d70ef2262c21)
<br>
### Docker Compose Setup
Depending on ther URL of the request, the Nginx reverse proxy service handles things differently. Static files such as CSS, JavaScript and front-end elements are served directly from the static data volume, increasing efficiency and loading times. All other requests are routed in to the uWSGI server that runs the application.
![Docker Compose setup](https://github.com/daniel-maxwell/RESTful-Recipes-API/assets/66431847/b929ed47-590b-4a65-9a36-afb42390eb25)
<br><br>


## Technologies, Languages and Workflows
- The application was created using Django and Django REST Framework, utilizes drf-spectacular for OPENAPI schema generation and runs inside a uWSGI server.
- The database used is Sqlite 3, with an intention to migrate over to Postgres in the future.
- The project is containerized using Docker, and uses an Nginx reverse proxy to handle requests between the client(s), app, and static data volumes.
- The project was created using the Test-Driven-Development software design philosophy, which is realised with an extensive unit testing suite, flake8 linter to enforce PEP-8 conformity, and the use of Github Actions to create a CI/CD pipeline.
<br><br><br>

Author
======
Made with ❤ by Daniel White | [Portfolio](https://daniel-maxwell.github.io/Portfolio/) | [LinkedIn](https://www.linkedin.com/in/daniel-maxwell-white/)
