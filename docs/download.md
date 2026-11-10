# Download dataset

The following example downloads dataset
[10.5061/dryad.x3ffbg7m8](https://doi.org/10.5061/dryad.x3ffbg7m8) to the
folder `data`.

##  Download dataset from DOI

=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data
    ```

    In some situations, you might have to quote the number the DOI (e.g. `datahugger "10.5061/dryad.31zcrjdm5" data`)

=== "Python"

    ``` python
    import datahugger

    datahugger.get("10.5061/dryad.x3ffbg7m8", "data")
    ```

##  Download dataset from URL

=== "CLI"

    ``` bash
    datahugger https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8 data
    ```

    In some situations, you might have to quote the number the DOI (e.g. `datahugger "https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8" data`)

=== "Python"

    ``` python
    import datahugger

    datahugger.get("https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8", "data")
    ```

## Dryad authentication

Dryad requires an API authentication token to download dataset files. Pass the token with `--auth-token` in the CLI or the `token` argument in Python. See Dryad's [API account documentation](https://github.com/datadryad/dryad-app/blob/main/documentation/apis/api_accounts.md) for information about requesting API access and obtaining a token.

=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data --auth-token YOUR_DRYAD_TOKEN
    ```

=== "Python"

    ``` python
    import datahugger

    datahugger.get("10.5061/dryad.31zcrjdm5", "data", token="YOUR_DRYAD_TOKEN")
    ```

Keep your token private; do not commit it to source control or share it publicly.
