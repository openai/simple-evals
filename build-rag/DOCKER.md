### `DOCKER.md` – Full Documentation for Building and Running the Docker Container

This documentation explains how to use Docker to build and run the Python script in a lightweight container, mapping the current directory for flexibility and ease of use.

---

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) must be installed on your system.
- Ensure your project directory contains the following files:
  - `pretty_print_csv.py`: Your Python script.
  - `simple_qa_test_set.csv`: The input CSV file.
  - `Dockerfile`: The Dockerfile for containerizing the application.
  - `requirements.txt`: List of Python dependencies (empty in this case, as no external libraries are required).

---

### Dockerfile Overview

The Docker container uses the lightweight `python:3.11-slim` base image to create a small and efficient environment for running the Python script. The current directory is mapped to `/app` in the container for easy file access and editing.

---

### Step-by-Step Instructions

#### 1. Build the Docker Image

Run the following command in the project directory (where the `Dockerfile` is located):

```bash
docker build -t pretty-print-csv .
```

- `-t pretty-print-csv`: Tags the image with the name `pretty-print-csv`.
- The `.` specifies the current directory as the build context.

---

#### 2. Run the Container

To run the container and map your current directory to the `/app` directory in the container, use this command:

```bash
docker run --rm -it -v "$(pwd):/app" pretty-print-csv
```

- `--rm`: Automatically removes the container when it exits.
- `-it`: Starts an interactive terminal session inside the container.
- `-v "$(pwd):/app"`: Mounts your current directory to the `/app` directory in the container, making your files accessible inside the container.

---

#### 3. Access the Bash Shell

Once the container is running, you will be dropped into a Bash shell within the container. From here, you can execute commands like:

- **Run the script:**
  ```bash
  python pretty_print_csv.py
  ```

- **Inspect files:**
  ```bash
  ls -l
  ```

- **Edit or add files (via mapped volume):**
  Any changes made to files in the `/app` directory inside the container will reflect in your host machine's current directory.

---

#### 4. Exit the Container

To exit the container, type:

```bash
exit
```

This will stop and remove the container because of the `--rm` option.

---

### Troubleshooting

1. **Error: `docker: command not found`**
   - Ensure Docker is installed and added to your system's PATH.

2. **Permission Denied When Running Docker**
   - On Linux, you may need to prefix commands with `sudo` or add your user to the `docker` group.

3. **Changes Not Reflected**
   - Ensure the `-v "$(pwd):/app"` flag is used to map the current directory to the container.

---

### Example Workflow

1. **Build the image:**
   ```bash
   docker build -t pretty-print-csv .
   ```

2. **Run the container with mapped volume:**
   ```bash
   docker run --rm -it -v "$(pwd):/app" pretty-print-csv
   ```

3. **Run the script inside the container:**
   ```bash
   python pretty_print_csv.py
   ```

4. **Exit the container:**
   ```bash
   exit
   ```

---

### Additional Notes

- If you update `pretty_print_csv.py` or `simple_qa_test_set.csv`, there's no need to rebuild the Docker image. The mapped volume ensures the container always works with the latest files in your current directory.
- For production use, consider adjusting the `CMD` in the Dockerfile to directly execute the Python script, reducing the need to manually run it inside the container.

Happy coding! 🚀
