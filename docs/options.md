# Options

## Skip large files

For most repositories, it is possible to skip files that exceed a certain
number of bytes. For example, you want to skip files larger than 50Mb.


=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data --max_file_size 50000000
    ```

=== "Python"

    ``` python
    datahugger.get("10.5061/dryad.x3ffbg7m8", "data", max_file_size=50000000)
    ```


## Extract single zip

Some services like [Zenodo](https://zenodo.org) don't offer an option to preserve
folder structures. Therefore, the content is often zipped before being
uploaded to the service. In this case, Datahugger will unzip the file to the
output folder by default.

Disable auto unzip function

=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.x3ffbg7m8 data --no-unzip
    ```

=== "Python"


    ``` python
    datahugger.get("10.5061/dryad.x3ffbg7m8", "data", unzip=False)
    ```

### Download selected files from a ZIP

When a dataset contains a single ZIP, use `--zip` (or `-z`) with
`--filter-files` to download only matching ZIP members. The filter is a Python
regular expression matched from the beginning of each member's **full path**
inside the ZIP, and the paths are preserved in the output directory.

=== "CLI"

    ``` bash
    datahugger 10.5281/zenodo.10809434 data --zip \
      --filter-files 'obsea_dataset/labels/.*\.xml'
    ```

=== "Python"

    ``` python
    datahugger.get(
        "10.5281/zenodo.10809434", "data",
        zip=True, filter_files=r"obsea_dataset/labels/.*\.xml",
    )
    ```

This requires HTTP byte-range support at the ZIP download URL. If the server
does not support it, the operation fails rather than downloading the whole ZIP.
The ZIP directory and selected compressed members are transferred; downloaded
members are checked against their ZIP CRC. Repository checksums for the complete
ZIP cannot be verified in this mode, so `--checksum` is not supported.
`--max-file-size` applies to the uncompressed size of each selected member,
`--force-download` controls overwriting, and `--dry-run` lists matches without
downloading their contents. Without a filter, `--zip` uses the normal full ZIP
download and extraction behavior, which flattens folder paths. `--zip` cannot
be combined with `--no-unzip`.


## Download mode

By default, Datahugger skips the download of files and datasets that are
already available on the local system. The options
are: "skip_if_exists", "force_redownload".


=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data --download_mode force_redownload
    ```

=== "Python"

    ``` python
    datahugger.get("10.5061/dryad.x3ffbg7m8", "data", download_mode="force_redownload")
    ```


## Progress

By default, Datahugger shows the download progress. You can disable the
progress indicator.


=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data --no-progress
    ```

=== "Python"

    ``` python
    datahugger.get("10.5061/dryad.x3ffbg7m8", "data", progress=False)
    ```
