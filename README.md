# SHACLINT: SHACL Shapes Integration Implementation

SHACLINT is the implementation of a software method designed for the integration of SHACL shapes from heterogeneous data sources. This method operates at a semantic level, using ontology alignments to coherently merge validation constraints. The main objective is to generate a single SHACL shapes graph that can validate aggregated knowledge graphs, ensuring their structural and conceptual integrity.

This tool is the reference implementation of the SHACLINT method, developed within the framework of research on the aggregation and semantic representation of Digital Twins (DTws).

## Installation

To install the necessary dependencies, run the following command in the root of the repository:

```bash
pip install -r requirements.txt
```

## Usage

To launch the application, you can use Flask. Make sure your `FLASK_APP` environment variable points to the application, and then run the server.

```bash
# For Windows
set FLASK_APP=shacl_integration_app
python -m flask run

# For macOS/Linux
export FLASK_APP=shacl_integration_app
python -m flask run
```

By default, the service will run at `http://127.0.0.1:5000`.

## REST API

The service exposes a REST API to interact with the integration method.

### Get Integration Options

To discover the concept clusters that can be integrated, make a GET request to the following endpoint:

```bash
curl http://127.0.0.1:5000/integration_options
```

### Perform an Integration

To run the integration process on a specific cluster, make a POST request, specifying the cluster `id` and the `operation` to perform (e.g., `union` or `intersection`).

-   **URL**: `/integrate/<id>/<operation>`
-   **Method**: `POST`
-   **URL Parameters**:
    -   `id`: The identifier of the dataset to integrate (obtained from the `/integration_options` endpoint).
    -   `operation`: The integration strategy to apply (`union` or `intersection`).

**Example call with cURL:**

```bash
curl -X POST http://127.0.0.1:5000/integrate/1/union
```

This will return the integrated SHACL graph as the result of the operation.

## How to Cite (DOI)

If you use this software in your research, please cite it. You can use the following DOI to reference it:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15813107.svg)](https://doi.org/10.5281/zenodo.15813107)

## License

This project is under the Apache 2.0 License. You can find more details in the [LICENSE](LICENSE) file.