### What is the "Hot directory"

<<<<<<< HEAD
This is a pre-set file location that documents will be written to when uploaded by AnythingLLM. There is really no need to touch it.
=======
This is the location where you can dump all supported file types and have them automatically converted and prepared to be digested by the vectorizing service and selected from the AnythingLLM frontend.

Files dropped in here will only be processed when you are running `python watch.py` from the `collector` directory.

Once converted the original file will be moved to the `hotdir/processed` folder so that the original document is still able to be linked to when referenced when attached as a source document during chatting.

**Supported File types**
- `.md`
- `.text`
- `.pdf`

__requires more development__
- `.png .jpg etc`
- `.mp3`
- `.mp4`
>>>>>>> 27c58541 (inital commit ⚡)
