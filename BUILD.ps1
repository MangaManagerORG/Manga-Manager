##$repoName = "Manga-Manager"
##$ownerName = "MangaManagerOrg"
### Get the latest release
##$latestRelease = Invoke-RestMethod -Uri "https://api.github.com/repos/$ownerName/$repoName/releases/latest"
### Get the branch or tag name of the commit where the latest release is tied to
##$latestReleaseBranchOrTagName = $latestRelease.target_commitish
### Get the short hash of the commit where the latest release is tied to
##$latestReleaseCommitHash = git rev-parse --short $latestReleaseBranchOrTagName
### Get the short hash of the latest commit in the develop branch
##$latestDevelopHash = git rev-parse --short develop
##
##$content = Get-Content .\MangaManager\src\__version__.py
##if ($content -match '(?<=__version__ = ")[^:"]+') {
##    $newContent = $content -replace '__version__ = ".*"', "__version__ = `"$versionNumber:nightly--$latestReleaseCommitHash->$latestDevelopHash`""
##    $newContent | Set-Content .\MangaManager\src\__version__.py
##}
##Write-Output $newContent
#$repoName = "Manga-Manager"
#$ownerName = "MangaManagerOrg"
## Get the latest release
#$latestRelease = Invoke-RestMethod -Uri "https://api.github.com/repos/$ownerName/$repoName/releases/latest"
## Get the branch or tag name of the commit where the latest release is tied to
#$latestReleaseBranchOrTagName = $latestRelease.target_commitish
## Get the short hash of the commit where the latest release is tied to
#$latestReleaseCommitHash = git rev-parse --short $latestReleaseBranchOrTagName
## Get the short hash of the latest commit in the develop branch
#$latestDevelopHash = git rev-parse --short develop
#
#$content = Get-Content .\MangaManager\src\__version__.py
#$versionRegex = '(?<=__version__ = ")[^:"]+'
#if ($content -match $versionRegex) {
#    $versionNumber = $matches[0]
#    $newContent = $content -replace '__version__ = ".*"', "__version__ = `"$versionNumber:nightly--$latestReleaseCommitHash->$latestDevelopHash`""
#    $newContent | Set-Content .\MangaManager\src\__version__.py
#}
#Write-Output $newContent
$repoName = "Manga-Manager"
$ownerName = "MangaManagerOrg"
# Get the latest release
$latestRelease = Invoke-RestMethod -Uri "https://api.github.com/repos/$ownerName/$repoName/releases/latest"
# Get the branch or tag name of the commit where the latest release is tied to
$latestReleaseBranchOrTagName = $latestRelease.target_commitish
# Get the short hash of the commit where the latest release is tied to
$latestReleaseCommitHash = git rev-parse --short $latestReleaseBranchOrTagName
# Get the short hash of the latest commit in the develop branch
$latestDevelopHash = git rev-parse --short develop

$content = Get-Content .\MangaManager\src\__version__.py
$versionFile = ".\MangaManager\src\__version__.py"

# Read the current contents of the version file
$content = Get-Content $versionFile

# Update the commit hashes in the version file
$content | ForEach-Object {
    if ($_ -match "^__version__ = '.*:stable$'") {
        $_ -replace "(?<=[^-])-?[0-9a-f]{7,}?(?=-|->)", $latestReleaseCommitHash
    } elseif ($_ -match "^__version__ = '.*:nightly$'") {
        $_ -replace "(?<=[^-])-?[0-9a-f]{7,}?(?=-|->)", $latestDevelopHash
    } else {
        $_
    }
} | Set-Content $versionFile
Write-Output $content