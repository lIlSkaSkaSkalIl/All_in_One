# @title ♻️ For Google Drive Authentication
# @markdown <br><center><img src='https://user-images.githubusercontent.com/125879861/255377947-6ac19c35-dbbd-4a9b-bc0e-c603de81c533.png' height="70" alt="Gdrive-logo"/></center>
# @markdown <center><h2><font color=yellow><b>Mount Google Drive | Generate Access Token</b></h2></center><br>

# @markdown <br><h3><font color=cyan><b>🐬 To Mount Google Drive in Colab</b></h3>

MODE = "Mount"  # @param ["Mount", "Unmount", "Nothing"]
MOUNT_TO = "/content/drive"  # @param ["/content/drive"]

# @markdown <br><h3><font color=orange><b>🦐 To Generate Google Drive Access Token</b></h3>

DO = "Nothing"  # @param ["Generate", "Nothing"]
SAVE_TO = "/content/token.pickle"  # @param ["/content/token.pickle"]
# Mount your Gdrive!

# @markdown > <i>Select `Nothing` To Select Single Operation

import pickle
from pydrive2.auth import GoogleAuth
from google.colab import auth
from oauth2client.client import GoogleCredentials
from google.colab import drive

# auth.authenticate_user()

drive.mount._DEBUG = False
if MODE == "Mount":
    drive.mount(MOUNT_TO, force_remount=True)
elif MODE == "Unmount":
    try:
        drive.flush_and_unmount()
    except ValueError:
        pass

if DO == "Generate":
    # Authenticate the user
    auth.authenticate_user()
    # Get the credentials
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()

    # Save the credentials for the next run
    with open(SAVE_TO, "wb") as token:
        pickle.dump(gauth.credentials, token)

    print(f"\nFile Saved as {SAVE_TO} 😘 ")

# drive = GoogleDrive(gauth)
