# py-vendor
[Install](#install)  [Use](#use) - [Examples](#examples) -
[Config File](#config-file) - [Contribute](#contribute)

Easy, configurable, and reproducible code vendors.

## Install
All package releases are available on PyPI and can be installed using `pip`:
```shell
pip instal py-vendor
```

## Use
After installing the package the `py-vendor` command line utility should be
available:
```shell
py-vendor --help
```

Define the vendors in a YAML config file:
```yaml
# py-vendor.yml
params:
  vendor_dir: src/my_vendors
vendors:
  example:
    url: https://github.com/Stannislav/dummy.git
    ref: 68d5403c76fb66758c45af1d44d32d22e0c64413
```

Then run the vendoring process:
```shell
py-vendor run --config py-vendor.yml
```

See the [Examples](#examples) section for more examples, and the
[Config File](#config-file) section for the config file specs.

## Examples
Below one can find examples of YAML config files for typical use cases.

### Vendor all files from one repository
```yaml
params:
  vendor_dir: src/vendors
vendors:
  example:
    url: https://github.com/Stannislav/dummy.git
    ref: 68d5403c76fb66758c45af1d44d32d22e0c64413
```
This copies all files from the given repository commit to
`src/vendors/example`.

### Vendor multiple repositories
```yaml
params:
  vendor_dir: src/vendors
vendors:
  example:
    url: https://github.com/Stannislav/dummy.git
    ref: 68d5403c76fb66758c45af1d44d32d22e0c64413
  aoc:
    url: https://github.com/Stannislav/Advent-of-Code
    ref: af3681d3f04aa7b8ce89e0b86e40d4e4d1dbd493
```
This will create directories `src/example` and `src/aoc`.

### Vendor only specific files
```yaml
params:
  example: src/vendors
vendors:
  dummy:
    url: https://github.com/Stannislav/dummy.git
    ref: 68d5403c76fb66758c45af1d44d32d22e0c64413
    copy:
      - README.md
      - setup.py
      - docker-compose.yml
```

### Use wildcards to glob files
```yaml
params:
  vendor_dir: src/vendors
vendors:
  example:
    url: https://github.com/Stannislav/dummy.git
    ref: 68d5403c76fb66758c45af1d44d32d22e0c64413
    copy:
      - README.md
      - src/**/*.py
```
This will copy the `README.md` file, as well as all `.py` files in the `src`
directory and all its subdirectories. The directory structure is preserved.

### Change directory structure
```yaml
params:
  vendor_dir: src/vendors
vendors:
  example:
    url: https://github.com/Stannislav/dummy.git
    ref: 68d5403c76fb66758c45af1d44d32d22e0c64413
    copy:
      - README.md
      - pattern: src/dummy/**/*.py
        relative_to: src/dummy
```
Note that since there are additional directives the file pattern must be under
the `pattern` directive.

The directory structure of the paths specified by `pattern` will be relative to
`src/dummy`. For example, the file `src/dummy/__init__.py` will be copied to
`src/vendors/example/__init__.py`. Without the `relative_to` directive it would've
gone to `src/vendors/example/src/dummy/__init__.py`.

One can also adjust the target directory where the files go by using the `dest`
directive:
```yaml
params:
  vendor_dir: src/vendors
vendors:
  example:
    url: https://github.com/Stannislav/dummy.git
    ref: 68d5403c76fb66758c45af1d44d32d22e0c64413
    copy:
      - README.md
      - pattern: src/dummy/**/*.py
        relative_to: src/dummy
        dest: sources
```
The file `src/dummy/__init__.py` will be copied to
`src/vendors/example/sources/__init__.py` etc.

### Add headers to source files and apply string replacements
```yaml
params:
  vendor_dir: src/vendors
vendors:
  example:
    url: https://github.com/Stannislav/dummy.git
    ref: 68d5403c76fb66758c45af1d44d32d22e0c64413
    copy:
      - README.md
      - pattern: src/dummy/**/*.py
        header: |+
          # This file was copied from https://github.com/Stannislav/dummy
          # License: MIT
        subs:
          - ["([h|H])ello", "\\1i"]
 ```
Every file matched by `pattern` will be modified to include the header specified
by `header`. The `subs` directive is a list of substitutions
`(sub_pattern, replacement)` that are applied to every line of all matched files.
Internally `re.sub(sub_pattern, replacement, line)` is called.

### Modify files after copying
```yaml
params:
  vendor_dir: src/vendors
vendors:
  example:
    url: https://github.com/Stannislav/dummy.git
    ref: 68d5403c76fb66758c45af1d44d32d22e0c64413
    copy:
      - pattern: src/dummy/servers/dummy_server.py
        relative_to: src/dummy/servers
        dest: server_1
      - pattern: src/dummy/servers/smarty_server.py
        relative_to: src/dummy/servers
        dest: server_2
    modify:
      - pattern: "**/*.py"
        header: |+
          # This file was copied from https://github.com/Stannislav/dummy
          # License: MIT
        subs:
          - ["([h|H])ello", "\\1i"]
```
The `modify` group has similar structure to the `copy` group. However the file
patterns now to refer to the copied files. This allows to modify files using
different globbing patterns than in the `copy` section.

### Create new files
```yaml
params:
  vendor_dir: src/vendors
vendors:
  example:
    url: https://github.com/Stannislav/dummy.git
    ref: 68d5403c76fb66758c45af1d44d32d22e0c64413
    copy:
      - pattern: src/dummy/servers/dummy_server.py
        relative_to: src/dummy/servers
        dest: server_1
      - pattern: src/dummy/servers/smarty_server.py
        relative_to: src/dummy/servers
        dest: server_2
    create:
      - __init__.py
      - server_1/__init__.py
      - server_2/__init__.py
```
The `create` group must contain a list of file paths that will be
created/touched in the target directory.

If both the `modify` and `create` groups are present, then `modify` will be
executed first.

## Config File
(coming soon)

## Contribute
This project uses [`poetry`](https://python-poetry.org/) for dependency
management and packaging.
Follow [the official installation instructions](https://python-poetry.org/docs)
to set it up on your machine.

To start working on the code clone the repository and install all dependencies:
```shell
git clone https://github.com/Stannislav/py-vendor.git
cd py-vendor
poetry install
```
See `CONTRIBUTING.md` for more details and instructions.
