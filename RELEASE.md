# Release procedure

* Commit changes that are part of the Release
* Bump version number :

    `bumpversion patch --commit --tag`

* Upload release to PyPi

    `flit upload`

* Push to both repositories

    `git push --tags`

* Add release to GitHub
