class PartUtil:
    def __init__(self, classes, console, deputil, compiler):
        self._classes = classes
        self._console = console
        self._deputil = deputil
        self._compiler = compiler


    def getPackages(self, partIncludes, variants, collapseParts, minPackageSize, smartExclude, explicitExclude):
        # Build bitmask ids for parts
        self._console.debug("Assigning bits to parts...")

        # References partId -> bitId of that part
        self._console.indent()
        partBits = {}
        partPos = 0
        for partId in partIncludes:
            partBit = 1<<partPos

            self._console.debug("Part #%s => %s" % (partId, partBit))

            partBits[partId] = partBit
            partPos += 1

        self._console.outdent()

        self._console.debug("")
        self._console.info("Resolving part dependencies...")
        self._console.indent()

        partDeps = {}
        for partId in partIncludes:
            # Exclude all features of other parts
            # and handle dependencies the smart way =>
            # also exclude classes only needed by the
            # already excluded features
            partExcludes = []
            for otherPartId in partIncludes:
                if otherPartId != partId:
                    partExcludes.extend(partIncludes[otherPartId])

            # Extend with smart excludes
            partExcludes.extend(smartExclude)

            # Finally resolve the dependencies
            partClasses = self._deputil.resolveDependencies(partIncludes[partId], partExcludes, variants)

            # Remove explicit excludes
            for classId in explicitExclude:
                if classId in partClasses:
                    # self._console.debug("Explicit excluding: %s" % classId)
                    partClasses.remove(classId)

            # Store
            self._console.debug("Part #%s needs %s classes" % (partId, len(partClasses)))
            partDeps[partId] = partClasses

        self._console.outdent()


        # Assign classes to packages
        self._console.debug("")
        self._console.debug("Assigning classes to packages...")

        # References packageId -> class list
        packageClasses = {}

        # References packageId -> bit number e.g. 4=1, 5=2, 6=2, 7=3
        packageBitCounts = {}

        for classId in self._classes:
            packageId = 0
            bitCount = 0

            # Iterate through the parts use needs this class
            for partId in partIncludes:
                if classId in partDeps[partId]:
                    packageId += partBits[partId]
                    bitCount += 1

            # Ignore unused classes
            if packageId == 0:
                continue

            # Create missing data structure
            if not packageClasses.has_key(packageId):
                packageClasses[packageId] = []
                packageBitCounts[packageId] = bitCount

            # Finally store the class to the package
            packageClasses[packageId].append(classId)




        # Assign packages to parts
        self._console.debug("Assigning packages to parts...")
        partPackages = {}

        for partId in partIncludes:
            partBit = partBits[partId]

            for packageId in packageClasses:
                if packageId&partBit:
                    if not partPackages.has_key(partId):
                        partPackages[partId] = []

                    partPackages[partId].append(packageId)

            # Be sure that the part package list is in order to the package priorit
            self._sortPackageIdsByPriority(partPackages[partId], packageBitCounts)




        # User feedback
        self._printPartStats(packageClasses, partPackages)



        # Support for package collapsing
        # Could improve latency when initial loading an application
        # Merge all packages of a specific part into one (also supports multiple parts)
        # Hint: Part packages are sorted by priority, this way we can
        # easily merge all following packages with the first one, because
        # the first one is always the one with the highest priority
        if len(collapseParts) > 0:
            self._console.debug("")
            self._console.info("Collapsing packages...")
            self._console.indent()

            collapsePos = 0
            for partId in collapseParts:
                self._console.debug("Package %s..." % (partId))

                collapsePackage = partPackages[partId][collapsePos]
                self._console.indent()
                for packageId in partPackages[partId][collapsePos+1:]:
                    self._console.debug("Merge #%s into #%s" % (packageId, collapsePackage))
                    self._mergePackage(packageId, collapsePackage, partIncludes, partPackages, packageClasses)

                self._console.outdent()
                collapsePos += 1

            self._console.outdent()



        # Support for merging small packages
        # Hint1: Based on the token length which is a bit strange but a good
        # possibility to get the not really correct filesize in an ultrafast way
        # More complex code and classes generally also have more tokens in them
        # Hint2: The first common package before the selected package between two
        # or more parts is allowed to merge with. As the package which should be merged
        # may have requirements these must be solved. The easiest way to be sure regarding
        # this issue, is to look out for another common package. The package for which we
        # are looking must have requirements in all parts so these must be solved by all parts
        # so there must be another common package. Hardly to describe... hope this makes some sense
        if minPackageSize != None and minPackageSize != 0:
            smallPackages = []

            # Start at the end with the priority sorted list
            sortedPackageIds = self._sortPackageIdsByPriority(self._classesToPackageIds(packageClasses), packageBitCounts)
            sortedPackageIds.reverse()
            
            self._console.debug("")
            self._console.info("Optimizing package sizes...")
            self._console.indent()
            self._console.debug("Minimum package size: %sKB" % minPackageSize)
            
            # We need bytes (the user defines kbytes)
            minPackageSize = minPackageSize * 1024

            for packageId in sortedPackageIds:
                packageSize = 0
                self._console.indent()

                for classId in packageClasses[packageId]:
                    packageSize += self._compiler.getCompiledSize(classId, variants)

                if packageSize >= minPackageSize:
                    self._console.debug("Package #%s: %sKB" % (packageId, packageSize / 1024))
                    self._console.outdent()
                    continue
                    
                self._console.debug("Package #%s: %sKB" % (packageId, packageSize / 1024))
                collapsePackage = self._getPreviousCommonPackage(packageId, partPackages, packageBitCounts)

                self._console.indent()
                if collapsePackage != None:
                    self._console.debug("Merge package #%s into #%s" % (packageId, collapsePackage))
                    self._mergePackage(packageId, collapsePackage, partIncludes, partPackages, packageClasses)

                self._console.outdent()
                self._console.outdent()
            
            self._console.outdent()

            # User feedback
            self._printPartStats(packageClasses, partPackages)



        # Post process results
        # Translate bit-like IDs to easy numeric ones.
        # Apply human sorting from 0-...
        self._console.debug("")
        sortedPackageIds = self._sortPackageIdsByPriority(self._classesToPackageIds(packageClasses), packageBitCounts)

        resultInclude = []
        resultParts = {}
        for pkgPos, pkgId in enumerate(sortedPackageIds):
            self._console.debug("Translate package ID: %s => %s" % (pkgId, pkgPos))
            resultInclude.append(self._deputil.sortClasses(packageClasses[pkgId], variants))

            for partId in partPackages:
                if pkgId in partPackages[partId]:
                    if not resultParts.has_key(partId):
                        resultParts[partId] = []

                    resultParts[partId].append(pkgPos)

        self._console.debug("")
        

        # Return
        return resultInclude, resultParts



    def _sortPackageIdsByPriority(self, packageIds, packageBitCounts):
        def _cmpPackageIds(pkgId1, pkgId2):
            if packageBitCounts[pkgId2] > packageBitCounts[pkgId1]:
                return 1
            elif packageBitCounts[pkgId2] < packageBitCounts[pkgId1]:
                return -1

            return pkgId2 - pkgId1

        packageIds.sort(_cmpPackageIds)

        return packageIds



    def _getPreviousCommonPackage(self, searchId, partPackages, packageBitCounts):
        relevantParts = []
        relevantPackages = []

        for partId in partPackages:
            packages = partPackages[partId]
            if searchId in packages:
                relevantParts.append(partId)
                relevantPackages.extend(packages[:packages.index(searchId)])

        # Sorted by priority, but start from end
        self._sortPackageIdsByPriority(relevantPackages, packageBitCounts)
        relevantPackages.reverse()

        # Check if a package is available identical times to the number of parts
        for packageId in relevantPackages:
            if relevantPackages.count(packageId) == len(relevantParts):
                return packageId

        return None



    def _printPartStats(self, packageClasses, partPackages):
        packageIds = self._classesToPackageIds(packageClasses)

        self._console.debug("")
        self._console.debug("Packages Summary")
        self._console.indent()
        for packageId in packageIds:
            self._console.debug("Package #%s contains %s classes" % (packageId, len(packageClasses[packageId])))
        self._console.outdent()

        self._console.debug("")
        self._console.debug("Part Summary")
        self._console.indent()
        for partId in partPackages:
            self._console.debug("Part #%s uses these packages: %s" % (partId, self._intListToString(partPackages[partId])))
        self._console.outdent()



    def _classesToPackageIds(self, incoming):
        result = []

        for key in incoming:
            result.append(key)

        result.sort()
        result.reverse()

        return result



    def _mergePackage(self, replacePackage, collapsePackage, partIncludes, partPackages, packageClasses):
        # Replace other package content
        for partId in partIncludes:
            partContent = partPackages[partId]

            if replacePackage in partContent:
                # Store collapse package at the place of the old value
                partContent[partContent.index(replacePackage)] = collapsePackage

                # Remove duplicate (may be, but only one)
                if partContent.count(collapsePackage) > 1:
                    partContent.reverse()
                    partContent.remove(collapsePackage)
                    partContent.reverse()

        # Merging collapsed packages
        packageClasses[collapsePackage].extend(packageClasses[replacePackage])
        del packageClasses[replacePackage]



    def _intListToString(self, input):
        result = ""
        for entry in input:
            result += "#%s, " % entry

        return result[:-2]
