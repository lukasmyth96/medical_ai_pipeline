<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->






<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Medical Pre-authorization AI Pipeline</h3>

  <p align="center">
    An LLM-powered pipeline to help healthcare insurers process Pre-authorization requests.
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#project-overview">Project Overview</a>
      <ul>
        <li><a href="##pipeline-1---cpt-guideline-ingestion">Pipeline 1 - Guideline Ingestion</a></li>
        <li><a href="#pipeline-2---pre-authorization">Pipeline 2 - Pre-authorization</a></li>
        <li><a href="#rest-api">REST API</a></li>
      </ul>
    </li>
    <li>
      <a href="#running-the-pipelines">Running the Pipelines</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
  </ol>
</details>

---
## Project Overview

The project contains two LLM-powered pipelines along with a REST API which can be used to run each pipeline and view the results.

### Pipeline 1 - CPT Guideline Ingestion

This pipeline parses, processes and stores the Pre-authorization guidelines (criteria) for a single CPT code.
The input to the pipeline is a CPT code and a PDF file containing the corresponding guidelines for that code.

In production, this pipeline could be used to ingest the guidelines supplied by a customer (healthcare insurer) prior to running
the Pre-Authorization pipeline against those guidelines.

The pipeline performs the following steps:
1. Extracts all text from the PDF.
2. Filters irrelevant (non-guideline) text.
3. Formats criteria as enumerated bullet points <br> (_... these numbers are used as an ID each criterion_ )
4. Uses LLM to convert criteria into logical decision tree <br> (_... which is used by Pipeline 2 to determine if criteria are met_ )

### Pipeline 2 - Pre-authorization

This pipeline takes a single medical record and uses a RAG pipeline to determine whether the criteria are met for the
requested CPT code.

The pipeline performs the following steps:
1. Extracts all text from the PDF.
2. Indexes the document for RAG using [LlamaIndex](https://www.llamaindex.ai/).
3. Uses RAG pipeline to extract requested CPT code.
4. Loads the criteria for this CPT code that were previously ingested by [Pipeline 1](#pipeline-1---cpt-guideline-ingestion).
5. Uses RAG pipeline to determine whether prior treatment was attempted and successful. <br> (..._if so, pipeline exits early as per task instructions._)
6. Uses RAG pipeline to determine separately whether each criterion is met.
7. Uses criteria decision tree (created by Pipeline 1) to determine whether criteria are met overall. 

### REST API

The REST API (built with [FastAPI](https://fastapi.tiangolo.com/)) enables you to easily call and view the results
of each pipeline using FastAPI's builtin [interactive docs page](https://fastapi.tiangolo.com/#interactive-api-docs).

In production, this API would allow customers (insurers) to upload their CPT guidelines (via Pipeline 1) and submit
the Pre-authorization requests they receive for analysis (via Pipeline 2).

The API saves (and uses) pipeline results to disk within the [database](/database) folder which serves as a mock for three services you might use in production:
- A NoSQL DB to store application data (e.g. MongoDB, DocumentDB, Firestore).
- A cloud file storage system for uploaded PDFs (e.g S3, Google Cloud Storage).
- A Vector DB to store embeddings for RAG (e.g. Chrome, Pinecone).


The API has two endpoints:

- `POST /pre-authorization/guidelines`
  - Calls Pipeline 1 to ingest the guidelines for a single CPT code.
  - Saves result as JSON to the mock DB.
<br><br>
- `POST /pre-authorization` 
  - Calls Pipeline 2 to generate the Pre-authorization report. 
  - Saves result as JSON to the mock DB.

See [Running the Pipelines](#running-the-pipelines) for instructions on running and using the API.





<p align="right">(<a href="#readme-top">back to top</a>)</p>


---
## Running the Pipelines

To run the pipelines, you can run the API using Docker and use the [FastAPI interactive docs](https://fastapi.tiangolo.com/#interactive-api-docs)
page to call each endpoint which will run a pipeline and return the results in the response.

### Prerequisites

* Docker
* An OpenAI API Key


### Instructions

1. Create a `.env` file in the repo root directory.
2. Copy the contents of `example.env` into the `.env` and populate the Open AI API Key.
3. Run `run_web_app.sh` which will build and run the Docker image:
    ```shell
    bash ./run_web_app.sh
    ```
4. Open http://127.0.0.1:8000 to view the FastAPI interactive docs page.
5. To call the desired endpoint
   1. Select the endpoint you want to call
   2. Click "Try it out" on the right
   3. Populate the request body using the form
   4. Click "Execute" to send the request

Once the pipeline is complete, the results will be displayed as a JSON object (the response body).


<p align="right">(<a href="#readme-top">back to top</a>)</p>
