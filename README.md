<p align="center">
  <img width="360px" alt="Datahugger - Where DOI hugs Data" src="https://github.com/grycap/datahugger/raw/main/datahugger_logo.svg">
</p>

# Datahugger - Where DOI :open_hands: Data

Datahugger is a tool to download scientific datasets, software, and code from a large number of repositories based on their DOI [(wiki)](https://en.wikipedia.org/wiki/Digital_object_identifier) or URL. With Datahugger, you can automate the downloading of data and improve the reproducibility of your research. Datahugger provides a straightforward [Python interface](#download-with-python) as well as an intuitive [Command Line Interface](#download-with-command-line) (CLI).

## Supported repositories

Datahugger offers support for more than [<!-- count -->377<!-- count --> generic and specific (scientific) repositories](https://j535d165.github.io/datahugger/repositories) (and more to come!).

[![Datahugger support Zenodo, Dataverse, DataOne, GitHub, FigShare, HuggingFace, Mendeley Data, Dryad, OSF, and many more](https://github.com/J535D165/datahugger/raw/main/docs/images/logos.png)](https://j535d165.github.io/datahugger/repositories)

We are still expanding Datahugger with support for more repositories. You can
help by [requesting support for a repository](https://github.com/grycap/datahugger/issues/new/choose) in the issue
tracker. Pull Requests are very welcome as well.

## Installation

Datahugger requires Python 3.6 or later.

```
pip install git+https://github.com/micafer/datahugger
```

## Getting started

### Datahugger with Python

Load a dataset (or any digital asset) from a repository with the
`datahugger.get()` function. The first argument is the DOI or URL,
and the second is the folder name to store the dataset (it will be
created if it does not exist).

The following code loads the Zenodo dataset [10.5281/zenodo.6625880](https://doi.org/10.5281/zenodo.6625880) into
the folder `data`. This dataset is also used in the repository integration tests.

```python
import datahugger

# download the dataset to the folder "data"
datahugger.get("10.5281/zenodo.6625880", "data")
```

For an example of how this can integrate with your work, see the
[example workflow notebook](https://github.com/grycap/datahugger/blob/main/examples/example_datahugger_in_workflow.ipynb) or
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/grycap/datahugger/blob/main/examples/example_datahugger_in_workflow.ipynb)


### Datahugger with command line

The command line function `datahugger` provides an easy interface to download data. The first
argument is the DOI or URL, and the second argument is the name of the folder to store the dataset (will be
created if it does not exist).

```bash
datahugger 10.5281/zenodo.6625880 data
```

```bash
% datahugger 10.5281/zenodo.6625880 data
quasiperiod.ipynb                  : 100%|██████████████████████████████████████████| 252k/252k
quasiperiod_svm_learning_cu[...].py: 100%|████████████████████████████████████████| 1.96k/1.96k
quasiperiod_log_svm_hyperpa[...].py: 100%|████████████████████████████████████████| 2.62k/2.62k
rational_dimension.ipynb           : 100%|████████████████████████████████████████| 97.7k/97.7k
quasiperiod_svm_learning_cu[...].py: 100%|████████████████████████████████████████| 1.96k/1.96k
README.txt                         : |                                            | 2.95k/0.00
quasiperiod_log_svm_learnin[...].py: 100%|████████████████████████████████████████| 1.98k/1.98k
quasiperiod_svm_learning_cu[...].py: 100%|████████████████████████████████████████| 1.96k/1.96k
quasiperiod_log_svm_learnin[...].py: 100%|████████████████████████████████████████| 1.98k/1.98k
quasiperiod.m                      : 100%|████████████████████████████████████████| 3.25k/3.25k
quasiperiod.txt.gz                 : |                                            | 1.76G/0.00
quasiperiod_log_svm_learnin[...].py: 100%|████████████████████████████████████████| 1.98k/1.98k
quasiperiod_svm_hyperparame[...].py: 100%|████████████████████████████████████████| 2.65k/2.65k
```

**Tip:** On some systems, you have to quote the DOI or URL. For example: `datahugger "10.5281/zenodo.6625880" data`.

## Tips and tricks

- No need to struggle with DOIs versus DOI URLs. They both work (and more). Example: The values `10.5061/dryad.x3ffbg7m8`, `doi:10.5061/dryad.x3ffbg7m8`, [`https://doi.org/10.5061/dryad.x3ffbg7m8`](https://doi.org/10.5061/dryad.x3ffbg7m8), and [`https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8`](https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8) all point to the same dataset.
- Do not republish the dataset when uploading your data to a scientific data repository. These storage resources can be used better :)

## Contact

Please feel free to reach out with questions, comments, and suggestions. The
[issue tracker](/issues) is a good starting point. You can also email me at
[jonathandebruinos@gmail.com](mailto:jonathandebruinos@gmail.com).
