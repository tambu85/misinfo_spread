# misinfo_spread

Replication code for XXX <-- enter paper reference here

# Things to do
See outstanding tasks in [TODO.md](./TODO.md).

## Contents
These are the main contents of this repository:
* `data` - place input data here;
* `experiments` - place working code here;
* `output` - Outputs and plot files (may go anytime);
* `README.md` - This file;
* `simulator` - R scripts for monte carlo simulation of the various versions of the model;
* `replication` - replication code;

## Installation

These steps assume you are using [Anaconda Python](https://www.anaconda.com/) as your python distribution, which comes with the `conda` package manager installed.

1. Open the terminal and clone this repository from github:

    ```
    git clone git@github.com:tambu85/misinfo_spread.git
    ```

   This assumes you have configured [authentication to Github via SSH](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github#ssh).  

2. Enter into the folder `misinfo_spread`:

    ```
    cd misinfo_spread
    ```

3. Create a virtual environment and install the required dependencies (see `environment.yml`). With this can be achieved by running:

    ```
    conda env create -n misinfo_spread --file environment.yml
    ```

4. Activate the environment you have just created:

    ```
    conda activate misinfo_spread
    ```

4. Install pip, either via conda (`conda install pip`) or its [default installation methods](https://pip.pypa.io/en/stable/installation/).
5. Install the package as an editable install:

    ```
    pip install -e .
    ```
