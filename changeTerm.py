# Import UVic Class from uvic.py
import uvic

# Change Term
def changeTerm():
    """
    Change Selected Term for UVic Schedule. 

    Parameters None
    Returns None
    """

    # Authorize with UVic
    auth = uvic.Auth()

    # Load to Change Term Page
    auth.load('https://www.uvic.ca/BAN1P/bwskflib.P_SelDefTerm?calling_proc_name=bwskfshd.P_CrseSchdDetl')

# Main
def main():
    changeTerm()

if __name__ == "__main__":
    main()
