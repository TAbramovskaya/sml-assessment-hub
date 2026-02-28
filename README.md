## SML Assessment Hub

### Overview

**SML Assessment Hub** is a project designed to collect and aggregate information about student performance while solving tasks as part of specialized courses on the Simulative learning platform.

The Simulative educational platform provides a wide range of tasks across various technical domains, along with an environment for solving these tasks and tools for validating and assessing solutions. Students from different schools and educational programs use the platform as part of their own curricula.

This project focuses on collecting performance data of a Simulative Client’s students for further processing, analysis, and reporting.

### Goals

Simulative provides an API for accessing student performance data. This project implements the following functionality:

- fetching data from Simulative servers, followed by processing and validation for storage and analysis;

- preparing a PostgreSQL database, including database schema design and data loading;

- exporting data to Google Sheets, generating and uploading reports on student activity and course results for the client;

- comprehensive logging of all stages of the processes described above.

### Configuration

Sensitive data must be stored in the `secret` directory. This includes:

- Client-related configuration data;

- database connection credentials;

- service account credentials for Google APIs.

Anonymized templates of the required secret files are provided in the `secret_boilerplates` directory.