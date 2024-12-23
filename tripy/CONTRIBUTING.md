# Contributing To Tripy

Thank you for considering contributing to Tripy!

## Setting Up

1. Clone the TensorRT-Incubator repository:

    ```bash
    git clone https://github.com/NVIDIA/TensorRT-Incubator.git
    ```

2.  Pull or build the development container locally.

    -  If you haven't made changes that could impact the container
        (e.g. changes to [Dockerfile](./Dockerfile) or [pyproject.toml](./pyproject.toml))
        then you can pull an existing container.

        First, ensure you have logged in to the registry. When prompted, you can use
        your GitHub username and a
        [personal access token](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry)
        for the password:

        ```bash
        docker login ghcr.io/nvidia/tensorrt-incubator
        ```

        Next, pull and launch the container. From the [`tripy` root directory](.), run:

        ```bash
        docker run --pull always --gpus all -it -p 8080:8080 -v $(pwd):/tripy/ --rm ghcr.io/nvidia/tensorrt-incubator/tripy
        ```

    - Otherwise, you can build the container locally and launch it.
        From the [`tripy` root directory](.), run:

        ```bash
        docker build -t tripy .
        docker run --gpus all -it -p 8080:8080 -v $(pwd):/tripy/ --rm tripy:latest
        ```

3. You should now be able to use `nvtripy` in the container. To test it out, you can run a quick sanity check:

    ```bash
    python3 -c "import nvtripy as tp; print(tp.ones((2, 3)))"
    ```

    This should give you some output like:
    ```
    tensor(
        [[1. 1. 1.]
        [1. 1. 1.]],
        dtype=float32, loc=gpu:0, shape=(2, 3)
    )
    ```

## Making Changes

### Before You Start: Install pre-commit

Before committing changes, make sure you install the pre-commit hook.
You only need to do this once.

We suggest you do this *outside* the container and also use `git` from
outside the container.

From the [`tripy` root directory](.), run:
```bash
python3 -m pip install pre-commit
pre-commit install
```

### Getting Up To Speed

We've added several guides that can help you better understand
the codebase. We recommend starting with the
[architecture](https://nvidia.github.io/TensorRT-Incubator/post0_developer_guides/architecture.html)
documentation.

If you're intersted in adding a new operator to Tripy, refer to
[this guide](https://nvidia.github.io/TensorRT-Incubator/post0_developer_guides/how-to-add-new-ops.html).


### Making Commits

1. Tripy follows [fork based developement](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo).
    - Fork repo from GitHub
    - Push changes to your branches on fork instead of the main repo
    - Create a PR to merge changes from fork to the main repo

2. Managing PRs
    - Label your PR correctly (e.g., use `tripy` for changes to `tripy`).
    - Add a brief description explaining the purpose of the change.
    - Each functional change should include an update to an existing test or a new test.
    - Ensure any commits you make are signed. See [this page](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification#ssh-commit-signature-verification)
    for details on signing commits.

3. Please make sure any contributions you make satisfy the developer certificate of origin:

> Developer Certificate of Origin
>	Version 1.1
>
>	Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
>
>	Everyone is permitted to copy and distribute verbatim copies of this
>	license document, but changing it is not allowed.
>
>
>	Developer's Certificate of Origin 1.1
>
>	By making a contribution to this project, I certify that:
>
>	(a) The contribution was created in whole or in part by me and I
>		have the right to submit it under the open source license
>		indicated in the file; or
>
>	(b) The contribution is based upon previous work that, to the best
>		of my knowledge, is covered under an appropriate open source
>		license and I have the right under that license to submit that
>		work with modifications, whether created in whole or in part
>		by me, under the same open source license (unless I am
>		permitted to submit under a different license), as indicated
>		in the file; or
>
>	(c) The contribution was provided directly to me by some other
>		person who certified (a), (b) or (c) and I have not modified
>		it.
>
>	(d) I understand and agree that this project and the contribution
>		are public and that a record of the contribution (including all
>		personal information I submit with it, including my sign-off) is
>		maintained indefinitely and may be redistributed consistent with
>		this project or the open source license(s) involved.

### Tests

Almost any change you make will require you to add tests or modify existing ones.
For details on tests, see [the tests README](./tests/README.md).

### Documentation

If you add or modify any public-facing interfaces, you should also update the documentation accordingly.
For details on the public documentation, see [the documentation README](./docs/README.md).

### Coding Guidelines

We do not have a specific coding style at the moment. However, we recommend contributors to follow consistent coding style with the existing codebase and refer to [PEP8 style guide](https://peps.python.org/pep-0008/).

Python files are formatted using the [`black` formatter](https://black.readthedocs.io/en/stable/).

### Advanced: Using Custom MLIR-TensorRT Builds With Tripy

Tripy depends on [MLIR-TensorRT](../mlir-tensorrt/README.md) for compilation and execution.
The Tripy container includes a build of MLIR-TensorRT, but in some cases, you may want to test Tripy with a local build:

1. Build MLIR-TensorRT as per the instructions in the [README](../mlir-tensorrt/README.md).

2. Launch the container with mlir-tensorrt repository mapped for accessing wheels files; from the [`tripy` root directory](.), run:
    ```bash
    docker run --gpus all -it -p 8080:8080 -v $(pwd):/tripy/ -v $(pwd)/../mlir-tensorrt:/mlir-tensorrt  --rm tripy:latest
    ```

3. Install MLIR-TensorRT wheels
    MLIR-TensorRT must be built against a specific version of TensorRT, but will be able
    to work with any ABI-compatible version at runtime.

    The Tripy container includes TensorRT. Follow these steps to confirm
    the TensorRT version and ensure compatibility with your TensorRT wheels:

    ```bash
    echo "$LD_LIBRARY_PATH" | grep -oP 'TensorRT-\K\d+\.\d+\.\d+\.\d+'
    ```

    Ensure the installed MLIR-TensorRT wheels have:
    * The same major version as the TensorRT version in the container.
    * A minor version equal to or higher than the version in the container.

    For example, to install Python 3.10.12 wheels compatible with TensorRT 10.2+, run:
    ```bash
    python3 -m pip install --force-reinstall /mlir-tensorrt/build/wheels/python3.10.12/trt102/**/*.whl
    ```

4. Verify everything works:
    ```bash
    python3 -c "import nvtripy as tp; print(tp.ones((2, 3)))"
    ```
