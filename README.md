                  #+:::::++           ++:::::++           ++:::::++
                +-:=++++++++        +::+++++++++        +-:-++++++++
              :+::++++*     +     #=:+++++=     +     *+::++++      #
             +::++++++           +:-++++++           +::++++++
            +:++++++++*        ++:++++++++*        *+:=+++++++
          ++++++++++++++*    ++:++++++++++++:    ++-++++++++++++     .
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
       :+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
         ++++++           #++++++++++*       ++++++++#        #+++*

---

# surfreport

`surfreport` is a Python package that allows you to retrieve surf reports directly from the terminal. It fetches data from surf report APIs, providing a command-line interface (CLI) for easy access to current and forecasted surf conditions.

## Installation

1. Clone this repository:

```sh
git clone https://github.com/jtabke/surfreport.git
cd surfreport
```

2. Install dependencies:

```sh
pip install .
```

### Contributing

For contributions, install the package with development dependencies using:

```sh
pip install -e ".[dev]"
```

## Usage

Run `surfreport` to access a menu of all regions. Selecting a subregion or spot will display an overview and surf report if available.

### Search for a spot

```sh
surfreport -s <spot query>
```

Replace `<spot query>` with the surf spot you with to get the forecast for. If there are multiple matches it will ask you to choose appropriate match.

## Roadmap

- **CLI Enhancements**: Currently, the focus is on building out the CLI usage and adding more data sources to ensure comprehensive surf report retrieval.
- **TUI Development**: Future developments may include a Text User Interface (TUI) for visual representation of surf conditions.
