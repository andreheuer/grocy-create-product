# grocy-create-product
This script supports the batch creation of new products in [Grocy](https://grocy.info). Based on the scanned (or entered) barcode, 
the [https://de.openfoodfacts.org](openfoodfacts) and [https://world.openbeautyfacts.org](openbeautyfacts) databases are queried. If all data has been
provided, the new product is created in Grocy, the calories are entered (taken from Openfoodfact for g/kg and ml/L articles) and a picture (also from openfoodfacts)
is uploaded to Grocy.

## How to use
1. Install Python 3
2. Clone repository
3. Change `GROCY_URL` to your URL and set default group and location IDs.
4. Set `GROCY_API_KEY` to your API key
5. Set a default group id with `DEFAULT_GROUP` (so you just to have press ENTER to confirm)
6. Set a default location id with `DEFAULT_LOCATION` (so you just to have press ENTER to confirm)
7. Set `CONTINUOUS_MODE` mode to `True` or `False`. If `True`, the script will run in a loop.
8. Run the script either with a barcode as parameter (`CONTINUOUS_MODE` should be `False` then) or without a parameter

The script can be aborted either by an empty string and pressing enter in the barcode prompt or pressing CTRL+C in any prompt.
