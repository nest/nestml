Release checklist
-----------------

Follow this checklist to successfully perform a NESTML release. Let's say that 3.0 is the currently-out release, and we want to publish 3.1.

- Find out authors who contributed since the last release.

  ```bash
  git log v3.0..HEAD | grep Author\: | sort | uniq
  ```

- Ensure copyright transferal agreement is obtained from each author (contact: HEP).

- Edit `setup.py` and enter the right version number.

- Add a tag to the repository. Since v3.0 we're adding the "v" prefix.

  ```bash
  git tag -a v3.1
  ```

  It is recommended to write some release notes at this point. Check formatting by looking at the release notes of the currently-out version.

  ```bash
  git push origin v3.1
  ```

- Perform a corresponding release on PyPi

  ```bash
  python setup.py sdist
  twine upload dist/*
  ```

- Edit `setup.py` and add suffix to version number, e.g. `version='3.1-post-dev'`, to distinguish master branch version from release version.

  ```bash
  git add setup.py
  git commit -m "add -post-dev suffix to version number to distinguish master branch version from release version"
  git push -u origin master
  ```
