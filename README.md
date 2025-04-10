> [!NOTE]
> This converter is still a WIP. Most of the "common" structures work but the resulting .conllu files are not 100% correct.

# Converting the PPCHY to UD
This is an adapted version of the [UDConverter](https://github.com/thorunna/UDConverter) that was originally created for the [IcePaHC](https://linguist.is/wiki/index.php?title=Icelandic_Parsed_Historical_Corpus_(IcePaHC)).
The scripts are modified to work with the [PPCHY](https://github.com/beatrice57/penn-parsed-corpus-of-historical-yiddish). All credits for the original implementation goes to the contributors to the original [UDConverter](https://github.com/thorunna/UDConverter). 

## Setup
Required packages can be installed by: 
```
pip install -r requirements.txt
```
## Usage

Scripts are in the `scripts` folder.

### Preprocessing
Preprocessing has to be done manually at the moment. There is a script, `preProcess.sh`, that can be run on the desired files. 

### Conversion
The main script is `convert.py`. You can run it using: 
```
python3 convert.py -N -i /path/to/corpus/* --output
```

Using the `--output` flag create the respective .conllu file in the `/CoNLLU/` folder.

