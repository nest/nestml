Release checklist
-----------------

Follow this checklist to successfully perform a NESTML release. Let's say that 3.0 is the currently-out release, and we want to publish 3.1.

- Find out authors who contributed since the last release.

  ```bash
  git log v3.0..HEAD | grep Author\: | sort | uniq
  ```

- Ensure copyright transferal agreement is obtained from each author (contact: @heplesser). Obtain affiliation one-liner for each author.

- Edit `setup.py` and enter the right version number. Edit `pynestml/__init__.py` and enter the right version number. Push to a new branch called `release-v3.1`.

- Log in to Zenodo, and create a new upload. Press the "Reserve DOI" button.

- Go back to GitHub and create a new release from the web interface. 
  - Select the right branch, e.g. `release-v3.1`
  - Under version tag, enter the new version number. Since v3.0 we're adding the "v" prefix (e.g. "v3.1").
  - For release title, use "NESTML" + version number, e.g. "NESTML 3.1".
  - For release notes, write something starting with "\[NESTML 3.1\](https://dx.doi.org/10.5281/zenodo.3697733)" so that the Zenodo publication is linked. Look at the previous release note for further inspiration.
  - Download the generated .tar.gz file.

- Extract the tarball locally and double-check that everything looks OK! E.g. no `.git` directory, version numbers. Sanity check the filesize.

- Go back to Zenodo and enter remaining information.
  - Upload the .tar.gz file from GitHub
  - Upload type: software
  - For title: "NESTML 3.1"
  - Enter authors
  - For description: copy release notes from GitHub, but remove hyperlink to doi.org. Append "For further information, please visit https://github.com/nest/nestml"
  - Select "Open Access"
  - Enter "GNU GPL v2.0 only" as a licence
  - Under "Related/alternate identifiers", enter a reference to the Zenodo entry of the previous NESTML version (here, v3.0) by entering the DOI of the v3.0 entry.
  - Click Save, then click Publish

- Go to the Zenodo entry of the previous NESTML version (here, v3.0), and add a reference to the Zenodo entry of the NESTML version currently being released, under "Related/alternate identifiers". Use the DOI of the new Zenodo entry.

- Perform a corresponding release on PyPi. From the `release-v3.1` branch:

  ```bash
  python setup.py bdist_wheel
  twine upload dist/*
  ```

- Update version number on master branch: edit `setup.py` and add suffix to version number, e.g. `version='3.1-post-dev'`, to distinguish master branch version from release version. Do the same for `pynestml/__init__.py`.

  ```bash
  git add setup.py
  git commit -m "add -post-dev suffix to version number to distinguish master branch version from release version"
  git push -u origin master
  ```

- Delete the release branch (in this example, `release-v3.1`).
