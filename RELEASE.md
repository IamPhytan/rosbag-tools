# Release procedure

* Commit changes that are part of the Release
* Bump version number :

    `bumpversion patch --commit --tag`

* Upload release to PyPi

    `flit publish`

* Push to both repositories

    `git push --tags`

* Add release to GitHub
