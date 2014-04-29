import os
from upseto import manifest
from upseto import gitwrapper
import collections


Dependency = collections.namedtuple("Dependency", "requirement projectDir manifest parentOriginURL")


class Traverse:
    def __init__(self, baseDir=".."):
        self._baseDir = baseDir
        self._visited = set()

    def traverse(self, mani):
        """
        Recursivly visit all dependencies, once. Yields a 'Dependency'
        named tuple for each dependency visited (root not included).
        the 'manifest' field might be none if this project does not
        have an upseto manifest.
        """
        if mani.originURL() in self._visited:
            return
        self._visited.add(mani.originURL())
        for requirement in mani.requirements():
            basename = gitwrapper.originURLBasename(requirement['originURL'])
            projectDir = os.path.join(self._baseDir, basename)
            submanifest = manifest.Manifest.fromDir(projectDir) if \
                manifest.Manifest.exists(projectDir) else None
            dependency = Dependency(
                requirement=requirement,
                projectDir=projectDir,
                manifest=submanifest,
                parentOriginURL=mani.originURL())
            yield dependency
            # refresh manifest in case it was changed by caller (as in
            # FulfillRequirements which checks out the code)
            refreshedSubmanifest = manifest.Manifest.fromDir(projectDir) if \
                manifest.Manifest.exists(projectDir) else None
            if refreshedSubmanifest is not None:
                for x in self.traverse(refreshedSubmanifest):
                    yield x
