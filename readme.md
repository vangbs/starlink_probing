## Requirements

- Python 3.x
- `mtr` (for network measurements)

## Installation

### 1. Install `mtr`

#### On Ubuntu/Debian-based systems:
To install `mtr`, use the following command:

```bash
sudo apt-get update
sudo apt-get install mtr
```

#### On macOS (using Homebrew):
To install `mtr`, use the following command:

```bash
brew install mtr
```

#### On CentOS/RHEL-based systems:
To install `mtr`, use the following command:

```bash
sudo yum install mtr
```

## Running the Program

Once `mtr` is installed, you can run the program using Python 3 with the following command:

```bash
python3 tance_backbone.py <server_name>
```

The program will output results into a folder named `backbone_trace_<server_name>`.
